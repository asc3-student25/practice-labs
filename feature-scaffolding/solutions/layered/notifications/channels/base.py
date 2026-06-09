from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from notifications.models.notification import Notification


class FailureKind(str, Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"


@dataclass
class DeliveryResult:
    success: bool
    failure_kind: FailureKind | None = None
    reason: str = ""


class Channel(Protocol):
    """The contract every channel adapter implements."""

    name: str

    def send(self, notification: Notification) -> DeliveryResult: ...
