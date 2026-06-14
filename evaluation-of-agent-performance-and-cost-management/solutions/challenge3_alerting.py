"""
Lab Solution: Challenge 3 — Cost Alerting

Extends the Core Lab's CostTracker with budget guardrails. Adds daily
and per-user thresholds and exposes alert states (`ok`, `warning`,
`over_budget`) that callers can act on — log a warning, refuse a
request, or page on-call.

Run: python challenge3_alerting.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional
from datetime import datetime
import os
import tempfile

from main import CostTracker


AlertState = Literal["ok", "warning", "over_budget"]


@dataclass
class BudgetAlert:
    """Result of a budget check.

    Carries enough detail for the caller to log or display the alert
    without re-querying the tracker.
    """

    state: AlertState
    spent: float
    threshold: float
    message: str

    @property
    def utilization_pct(self) -> float:
        """Percentage of the threshold that's currently consumed."""
        if self.threshold <= 0:
            return 0.0
        return 100.0 * self.spent / self.threshold


class AlertingCostTracker(CostTracker):
    """CostTracker with daily and per-user budget thresholds.

    Inherits the existing aggregation accessors (`get_total_cost`,
    `get_daily_costs`) rather than reimplementing them — the alert
    methods build on the existing accessors so we don't duplicate
    aggregation logic. The Challenge text explicitly recommends this.
    """

    def __init__(
        self,
        log_file: str = "cost_log.json",
        daily_threshold: Optional[float] = None,
        per_user_threshold: Optional[float] = None,
        warning_ratio: float = 0.8,
    ):
        """
        Args:
            log_file: Path used by the parent CostTracker.
            daily_threshold: USD ceiling for the current day's spend.
                Pass None to disable daily alerts.
            per_user_threshold: USD ceiling per user across the full
                tracker history. Pass None to disable per-user alerts.
            warning_ratio: Fraction of threshold (0.0-1.0) that triggers
                a `warning` alert. Above the threshold itself triggers
                `over_budget`. Default 0.8 (80%).
        """
        super().__init__(log_file=log_file)
        if not 0.0 < warning_ratio < 1.0:
            raise ValueError(
                f"warning_ratio must be between 0.0 and 1.0, got {warning_ratio!r}"
            )
        self.daily_threshold = daily_threshold
        self.per_user_threshold = per_user_threshold
        self.warning_ratio = warning_ratio

    def _classify(self, spent: float, threshold: float) -> AlertState:
        """Map a spend/threshold pair to an AlertState."""
        if spent >= threshold:
            return "over_budget"
        if spent >= self.warning_ratio * threshold:
            return "warning"
        return "ok"

    def check_daily_alert(self, day: Optional[str] = None) -> BudgetAlert:
        """Return the alert state for a given day's spend.

        Args:
            day: ISO date string (YYYY-MM-DD). Defaults to today (UTC).
        """
        if self.daily_threshold is None:
            return BudgetAlert(
                state="ok",
                spent=0.0,
                threshold=0.0,
                message="No daily threshold configured.",
            )

        target_day = day or datetime.now().strftime("%Y-%m-%d")
        spent = self.get_daily_costs().get(target_day, 0.0)
        state = self._classify(spent, self.daily_threshold)

        message = self._format_message(
            scope=f"Daily ({target_day})",
            spent=spent,
            threshold=self.daily_threshold,
            state=state,
        )
        return BudgetAlert(
            state=state,
            spent=spent,
            threshold=self.daily_threshold,
            message=message,
        )

    def check_user_alert(self, user_id: str) -> BudgetAlert:
        """Return the alert state for a given user's total spend."""
        if self.per_user_threshold is None:
            return BudgetAlert(
                state="ok",
                spent=0.0,
                threshold=0.0,
                message="No per-user threshold configured.",
            )

        spent = self.get_total_cost(user_id=user_id)
        state = self._classify(spent, self.per_user_threshold)
        message = self._format_message(
            scope=f"User '{user_id}'",
            spent=spent,
            threshold=self.per_user_threshold,
            state=state,
        )
        return BudgetAlert(
            state=state,
            spent=spent,
            threshold=self.per_user_threshold,
            message=message,
        )

    @staticmethod
    def _format_message(
        scope: str, spent: float, threshold: float, state: AlertState
    ) -> str:
        prefix = {
            "ok": "OK",
            "warning": "WARNING",
            "over_budget": "OVER BUDGET",
        }[state]
        pct = 100.0 * spent / threshold if threshold else 0.0
        return (
            f"[{prefix}] {scope}: ${spent:.4f} of ${threshold:.4f} "
            f"({pct:.0f}% of threshold)"
        )


def main() -> None:
    print("=" * 60)
    print("  CHALLENGE 3 — Cost Alerting")
    print("=" * 60)

    # Use a temp log file so this demo doesn't collide with the Core Lab
    # cost_log.json the student already has on disk.
    with tempfile.NamedTemporaryFile(
        suffix=".jsonl", delete=False, mode="w"
    ) as fh:
        log_path = fh.name

    try:
        # Tight thresholds so each alert state is reachable in the demo.
        # In production these come from config/env.
        tracker = AlertingCostTracker(
            log_file=log_path,
            daily_threshold=0.10,
            per_user_threshold=0.05,
            warning_ratio=0.8,  # 80% of threshold trips a warning
        )

        print(
            f"\nDaily threshold:    ${tracker.daily_threshold:.4f}"
            f"\nPer-user threshold: ${tracker.per_user_threshold:.4f}"
            f"\nWarning at:         {int(tracker.warning_ratio * 100)}% of either"
        )

        # Phase 1: small request — both alerts should be `ok`.
        print("\n" + "-" * 60)
        print("  Phase 1: small request from alice ($0.01)")
        print("-" * 60)
        tracker.log_request("alice", tokens=100, cost=0.01)
        print(tracker.check_daily_alert().message)
        print(tracker.check_user_alert("alice").message)

        # Phase 2: alice continues — push her into the warning band but
        # not past the cap. Pick an increment that lands clearly above
        # 80% of the threshold (0.045 = 90% of 0.05) rather than exactly
        # at the boundary, so floating-point drift can't mask the alert.
        print("\n" + "-" * 60)
        print("  Phase 2: alice's running spend approaches per-user cap")
        print("-" * 60)
        tracker.log_request("alice", tokens=350, cost=0.035)
        print(tracker.check_user_alert("alice").message)  # warning band
        print(tracker.check_daily_alert().message)

        # Phase 3: alice goes over her per-user threshold.
        print("\n" + "-" * 60)
        print("  Phase 3: alice exceeds per-user threshold")
        print("-" * 60)
        tracker.log_request("alice", tokens=150, cost=0.015)
        alert = tracker.check_user_alert("alice")
        print(alert.message)
        # Show how a caller might act on the alert state.
        if alert.state == "over_budget":
            print(
                f"  -> would refuse further requests for alice "
                f"(spent {alert.utilization_pct:.0f}% of cap)"
            )

        # Phase 4: bob's traffic pushes the daily total over the daily cap
        # even though his per-user spend is fine.
        print("\n" + "-" * 60)
        print("  Phase 4: bob's traffic trips the daily threshold")
        print("-" * 60)
        for i in range(4):
            tracker.log_request("bob", tokens=100, cost=0.015)
        print(tracker.check_daily_alert().message)
        print(tracker.check_user_alert("bob").message)

        # Phase 5: raising thresholds returns alerts to ok without
        # changing any of the underlying spend data — the demo's whole
        # validation criterion.
        print("\n" + "-" * 60)
        print("  Phase 5: raise thresholds; alerts return to OK")
        print("-" * 60)
        tracker.daily_threshold = 10.0
        tracker.per_user_threshold = 5.0
        print(tracker.check_daily_alert().message)
        print(tracker.check_user_alert("alice").message)
        print(tracker.check_user_alert("bob").message)
    finally:
        if os.path.exists(log_path):
            os.unlink(log_path)


if __name__ == "__main__":
    main()
