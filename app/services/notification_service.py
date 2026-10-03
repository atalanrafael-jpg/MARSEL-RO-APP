from __future__ import annotations

from datetime import datetime, timezone

from ..business_models import NotificationMessage


class NotificationService:
    """In-memory notification service for customer and staff communication."""

    def __init__(self) -> None:
        self._messages: list[NotificationMessage] = []

    def send(self, *, repair_id: str, channel: str, template: str, message: str) -> NotificationMessage:
        notification = NotificationMessage(
            repair_id=repair_id,
            channel=channel,
            template=template,
            message=message,
            created_at=datetime.now(timezone.utc),
        )
        self._messages.append(notification)
        return notification

    def list_messages(self, repair_id: str | None = None) -> list[NotificationMessage]:
        if repair_id is None:
            return list(self._messages)
        return [item for item in self._messages if item.repair_id == repair_id]


__all__ = ["NotificationService"]
