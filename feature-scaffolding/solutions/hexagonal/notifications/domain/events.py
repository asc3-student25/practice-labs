from dataclasses import dataclass


@dataclass(frozen=True)
class NotificationSent:
    notification_id: str
    channel: str
    timestamp: str


@dataclass(frozen=True)
class NotificationFailed:
    notification_id: str
    channel: str
    reason: str
    kind: str  # "transient" or "permanent"
    timestamp: str
