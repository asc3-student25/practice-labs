from notifications.application.ports import AuditRepository


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._entries: list[dict] = []

    def append(
        self,
        notification_id: str,
        previous_status: str | None,
        new_status: str,
        reason: str,
        channel: str | None,
    ) -> None:
        raise NotImplementedError


_: AuditRepository = InMemoryAuditRepository()
