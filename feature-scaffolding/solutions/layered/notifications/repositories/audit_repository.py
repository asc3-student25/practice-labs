from typing import Protocol

from notifications.models.notification import AuditEntry


class AuditRepository(Protocol):
    def append(self, entry: AuditEntry) -> None: ...
    def list_for_notification(self, notification_id: str) -> list[AuditEntry]: ...


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._entries: list[AuditEntry] = []

    def append(self, entry: AuditEntry) -> None:
        raise NotImplementedError

    def list_for_notification(self, notification_id: str) -> list[AuditEntry]:
        raise NotImplementedError


_: AuditRepository = InMemoryAuditRepository()
