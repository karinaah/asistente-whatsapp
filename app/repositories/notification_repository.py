from datetime import datetime

from sqlalchemy.orm import Session

from app.models.notification import (
    Notification,
    NotificationStatus,
)
from app.models.notification_db import NotificationDB


class NotificationRepository:
    def create(
        self,
        db: Session,
        notification: Notification,
    ) -> NotificationDB:
        db_notification = NotificationDB(
            user_id=notification.user_id,
            follow_up_id=notification.follow_up_id,
            title=notification.title,
            message=notification.message,
            channel=notification.channel.value,
            status=notification.status.value,
            created_at=notification.created_at,
            delivered_at=notification.delivered_at,
            read_at=notification.read_at,
        )

        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)

        return db_notification

    def get_pending_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> list[NotificationDB]:
        return (
            db.query(NotificationDB)
            .filter(
                NotificationDB.user_id == user_id,
                NotificationDB.status
                == NotificationStatus.PENDING.value,
            )
            .order_by(NotificationDB.created_at)
            .all()
        )

    def mark_delivered(
        self,
        db: Session,
        notification_id: int,
    ) -> NotificationDB | None:
        notification = (
            db.query(NotificationDB)
            .filter(
                NotificationDB.id
                == notification_id,
            )
            .first()
        )

        if notification is None:
            return None

        notification.status = (
            NotificationStatus.DELIVERED.value
        )
        notification.delivered_at = datetime.now()

        db.commit()
        db.refresh(notification)

        return notification

    def mark_read(
        self,
        db: Session,
        notification_id: int,
    ) -> NotificationDB | None:
        notification = (
            db.query(NotificationDB)
            .filter(
                NotificationDB.id
                == notification_id,
            )
            .first()
        )

        if notification is None:
            return None

        notification.status = (
            NotificationStatus.READ.value
        )

        if notification.delivered_at is None:
            notification.delivered_at = datetime.now()

        notification.read_at = datetime.now()

        db.commit()
        db.refresh(notification)

        return notification