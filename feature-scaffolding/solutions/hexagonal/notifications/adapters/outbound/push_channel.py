from notifications.application.ports import ChannelGateway, DeliveryResult
from notifications.domain.notification import Notification


class PushChannel:
    name = "push"

    def send(self, notification: Notification) -> DeliveryResult:
        raise NotImplementedError


_: ChannelGateway = PushChannel()
