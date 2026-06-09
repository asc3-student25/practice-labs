from dataclasses import dataclass


@dataclass(frozen=True)
class SendNotification:
    recipient: str
    channels: list[str]
    subject: str
    body: str


@dataclass(frozen=True)
class RetryNotification:
    notification_id: str
