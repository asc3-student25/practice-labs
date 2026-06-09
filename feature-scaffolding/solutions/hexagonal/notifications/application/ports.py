"""Ports: the abstract interfaces the domain requires from the outside world.

Every outbound dependency of the application is defined here as a Protocol.
Concrete implementations live in adapters/outbound/; they depend on these
ports, not the other way around.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from notifications.domain.notification import Notification


class FailureKind(str, Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"


@dataclass
class DeliveryResult:
    success: bool
    failure_kind: FailureKind | None = None
    reason: str = ""


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> Notification: ...
    def get(self, notification_id: str) -> Notification | None: ...
    def list_by_recipient(self, recipient: str) -> list[Notification]: ...


class AuditRepository(Protocol):
    def append(
        self,
        notification_id: str,
        previous_status: str | None,
        new_status: str,
        reason: str,
        channel: str | None,
    ) -> None: ...


class ChannelGateway(Protocol):
    name: str

    def send(self, notification: Notification) -> DeliveryResult: ...
