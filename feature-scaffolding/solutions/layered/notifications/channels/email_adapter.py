from notifications.channels.base import Channel, DeliveryResult
from notifications.models.notification import Notification


class EmailAdapter:
    name = "email"

    def send(self, notification: Notification) -> DeliveryResult:
        """Stub. A real implementation would call an SMTP gateway."""
        raise NotImplementedError


_: Channel = EmailAdapter()  # static protocol conformance check
