"""
Lab Solution: Challenge 1 — Extend the Evaluation Loop and Model Comparison

Imports the evaluation harness from main.py and demonstrates two extensions
the Challenge calls for:

* a fourth test case in a new category ("account access") with its own
  expected keywords, so the golden dataset isn't dominated by policy/
  logistics questions
* a third model tier in the compare_models call (gpt-4-turbo) so the
  cost-vs-quality trade-off is visible across three points instead of two

Run: python challenge1_model_comparison.py
"""

import asyncio

from main import AgentEvaluator, TestCase


# Build the extended test suite — three originals plus one new account-access case.
EXTENDED_TEST_CASES = [
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
    # Fourth test case in a new category. Account-access questions stress
    # different parts of the system prompt than policy/logistics ones do,
    # so adding this category gives the evaluator a more balanced signal.
    TestCase(
        id="account-recovery",
        question="I forgot my password. How do I reset it?",
        expected_keywords=["reset", "email", "link"],
        category="account",
    ),
]


async def main() -> None:
    print("=" * 60)
    print("  CHALLENGE 1 — Extended Evaluation + Three-Tier Comparison")
    print("=" * 60)

    evaluator = AgentEvaluator(EXTENDED_TEST_CASES)

    # Predict before running so students can compare prediction to result.
    print(
        "\nPrediction:\n"
        "  - gpt-4-turbo: highest pass rate, mid-cost\n"
        "  - gpt-4o:      highest pass rate or close, highest cost\n"
        "  - gpt-5.4-mini: lowest cost per request, may miss edge cases\n"
    )

    # Run the four-case suite once to surface the new category.
    print("\n1. Running extended suite (default model)...")
    baseline_results = await evaluator.evaluate(model="gpt-5.4-mini")
    print(evaluator.generate_report(baseline_results))

    # Three-tier model comparison — the existing compare_models() loops
    # over whatever list you pass. Adding a third entry surfaces the
    # mid-tier point on the cost-quality curve.
    print("\n2. Comparing three model tiers...")
    comparison = await evaluator.compare_models(
        ["gpt-5.4-mini", "gpt-4-turbo", "gpt-4o"]
    )

    print("\n" + "=" * 60)
    print("  THREE-TIER MODEL COMPARISON")
    print("=" * 60)

    # Print one block per tier with the same metrics shape as the Core Lab.
    for model, metrics in comparison.items():
        print(f"\n{model}:")
        print(
            f"  Pass rate:    {metrics['passed_tests']}/{metrics['total_tests']} "
            f"({100 * metrics['pass_rate']:.0f}%)"
        )
        print(f"  Total cost:   ${metrics['total_cost_usd']:.4f}")
        print(f"  Avg cost:     ${metrics['avg_cost_usd']:.5f}/request")
        print(f"  Avg latency:  {metrics['avg_latency_ms']:.0f}ms")
        print(f"  Total tokens: {metrics['total_tokens']:,}")

    # Pick the best-cost-quality trade-off so students see how to read
    # the comparison output programmatically.
    print("\n" + "-" * 60)
    print("  Trade-off pick (highest pass rate, then lowest cost as tiebreaker)")
    print("-" * 60)
    ranked = sorted(
        comparison.items(),
        key=lambda kv: (-kv[1]["pass_rate"], kv[1]["total_cost_usd"]),
    )
    best_model, best_metrics = ranked[0]
    print(
        f"  Recommendation: {best_model} "
        f"({100 * best_metrics['pass_rate']:.0f}% pass at "
        f"${best_metrics['total_cost_usd']:.4f} total)"
    )


if __name__ == "__main__":
    asyncio.run(main())
