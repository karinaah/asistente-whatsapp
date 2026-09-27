from sqlalchemy.orm import Session

from app.models.notification import (
    Notification,
    NotificationChannel,
)
from app.models.notification_db import NotificationDB
from app.models.proactive_follow_up_db import (
    ProactiveFollowUpDB,
)
from app.repositories.notification_repository import (
    NotificationRepository,
)


class NotificationService:
    def __init__(
        self,
        repository: NotificationRepository | None = None,
    ):
        self.repository = (
            repository
            or NotificationRepository()
        )

    def create_from_follow_up(
        self,
        db: Session,
        follow_up: ProactiveFollowUpDB,
        channel: NotificationChannel = (
            NotificationChannel.WEB
        ),
    ) -> NotificationDB:
        notification = Notification(
            user_id=follow_up.user_id,
            follow_up_id=follow_up.id,
            title=follow_up.title,
            message=follow_up.message,
            channel=channel,
        )

        return self.repository.create(
            db,
            notification,
        )

    def get_pending_for_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[NotificationDB]:
        return self.repository.get_pending_by_user_id(
            db,
            user_id,
        )

    def mark_delivered(
        self,
        db: Session,
        notification_id: int,
    ) -> NotificationDB | None:
        return self.repository.mark_delivered(
            db,
            notification_id,
        )

    def mark_read(
        self,
        db: Session,
        notification_id: int,
    ) -> NotificationDB | None:
        return self.repository.mark_read(
            db,
            notification_id,
        )