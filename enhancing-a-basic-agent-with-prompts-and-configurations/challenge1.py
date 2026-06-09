"""
Challenge 1 Starter: Dynamic Context Injection

Use the `ContentContext` model and `build_dynamic_prompt()` helper below to
build three distinct agents — one per context — and run the same query
against each, observing how the system prompt shifts the output.

When you're ready to compare your work to the reference implementation,
see `solutions/challenge1_solution.py`.
"""

import os
from pydantic import BaseModel
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables.")


class ContentContext(BaseModel):
    """Model representing content generation context"""

    audience: str  # 'technical' or 'general'
    length: str  # 'short', 'medium', 'long'
    tone: str  # 'formal', 'casual'


def build_dynamic_prompt(ctx: ContentContext) -> str:
    """Build a system prompt based on context"""
    base = """You are a content strategist for TechWrite."""

    # Customize based on audience
    if ctx.audience == "technical":
        base += "\n\nAudience: Technical professionals. Use industry terminology and assume deep technical knowledge."
    else:
        base += "\n\nAudience: General business readers. Explain technical concepts clearly without jargon."

    # Customize based on length
    length_guidance = {
        "short": "Create concise outlines with 3 main sections.",
        "medium": "Create detailed outlines with 4-5 main sections.",
        "long": "Create comprehensive outlines with 6-7 main sections.",
    }
    base += f"\n\nLength: {length_guidance[ctx.length]}"

    # Customize based on tone
    if ctx.tone == "formal":
        base += "\n\nTone: Professional and formal. Avoid colloquialisms."
    else:
        base += "\n\nTone: Conversational and approachable. Use friendly language."

    return base


if __name__ == "__main__":
    contexts = [
        ContentContext(audience="technical", length="short", tone="formal"),
        ContentContext(audience="general", length="medium", tone="casual"),
        ContentContext(audience="technical", length="long", tone="casual"),
    ]

    query = "Create a blog outline about microservices architecture"

    for i, context in enumerate(contexts, start=1):
        agent = Agent(
            "openai:gpt-4o-mini",
            system_prompt=build_dynamic_prompt(context),
        )
        result = agent.run_sync(query)

        print(f"\n=== Context {i}: {context.model_dump()} ===")
        print(result.output)
