"""Inbound adapter: Flask HTTP API translated into application use cases.

Depends on the application's use cases and the domain's commands. Does not
touch ports or adapters directly.
"""

from flask import Blueprint

from notifications.application.use_cases import (
    CreateAndDispatch,
    GetNotification,
    ListByRecipient,
)


def create_blueprint(
    create_and_dispatch: CreateAndDispatch,
    get_notification: GetNotification,
    list_by_recipient: ListByRecipient,
) -> Blueprint:
    """Build a Flask blueprint wired to the given use cases."""
    raise NotImplementedError
