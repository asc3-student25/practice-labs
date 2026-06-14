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
from judge import JudgeAgent, JudgeScore

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
    judge_helpfulness: Optional[int]
    judge_correctness: Optional[int]
    judge_completeness: Optional[int]
    judge_rationale: str
    judge_passed: bool
    judge_error: Optional[str]
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

    @staticmethod
    def _judge_passed(score: Optional[JudgeScore]) -> bool:
        """Judge is happy only when all qualitative dimensions are strong."""
        if not score:
            return False
        return score.helpfulness >= 4 and score.correctness >= 4 and score.completeness >= 4

    async def evaluate(
        self, model: str = "gpt-5.4-mini", judge_model: Optional[str] = None
    ) -> List[TestResult]:
        """Run evaluation suite."""
        agent = SupportAgent(model)
        judge = JudgeAgent(judge_model or model)
        results = []

        for case in self.test_cases:
            result = await self._evaluate_case(agent, judge, case)
            results.append(result)

        return results

    async def _evaluate_case(
        self, agent: SupportAgent, judge: JudgeAgent, case: TestCase
    ) -> TestResult:
        """Evaluate single test case.

        Wraps the agent call in try/except so a per-case failure (rate
        limit, transient network error, unexpected response shape) is
        captured as a failed TestResult with zeroed metrics rather than
        propagating out and crashing the rest of the evaluation suite.
        """
        start_time = datetime.now()
        response = ""
        metadata = {"tokens": 0}
        try:
            response, metadata = await agent.handle_query(case.question)
        except Exception as e:
            response = f"Error: {e}"

        latency_ms = (datetime.now() - start_time).total_seconds() * 1000

        response_lower = response.lower()
        keywords_found = [
            keyword for keyword in case.expected_keywords if keyword.lower() in response_lower
        ]
        keywords_missing = [
            keyword for keyword in case.expected_keywords if keyword.lower() not in response_lower
        ]
        passed = len(keywords_missing) == 0

        tokens_used = int(metadata.get("tokens", 0))
        rate_per_1k = self.COST_PER_1K_TOKENS.get(agent.model, 0.0001)
        cost_usd = (tokens_used / 1000) * rate_per_1k

        judge_score: Optional[JudgeScore] = None
        judge_error: Optional[str] = None
        try:
            judge_score = await judge.score(
                question=case.question,
                response=response,
                expected_response=case.expected_response,
                expected_keywords=case.expected_keywords,
            )
        except Exception as e:
            judge_error = str(e)

        return TestResult(
            test_id=case.id,
            question=case.question,
            response=response,
            passed=passed,
            keywords_found=keywords_found,
            keywords_missing=keywords_missing,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            cost_usd=cost_usd,
            judge_helpfulness=judge_score.helpfulness if judge_score else None,
            judge_correctness=judge_score.correctness if judge_score else None,
            judge_completeness=judge_score.completeness if judge_score else None,
            judge_rationale=judge_score.rationale if judge_score else "Judge scoring unavailable",
            judge_passed=self._judge_passed(judge_score),
            judge_error=judge_error,
            timestamp=datetime.now().isoformat(),
        )

    async def compare_models(
        self, models: List[str], judge_model: Optional[str] = None
    ) -> Dict[str, Dict]:
        """Compare performance across models."""
        comparison = {}

        for model in models:
            print(f"\nEvaluating {model}...")
            results = await self.evaluate(model, judge_model=judge_model)
            judged = [
                r
                for r in results
                if r.judge_helpfulness is not None
                and r.judge_correctness is not None
                and r.judge_completeness is not None
            ]
            avg_helpfulness = (
                sum(r.judge_helpfulness for r in judged) / len(judged) if judged else 0.0
            )
            avg_correctness = (
                sum(r.judge_correctness for r in judged) / len(judged) if judged else 0.0
            )
            avg_completeness = (
                sum(r.judge_completeness for r in judged) / len(judged) if judged else 0.0
            )

            comparison[model] = {
                "pass_rate": sum(1 for r in results if r.passed) / len(results),
                "judge_pass_rate": sum(1 for r in results if r.judge_passed) / len(results),
                "avg_helpfulness": avg_helpfulness,
                "avg_correctness": avg_correctness,
                "avg_completeness": avg_completeness,
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
        judge_passed = sum(1 for r in results if r.judge_passed)
        total = len(results)
        total_cost = sum(r.cost_usd for r in results)
        avg_latency = sum(r.latency_ms for r in results) / total
        total_tokens = sum(r.tokens_used for r in results)
        judged = [
            r
            for r in results
            if r.judge_helpfulness is not None
            and r.judge_correctness is not None
            and r.judge_completeness is not None
        ]
        avg_helpfulness = (
            sum(r.judge_helpfulness for r in judged) / len(judged) if judged else 0.0
        )
        avg_correctness = (
            sum(r.judge_correctness for r in judged) / len(judged) if judged else 0.0
        )
        avg_completeness = (
            sum(r.judge_completeness for r in judged) / len(judged) if judged else 0.0
        )

        keyword_pass_judge_unhappy = [r for r in results if r.passed and not r.judge_passed]
        keyword_fail_judge_happy = [r for r in results if (not r.passed) and r.judge_passed]

        report = []
        report.append("=" * 60)
        report.append("  AGENT EVALUATION REPORT")
        report.append("=" * 60)
        report.append(f"\nTimestamp: {datetime.now().isoformat()}")
        report.append(f"\nSUMMARY:")
        report.append(f"  Keyword Pass Rate: {passed}/{total} ({100*passed/total:.1f}%)")
        report.append(
            f"  Judge Pass Rate: {judge_passed}/{total} ({100*judge_passed/total:.1f}%)"
        )
        report.append(
            f"  Avg Judge Scores (H/C/C): {avg_helpfulness:.2f}/{avg_correctness:.2f}/{avg_completeness:.2f}"
        )
        report.append(f"  Total Cost: ${total_cost:.4f}")
        report.append(f"  Total Tokens: {total_tokens:,}")
        report.append(f"  Avg Latency: {avg_latency:.0f}ms")
        report.append(
            f"  Mismatch Count (keyword pass, judge unhappy): {len(keyword_pass_judge_unhappy)}"
        )
        report.append(
            f"  Mismatch Count (keyword fail, judge happy): {len(keyword_fail_judge_happy)}"
        )

        if keyword_pass_judge_unhappy:
            report.append("\nMISMATCHES: KEYWORD PASS BUT JUDGE UNHAPPY")
            for r in keyword_pass_judge_unhappy:
                report.append(
                    f"  - {r.test_id}: H/C/C={r.judge_helpfulness}/{r.judge_correctness}/{r.judge_completeness} | {r.judge_rationale}"
                )

        if keyword_fail_judge_happy:
            report.append("\nMISMATCHES: KEYWORD FAIL BUT JUDGE HAPPY")
            for r in keyword_fail_judge_happy:
                report.append(
                    f"  - {r.test_id}: missing={', '.join(r.keywords_missing)} | {r.judge_rationale}"
                )

        report.append(f"\nDETAILED RESULTS:")

        for r in results:
            keyword_status = "PASS" if r.passed else "FAIL"
            judge_status = "PASS" if r.judge_passed else "FAIL"
            mismatch = " MISMATCH" if r.passed != r.judge_passed else ""
            report.append(f"\nKW:{keyword_status} | JUDGE:{judge_status}{mismatch} | {r.test_id}")
            report.append(f"  Question: {r.question}")
            report.append(f"  Response: {r.response[:100]}...")
            report.append(
                f"  Tokens: {r.tokens_used} | Cost: ${r.cost_usd:.5f} | Latency: {r.latency_ms:.0f}ms"
            )
            report.append(
                "  Judge Scores (H/C/C): "
                f"{r.judge_helpfulness}/{r.judge_correctness}/{r.judge_completeness}"
            )
            report.append(f"  Judge Rationale: {r.judge_rationale}")
            if r.judge_error:
                report.append(f"  Judge Error: {r.judge_error}")

            if not r.passed:
                report.append(f"  Missing keywords: {', '.join(r.keywords_missing)}")

        report.append("\n" + "=" * 60)

        return "\n".join(report)


# Cost tracker
class CostTracker:
    """Track agent usage costs."""

    def __init__(
        self,
        log_file: str = "cost_log.json",
        daily_budget_threshold: Optional[float] = None,
        per_user_budget_threshold: Optional[float] = None,
    ):
        self.log_file = log_file
        self.daily_budget_threshold = daily_budget_threshold
        self.per_user_budget_threshold = per_user_budget_threshold
        # Hydrate from disk so `self.costs` reflects the full history
        # rather than just the current process's writes. Without this,
        # `get_total_cost()` returns only the current session's spend
        # while the JSONL file accumulates unbounded — a silent drift
        # that contradicts the lab's cost-accounting teaching.
        self.costs = self._load_existing()

    def set_budget_thresholds(
        self,
        daily_budget_threshold: Optional[float] = None,
        per_user_budget_threshold: Optional[float] = None,
    ):
        """Set or update budget thresholds."""
        self.daily_budget_threshold = daily_budget_threshold
        self.per_user_budget_threshold = per_user_budget_threshold

    @staticmethod
    def _budget_state(spend: float, threshold: Optional[float]) -> str:
        """Return ok/warning/over_budget based on spend vs threshold."""
        if threshold is None or threshold <= 0:
            return "ok"
        ratio = spend / threshold
        if ratio >= 1.0:
            return "over_budget"
        if ratio >= 0.8:
            return "warning"
        return "ok"

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
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "tokens": tokens,
            "cost_usd": cost,
            "metadata": metadata or {},
        }

        self.costs.append(entry)

        with open(self.log_file, "a") as f:
            f.write(json.dumps(entry) + "\n")

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

    def get_daily_budget_alert(self) -> str:
        """Check today's spend against configured daily threshold."""
        today = datetime.now().date().isoformat()
        today_spend = self.get_daily_costs().get(today, 0.0)
        return self._budget_state(today_spend, self.daily_budget_threshold)

    def get_user_budget_alert(self, user_id: str) -> str:
        """Check user's total spend against configured per-user threshold."""
        user_spend = self.get_total_cost(user_id)
        return self._budget_state(user_spend, self.per_user_budget_threshold)

    def can_accept_request(self, user_id: str) -> bool:
        """Refuse requests when either budget is already over."""
        return (
            self.get_daily_budget_alert() != "over_budget"
            and self.get_user_budget_alert(user_id) != "over_budget"
        )


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
        TestCase(
            id="order-status",
            question="How can I check my order status?",
            expected_keywords=["order number", "tracking", "email"],
            category="order-status",
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
    predicted_highest_pass = "gpt-4o"
    predicted_cheapest = "gpt-5.4-mini"
    print("Predictions before run:")
    print(f"  Highest pass rate: {predicted_highest_pass}")
    print(f"  Cheapest/request: {predicted_cheapest}")

    comparison = await evaluator.compare_models(["gpt-5.4-mini", "gpt-4o", "gpt-4-turbo"])

    print("\n" + "=" * 60)
    print("  MODEL COMPARISON")
    print("=" * 60)

    for model, metrics in comparison.items():
        print(f"\n{model.upper()}:")
        print(f"  Keyword Pass Rate: {metrics['pass_rate']*100:.1f}%")
        print(f"  Judge Pass Rate: {metrics['judge_pass_rate']*100:.1f}%")
        print(
            "  Avg Judge Scores (H/C/C): "
            f"{metrics['avg_helpfulness']:.2f}/{metrics['avg_correctness']:.2f}/{metrics['avg_completeness']:.2f}"
        )
        print(f"  Avg Cost: ${metrics['avg_cost_usd']:.5f}/request")
        print(f"  Total Cost: ${metrics['total_cost_usd']:.4f}")
        print(f"  Avg Latency: {metrics['avg_latency_ms']:.0f}ms")
        print(f"  Total Tokens: {metrics['total_tokens']:,}")

    actual_highest_pass = max(comparison.items(), key=lambda x: x[1]["pass_rate"])[0]
    actual_cheapest = min(comparison.items(), key=lambda x: x[1]["avg_cost_usd"])[0]

    print("\nPrediction vs report output:")
    print(
        f"  Highest pass rate -> predicted: {predicted_highest_pass}, actual: {actual_highest_pass}"
    )
    print(
        f"  Cheapest/request -> predicted: {predicted_cheapest}, actual: {actual_cheapest}"
    )

    # Cost tracking demo
    print("\n3. Cost tracking demo...")
    tracker = CostTracker(daily_budget_threshold=0.00001, per_user_budget_threshold=0.00001)

    for i, result in enumerate(results):
        tracker.log_request(
            user_id=f"user_{i % 3}",  # Simulate 3 users
            tokens=result.tokens_used,
            cost=result.cost_usd,
            metadata={"test_id": result.test_id},
        )

    print(f"\nTotal tracked cost: ${tracker.get_total_cost():.4f}")
    print(f"User 0 cost: ${tracker.get_total_cost('user_0'):.4f}")

    print("\nBudget alerts (tight thresholds):")
    print(f"  Daily alert: {tracker.get_daily_budget_alert()}")
    print(f"  user_0 alert: {tracker.get_user_budget_alert('user_0')}")

    tracker.set_budget_thresholds(daily_budget_threshold=999.0, per_user_budget_threshold=999.0)
    print("\nBudget alerts (raised thresholds):")
    print(f"  Daily alert: {tracker.get_daily_budget_alert()}")
    print(f"  user_0 alert: {tracker.get_user_budget_alert('user_0')}")
    print(f"  Can accept user_0 request: {tracker.can_accept_request('user_0')}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
