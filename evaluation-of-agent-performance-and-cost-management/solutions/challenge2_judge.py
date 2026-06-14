"""
Lab Solution: Challenge 2 — LLM-as-Judge Evaluation

Supplements the keyword-based pass/fail signal with a qualitative score
from a judge agent. Keyword matching is a weak proxy for quality —
a response can hit every expected keyword and still be unhelpful, or
omit a keyword while being correct. The judge gives the report a second
dimension that catches both failure modes.

Run: python challenge2_judge.py
"""

import asyncio
import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent

from main import AgentEvaluator, SupportAgent, TestCase, TestResult

load_dotenv()


# Schema the judge returns. Keeping the score range explicit (0.0-1.0)
# and the rationale concise makes aggregating across cases straightforward.
class JudgeScore(BaseModel):
    """Qualitative scores produced by the judge agent."""

    helpfulness: float = Field(
        ge=0.0, le=1.0, description="How directly the response addresses the question"
    )
    correctness: float = Field(
        ge=0.0, le=1.0, description="Factual accuracy of the response"
    )
    completeness: float = Field(
        ge=0.0,
        le=1.0,
        description="Whether the response covers all expected points",
    )
    rationale: str = Field(
        description="One- to two-sentence explanation supporting the scores"
    )


# Build a separate judge agent. Using a different system prompt is what
# makes this an LLM-as-judge pattern rather than just a second call to
# the support agent — the judge is told to evaluate, not to answer.
judge_agent = Agent(
    os.getenv("AI_MODEL", "openai:gpt-5.4-mini"),
    output_type=JudgeScore,
    system_prompt=(
        "You are a strict but fair judge of customer support quality. "
        "Score each response on three axes (helpfulness, correctness, "
        "completeness) on a 0.0-1.0 scale, where 1.0 means 'no improvement "
        "needed' and 0.0 means 'response is wrong or off-topic'. Provide "
        "a one- or two-sentence rationale that names a specific strength "
        "or weakness. Be consistent across cases."
    ),
)


@dataclass
class JudgedResult:
    """Pairs a baseline TestResult with a judge score for the same case."""

    baseline: TestResult
    judge: JudgeScore


async def judge_case(case: TestCase, result: TestResult) -> JudgeScore:
    """Run a single response through the judge agent."""
    expected = (
        ", ".join(case.expected_keywords)
        if case.expected_keywords
        else "(none specified)"
    )
    prompt = (
        f"Question: {case.question}\n\n"
        f"Agent response:\n{result.response}\n\n"
        f"Expected keywords (for context only): {expected}\n\n"
        "Score this response on helpfulness, correctness, and completeness, "
        "and explain briefly."
    )
    judge_result = await judge_agent.run(prompt)
    return judge_result.output


async def evaluate_with_judge(
    cases: List[TestCase], model: str = "gpt-5.4-mini"
) -> List[JudgedResult]:
    """Run the baseline keyword evaluation, then layer the judge on top."""
    evaluator = AgentEvaluator(cases)
    baseline_results = await evaluator.evaluate(model=model)

    # Sequence the judge calls per-case rather than parallelizing — the
    # judge is the second-pass signal, and at this scale the latency cost
    # of `gather` setup outweighs the wall-clock savings.
    judged: List[JudgedResult] = []
    for case, baseline in zip(cases, baseline_results):
        score = await judge_case(case, baseline)
        judged.append(JudgedResult(baseline=baseline, judge=score))
    return judged


def print_combined_summary(judged: List[JudgedResult]) -> None:
    """Side-by-side keyword pass-rate and judge-score summary."""
    total = len(judged)
    keyword_passes = sum(1 for j in judged if j.baseline.passed)
    avg_help = sum(j.judge.helpfulness for j in judged) / total
    avg_correct = sum(j.judge.correctness for j in judged) / total
    avg_complete = sum(j.judge.completeness for j in judged) / total

    print("\n" + "=" * 60)
    print("  COMBINED KEYWORD + JUDGE SUMMARY")
    print("=" * 60)
    print(f"\nKeyword pass rate: {keyword_passes}/{total} "
          f"({100 * keyword_passes / total:.0f}%)")
    print(f"Avg judge helpfulness:  {avg_help:.2f}")
    print(f"Avg judge correctness:  {avg_correct:.2f}")
    print(f"Avg judge completeness: {avg_complete:.2f}")

    # The most interesting cases for instructors and students to discuss
    # are the disagreements — high keyword score / low judge score (or
    # vice versa). Surface those in their own block.
    print("\n--- Cases where keyword and judge disagree ---")
    disagreements = []
    for j in judged:
        keyword_signal = 1.0 if j.baseline.passed else 0.0
        # "Disagreement" = judge average diverges by more than 0.4 from
        # the keyword binary signal.
        judge_avg = (
            j.judge.helpfulness + j.judge.correctness + j.judge.completeness
        ) / 3
        if abs(judge_avg - keyword_signal) > 0.4:
            disagreements.append((j, judge_avg))
    if not disagreements:
        print("  (No major disagreements between signals.)")
    else:
        for j, judge_avg in disagreements:
            kw = "PASS" if j.baseline.passed else "FAIL"
            print(
                f"  [{j.baseline.test_id}] keyword={kw} "
                f"judge_avg={judge_avg:.2f} — {j.judge.rationale[:80]}"
            )

    # Per-case breakdown.
    print("\n--- Per-case breakdown ---")
    for j in judged:
        kw = "PASS" if j.baseline.passed else "FAIL"
        print(
            f"  [{j.baseline.test_id}] kw={kw} | "
            f"help={j.judge.helpfulness:.2f} "
            f"correct={j.judge.correctness:.2f} "
            f"complete={j.judge.completeness:.2f}"
        )
        print(f"    judge: {j.judge.rationale}")


async def main() -> None:
    print("=" * 60)
    print("  CHALLENGE 2 — LLM-as-Judge Evaluation")
    print("=" * 60)

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

    judged = await evaluate_with_judge(test_cases)
    print_combined_summary(judged)


if __name__ == "__main__":
    asyncio.run(main())
