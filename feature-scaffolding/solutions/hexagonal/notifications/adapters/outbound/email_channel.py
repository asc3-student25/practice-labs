from notifications.application.ports import ChannelGateway, DeliveryResult
from notifications.domain.notification import Notification


class EmailChannel:
    name = "email"

    def send(self, notification: Notification) -> DeliveryResult:
        raise NotImplementedError


_: ChannelGateway = EmailChannel()
