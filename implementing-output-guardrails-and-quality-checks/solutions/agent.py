"""
Guardrail-Protected Agent

Complete integration of input validation, output validation, and PII detection.

Features:
- Pre-processing input validation
- Post-processing output validation
- Automatic PII redaction
- Retry logic with correction prompts
- Comprehensive logging

Run: python agent.py
"""

import os
import asyncio
from typing import Dict, Optional, List
from pydantic_ai import Agent
from pydantic_ai.messages import ModelMessage
from dotenv import load_dotenv

from input_guards import InputGuardrails
from output_guards import OutputGuardrails
from pii_detector import PIIDetector

load_dotenv()


# Create financial services support agent
support_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    system_prompt="""You are a professional financial services support agent.

Guidelines:
- Provide accurate information about our services
- Be professional and courteous  
- Never discuss competitors or provide financial/legal/tax advice
- Do not express personal opinions
- Keep responses concise and helpful
- Never use inappropriate language
""",
)


async def handle_query_with_guardrails(query: str) -> Dict:
    """
    Process query with complete guardrail protection.

    Pipeline:
    1. Input validation
    2. Agent execution
    3. Output validation
    4. PII detection and redaction
    5. Return results with metadata

    Returns:
        {
            'success': bool,
            'response': str,
            'error': str (if failed),
            'guardrails_triggered': List[str],
            'pii_redacted': Dict[str, int]
        }
    """
    # YOUR CODE HERE
    # [SOLUTION]
    triggered = []

    # STEP 1: Input Validation
    input_result = InputGuardrails.validate_input(query)
    if not input_result.is_valid:
        triggered.append("input_validation")
        return {
            "success": False,
            "response": None,
            "error": input_result.error_message,
            "guardrails_triggered": triggered,
            "pii_redacted": {},
        }

    # STEPS 2-4: Agent execution + output validation + PII redaction.
    # Factored into a helper so retry can reuse it without re-running
    # input validation against framework-generated correction prompts.
    return await handle_query_skipping_input_validation(
        query, _triggered=triggered
    )
    # [/SOLUTION]


async def handle_query_skipping_input_validation(
    query: str, _triggered: Optional[List[str]] = None
) -> Dict:
    """Run agent + output validation + PII redaction, *without* input validation.

    Only call this for framework-generated text such as the correction
    prompts produced by ``handle_query_with_retry``. Skipping input
    validation here is the structural fix for the retry self-poisoning
    bug: re-running ``InputGuardrails.validate_input`` on a correction
    prompt is a category error — the correction prompt is not user
    input, and its boilerplate can either match a ``RESTRICTED_TOPICS``
    substring or grow long enough on nested retries to trip the length
    check.

    The ``_triggered`` parameter is internal — it lets
    ``handle_query_with_guardrails`` thread the running ``triggered``
    list through so callers see the full guardrail trail.
    """
    triggered: List[str] = list(_triggered) if _triggered else []

    # Run Agent
    try:
        result = await support_agent.run(query)
        response = result.output
    except Exception as e:
        return {
            "success": False,
            "response": None,
            "error": f"Agent error: {str(e)}",
            "guardrails_triggered": triggered,
            "pii_redacted": {},
        }

    # Output Validation
    output_result = OutputGuardrails.validate_output(response)

    if not output_result.is_valid:
        triggered.append("output_validation")
        return {
            "success": False,
            "response": response,
            "error": f"Output validation failed: {'; '.join(output_result.errors)}",
            "guardrails_triggered": triggered,
            "pii_redacted": {},
            "validation_details": {
                "errors": output_result.errors,
                "warnings": output_result.warnings,
                "policy_violations": output_result.policy_violations,
            },
        }

    if output_result.policy_violations:
        triggered.append("policy_compliance")
        return {
            "success": False,
            "response": response,
            "error": f"Policy violations: {'; '.join(output_result.policy_violations)}",
            "guardrails_triggered": triggered,
            "pii_redacted": {},
        }

    # PII Detection and Redaction
    redacted_response, pii_found = PIIDetector.redact_pii(response)
    if pii_found:
        triggered.append("pii_redaction")
        response = redacted_response

    # SUCCESS
    return {
        "success": True,
        "response": response,
        "error": None,
        "guardrails_triggered": triggered,
        "pii_redacted": pii_found,
        "quality_score": output_result.quality_score,
    }


async def handle_query_with_retry(
    query: str,
    max_retries: int = 2,
    message_history: Optional[List[ModelMessage]] = None,
) -> Dict:
    """
    Handle query with automatic retry on guardrail failures.

    If output validation or policy compliance fails, retry with a
    correction prompt. Input validation failures are not retried — the
    user's original query was rejected on its own merits.

    The correction prompt is treated as framework-generated text:
    ``handle_query_skipping_input_validation`` runs the post-input-
    validation flow on it directly. The original user question is
    anchored in ``original_query`` so retries do not nest correction
    prompts inside each other (which previously caused query length to
    grow geometrically and trip the input length check).

    Args:
        query: User's query
        max_retries: Maximum retry attempts
        message_history: Conversation history

    Returns:
        Result dictionary
    """
    # Anchored — never reassign across retries. The earlier bug was that
    # ``query`` was rebound to the correction prompt each iteration, so
    # the second retry nested the first correction prompt inside itself.
    original_query = query

    # First attempt runs the full guardrail flow on the user's query.
    result = await handle_query_with_guardrails(query)

    for attempt in range(max_retries):
        if result["success"]:
            result["attempts"] = attempt + 1
            return result

        # Don't retry input validation failures — the user's actual
        # query was rejected, not a framework-generated correction.
        if "input_validation" in result["guardrails_triggered"]:
            result["attempts"] = attempt + 1
            return result

        # Only retry output validation or policy failures.
        if not any(
            g in result["guardrails_triggered"]
            for g in ("output_validation", "policy_compliance")
        ):
            result["attempts"] = attempt + 1
            return result

        correction_prompt = f"""
The previous response violated guidelines: {result['error']}

Please provide a response that:
- Is professional and helpful
- Stays within regulated-advice compliance and the company's content policy
- Avoids inappropriate language
- Does not express personal opinions
- Is factual and accurate

Original user question: {original_query}
"""
        # Skip input validation — correction_prompt is framework-generated,
        # so applying InputGuardrails to it is a category error.
        result = await handle_query_skipping_input_validation(correction_prompt)

    result["attempts"] = max_retries + 1
    return result


async def interactive_session():
    """Run interactive guardrail-protected session."""
    print("=" * 60)
    print("  Financial Services Support Agent")
    print("  (With Comprehensive Guardrails)")
    print("=" * 60)
    print("\nCommands:")
    print("  quit - Exit")
    print("  stats - Show guardrail statistics")
    print()

    # `guardrails` uses defaultdict(int) so Challenge 2 can introduce new
    # guardrail identifiers (e.g. "low_confidence") without students
    # having to remember to pre-register every key. The pre-fix dict
    # raised KeyError as soon as a new guardrail name appeared.
    from collections import defaultdict
    stats = {
        "total_queries": 0,
        "successful": 0,
        "blocked": 0,
        "guardrails": defaultdict(int, {
            "input_validation": 0,
            "output_validation": 0,
            "policy_compliance": 0,
            "pii_redaction": 0,
        }),
    }

    while True:
        query = input("\n\033[1;34mYou: \033[0m").strip()

        if query.lower() == "quit":
            print("\nThank you for using our support service!")
            break

        if query.lower() == "stats":
            print("\n" + "=" * 60)
            print("  Guardrail Statistics")
            print("=" * 60)
            print(f"Total queries: {stats['total_queries']}")
            print(f"Successful: {stats['successful']}")
            print(f"Blocked: {stats['blocked']}")
            print(f"\nGuardrails triggered:")
            for guard, count in stats["guardrails"].items():
                print(f"  {guard}: {count}")
            print("=" * 60)
            continue

        if not query:
            continue

        stats["total_queries"] += 1

        # Process with guardrails and retry
        print("\n\033[1;32mAssistant: \033[0m", end="", flush=True)

        result = await handle_query_with_retry(query, max_retries=2)

        if result["success"]:
            stats["successful"] += 1
            print(result["response"])

            # Show triggered guardrails
            if result["guardrails_triggered"]:
                for guard in result["guardrails_triggered"]:
                    stats["guardrails"][guard] += 1

                print(
                    f"\n\033[1;33m[Note: {', '.join(result['guardrails_triggered'])} applied]\033[0m"
                )

            if result.get("pii_redacted"):
                print(f"\033[1;33m[PII redacted: {result['pii_redacted']}]\033[0m")

        else:
            stats["blocked"] += 1
            print(f"\033[1;31m[Error: {result['error']}]\033[0m")

            for guard in result["guardrails_triggered"]:
                stats["guardrails"][guard] += 1


async def demo():
    """Demonstrate guardrails."""
    print("=" * 60)
    print("  Guardrail Demonstration")
    print("=" * 60)

    test_queries = [
        "What are your business hours?",
        "Tell me about competitor products",
        # Phrased to deterministically match an InputGuardrails
        # RESTRICTED_TOPICS substring ("investment advice"). The
        # original "Should I invest in Bitcoin?" never tripped any guard
        # because none of its words appeared in the substring list, so
        # the headline validation passed silently with the wrong outcome.
        "I need investment advice on which stocks to pick this quarter.",
        "How do I reset my password?",
        "My SSN is 123-45-6789, can you help?",
    ]

    for query in test_queries:
        print(f"\n{'─'*60}")
        print(f"Query: {query}")
        print(f"{'─'*60}")

        result = await handle_query_with_retry(query)

        print(f"Success: {result['success']}")
        if result["success"]:
            print(f"Response: {result['response']}")
            if result.get("attempts", 1) > 1:
                print(f"(Required {result['attempts']} attempts)")
        else:
            print(f"Error: {result['error']}")

        if result["guardrails_triggered"]:
            print(f"Guardrails: {', '.join(result['guardrails_triggered'])}")


async def main():
    """Main entry point."""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        await demo()
    else:
        await interactive_session()


if __name__ == "__main__":
    asyncio.run(main())
