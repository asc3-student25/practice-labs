from dataclasses import dataclass
from enum import Enum


class NotificationStatus(str, Enum):
    PENDING = "pending"
    SENDING = "sending"
    SENT = "sent"
    PARTIAL = "partial"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Notification:
    """Pure domain entity. Depends on nothing outside the domain package."""

    id: str
    recipient: str
    channels: list[str]
    subject: str
    body: str
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: str = ""
    updated_at: str = ""
