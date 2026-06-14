"""
Agent Evaluation and Cost Management

Comprehensive framework for measuring agent quality and tracking costs.

Core features:
- Test suite execution with golden datasets
- Quality metrics (accuracy, consistency, relevance)
- Cost tracking per request/user/day
- Model comparison across tiers
- Performance dashboards

Run: python main.py
"""

import os
import json
import asyncio
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from pydantic_ai import Agent
from dotenv import load_dotenv

load_dotenv()


# Test case model
@dataclass
class TestCase:
    id: str
    question: str
    expected_keywords: List[str]
    category: str
    expected_response: Optional[str] = None


# Test result model
@dataclass
class TestResult:
    test_id: str
    question: str
    response: str
    passed: bool
    keywords_found: List[str]
    keywords_missing: List[str]
    tokens_used: int
    latency_ms: float
    cost_usd: float
    timestamp: str


# Agent under test
class SupportAgent:
    def __init__(self, model: str | None = None):
        # Resolve the model: explicit arg > AI_MODEL env var > openai default.
        # Accept either a bare model name ("gpt-5.4-mini") or a fully
        # provider-prefixed identifier ("openai:gpt-5.4-mini",
        # "anthropic:claude-sonnet-4-5"). Bare names get the openai prefix
        # for backwards compatibility with the COST_PER_1K_TOKENS lookup.
        resolved = model or os.getenv("AI_MODEL", "openai:gpt-5.4-mini")
        if ":" not in resolved:
            resolved = f"openai:{resolved}"
        self.agent = Agent(
            resolved,
            system_prompt="""You are a friendly customer support agent.
            Answer questions accurately and concisely.
            Provide helpful information about our policies and services.""",
        )
        # Strip the provider prefix for the cost-table lookup so existing
        # COST_PER_1K_TOKENS keys ("gpt-5.4-mini", etc.) still resolve.
        self.model = resolved.split(":", 1)[1] if ":" in resolved else resolved

    async def handle_query(self, question: str) -> tuple[str, dict]:
        """Handle query and return (response, metadata)."""
        result = await self.agent.run(question)

        metadata = {
            "tokens": result.usage().total_tokens if result.usage() else 0,
            "model": self.model,
        }

        return result.output, metadata


# Evaluator
class AgentEvaluator:
    """Evaluate agent performance."""

    # Cost per 1K tokens (example rates - adjust for actual provider)
    COST_PER_1K_TOKENS = {
        "gpt-5.4-mini": 0.00015,
        "gpt-4o": 0.0050,
        "gpt-4-turbo": 0.0030,
    }

    def __init__(self, test_cases: List[TestCase]):
        self.test_cases = test_cases

    async def evaluate(self, model: str = "gpt-5.4-mini") -> List[TestResult]:
        """Run evaluation suite."""
        agent = SupportAgent(model)
        results = []

        for case in self.test_cases:
            result = await self._evaluate_case(agent, case)
            results.append(result)

        return results

    async def _evaluate_case(self, agent: SupportAgent, case: TestCase) -> TestResult:
        """Evaluate single test case.

        Wraps the agent call in try/except so a per-case failure (rate
        limit, transient network error, unexpected response shape) is
        captured as a failed TestResult with zeroed metrics rather than
        propagating out and crashing the rest of the evaluation suite.
        """
        # YOUR CODE HERE
        # [SOLUTION]
        start = datetime.now()

        try:
            # Run agent
            response, metadata = await agent.handle_query(case.question)

            # Calculate latency
            latency_ms = (datetime.now() - start).total_seconds() * 1000

            # Check keywords
            found = []
            missing = []
            for keyword in case.expected_keywords:
                if keyword.lower() in response.lower():
                    found.append(keyword)
                else:
                    missing.append(keyword)

            passed = len(missing) == 0

            # Calculate cost
            tokens = metadata["tokens"]
            cost_per_1k = self.COST_PER_1K_TOKENS.get(agent.model, 0.0001)
            cost_usd = (tokens / 1000) * cost_per_1k

            return TestResult(
                test_id=case.id,
                question=case.question,
                response=response,
                passed=passed,
                keywords_found=found,
                keywords_missing=missing,
                tokens_used=tokens,
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                timestamp=datetime.now().isoformat(),
            )
        except Exception as exc:
            # Capture the failure as a failed TestResult so the suite
            # continues. The exception class and message are recorded
            # in the response field for post-run debugging.
            latency_ms = (datetime.now() - start).total_seconds() * 1000
            return TestResult(
                test_id=case.id,
                question=case.question,
                response=f"[{type(exc).__name__}] {exc}",
                passed=False,
                keywords_found=[],
                keywords_missing=list(case.expected_keywords),
                tokens_used=0,
                latency_ms=latency_ms,
                cost_usd=0.0,
                timestamp=datetime.now().isoformat(),
            )
        # [/SOLUTION]

    async def compare_models(self, models: List[str]) -> Dict[str, Dict]:
        """Compare performance across models."""
        comparison = {}

        for model in models:
            print(f"\nEvaluating {model}...")
            results = await self.evaluate(model)

            comparison[model] = {
                "pass_rate": sum(1 for r in results if r.passed) / len(results),
                "avg_cost_usd": sum(r.cost_usd for r in results) / len(results),
                "total_cost_usd": sum(r.cost_usd for r in results),
                "avg_latency_ms": sum(r.latency_ms for r in results) / len(results),
                "total_tokens": sum(r.tokens_used for r in results),
                "passed_tests": sum(1 for r in results if r.passed),
                "total_tests": len(results),
            }

        return comparison

    def generate_report(self, results: List[TestResult]) -> str:
        """Generate formatted evaluation report."""
        passed = sum(1 for r in results if r.passed)
        total = len(results)
        total_cost = sum(r.cost_usd for r in results)
        avg_latency = sum(r.latency_ms for r in results) / total
        total_tokens = sum(r.tokens_used for r in results)

        report = []
        report.append("=" * 60)
        report.append("  AGENT EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"\nTimestamp: {datetime.now().isoformat()}")
        report.append(f"\nSUMMARY:")
        report.append(f"  Pass Rate: {passed}/{total} ({100*passed/total:.1f}%)")
        report.append(f"  Total Cost: ${total_cost:.4f}")
        report.append(f"  Total Tokens: {total_tokens:,}")
        report.append(f"  Avg Latency: {avg_latency:.0f}ms")
        report.append(f"\nDETAILED RESULTS:")

        for r in results:
            status = "PASS" if r.passed else "FAIL"
            report.append(f"\n{status} | {r.test_id}")
            report.append(f"  Question: {r.question}")
            report.append(f"  Response: {r.response[:100]}...")
            report.append(
                f"  Tokens: {r.tokens_used} | Cost: ${r.cost_usd:.5f} | Latency: {r.latency_ms:.0f}ms"
            )

            if not r.passed:
                report.append(f"  Missing keywords: {', '.join(r.keywords_missing)}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


# Cost tracker
class CostTracker:
    """Track agent usage costs."""

    def __init__(self, log_file: str = "cost_log.json"):
        self.log_file = log_file
        # Hydrate from disk so `self.costs` reflects the full history
        # rather than just the current process's writes. Without this,
        # `get_total_cost()` returns only the current session's spend
        # while the JSONL file accumulates unbounded — a silent drift
        # that contradicts the lab's cost-accounting teaching.
        self.costs = self._load_existing()

    def _load_existing(self) -> list:
        """Read prior cost entries from log_file (one JSON object per line).

        Returns an empty list if the file doesn't exist yet, or skips any
        malformed lines so a partial write from a crashed prior run can't
        corrupt this session's totals.
        """
        path = os.fspath(self.log_file)
        if not os.path.exists(path):
            return []
        entries = []
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    # Skip malformed lines; don't crash on partial writes.
                    continue
        return entries

    def log_request(
        self, user_id: str, tokens: int, cost: float, metadata: dict = None
    ):
        """Log a request's cost."""
        # YOUR CODE HERE
        # [SOLUTION]
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "tokens": tokens,
            "cost_usd": cost,
            "metadata": metadata or {},
        }

        self.costs.append(entry)

        # Append to log file
        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")
        # [/SOLUTION]

    def get_total_cost(self, user_id: Optional[str] = None) -> float:
        """Get total cost, optionally filtered by user."""
        if user_id:
            return sum(c["cost_usd"] for c in self.costs if c["user_id"] == user_id)
        return sum(c["cost_usd"] for c in self.costs)

    def get_daily_costs(self) -> Dict[str, float]:
        """Get costs grouped by day."""
        daily = {}

        for cost in self.costs:
            date = cost["timestamp"][:10]  # YYYY-MM-DD
            daily[date] = daily.get(date, 0) + cost["cost_usd"]

        return daily


# Main demonstrations
async def main():
    # Sample test cases
    test_cases = [
        TestCase(
            id="return-policy",
            question="What is your return policy?",
            expected_keywords=["30 days", "receipt", "refund"],
            category="policy",
        ),
        TestCase(
            id="shipping-time",
            question="How long does shipping take?",
            expected_keywords=["3-5 business days", "tracking"],
            category="logistics",
        ),
        TestCase(
            id="payment-methods",
            question="What payment methods do you accept?",
            expected_keywords=["credit card", "PayPal"],
            category="payment",
        ),
    ]

    evaluator = AgentEvaluator(test_cases)

    print("=" * 60)
    print("  AGENT EVALUATION & COST MANAGEMENT")
    print("=" * 60)

    # Run evaluation
    print("\n1. Running evaluation suite...")
    results = await evaluator.evaluate(model="gpt-5.4-mini")

    # Generate report
    report = evaluator.generate_report(results)
    print(report)

    # Save report
    with open("evaluation_report.txt", "w") as f:
        f.write(report)
    print("\nReport saved to evaluation_report.txt")

    # Compare models
    print("\n2. Comparing model tiers...")
    comparison = await evaluator.compare_models(["gpt-5.4-mini", "gpt-4o"])

    print("\n" + "=" * 60)
    print("  MODEL COMPARISON")
    print("=" * 60)

    for model, metrics in comparison.items():
        print(f"\n{model.upper()}:")
        print(f"  Pass Rate: {metrics['pass_rate']*100:.1f}%")
        print(f"  Avg Cost: ${metrics['avg_cost_usd']:.5f}/request")
        print(f"  Total Cost: ${metrics['total_cost_usd']:.4f}")
        print(f"  Avg Latency: {metrics['avg_latency_ms']:.0f}ms")
        print(f"  Total Tokens: {metrics['total_tokens']:,}")

    # Cost tracking demo
    print("\n3. Cost tracking demo...")
    tracker = CostTracker()

    for i, result in enumerate(results):
        tracker.log_request(
            user_id=f"user_{i % 3}",  # Simulate 3 users
            tokens=result.tokens_used,
            cost=result.cost_usd,
            metadata={"test_id": result.test_id},
        )

    print(f"\nTotal tracked cost: ${tracker.get_total_cost():.4f}")
    print(f"User 0 cost: ${tracker.get_total_cost('user_0'):.4f}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
