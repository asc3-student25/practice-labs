from dataclasses import dataclass


@dataclass
class RetryPolicy:
    """Retry configuration for transient channel failures.

    Permanent failures do not retry. The policy is passed to the
    notification service at construction time; swapping policies does
    not require editing the service.
    """

    max_attempts: int = 3
    base_delay_seconds: float = 1.0

    def delay_for_attempt(self, attempt: int) -> float:
        raise NotImplementedError
