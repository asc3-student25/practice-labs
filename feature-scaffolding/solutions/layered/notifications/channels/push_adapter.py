from notifications.channels.base import Channel, DeliveryResult
from notifications.models.notification import Notification


class PushAdapter:
    name = "push"

    def send(self, notification: Notification) -> DeliveryResult:
        """Stub. A real implementation would call a push notification service."""
        raise NotImplementedError


_: Channel = PushAdapter()
