"""Flask blueprint exposing the notification dispatcher HTTP API.

Thin translation between HTTP and the service layer. Does not contain
business rules — those live in services.notification_service.
"""

from flask import Blueprint

from notifications.services.notification_service import NotificationService


def create_blueprint(service: NotificationService) -> Blueprint:
    """Build a Flask blueprint wired to the given service.

    Routes:
        POST /notifications           -> service.create + service.dispatch
        GET  /notifications/<id>      -> service.get
        GET  /notifications?recipient -> service.list_for_recipient
    """
    raise NotImplementedError
