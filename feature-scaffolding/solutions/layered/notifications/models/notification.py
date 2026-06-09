from dataclasses import dataclass, field
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
    id: str
    recipient: str
    channels: list[str]
    subject: str
    body: str
    status: NotificationStatus = NotificationStatus.PENDING
    created_at: str = ""
    updated_at: str = ""


@dataclass
class AuditEntry:
    notification_id: str
    timestamp: str
    previous_status: NotificationStatus | None
    new_status: NotificationStatus
    reason: str = ""
    channel: str | None = None
