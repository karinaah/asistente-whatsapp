from types import SimpleNamespace

from app.models.notification import (
    NotificationChannel,
    NotificationStatus,
)
from app.services.notification_service import (
    NotificationService,
)


class FakeNotificationRepository:
    def __init__(self):
        self.created = []

    def create(
        self,
        db,
        notification,
    ):
        notification.id = 1
        self.created.append(notification)
        return notification

    def get_pending_by_user_id(
        self,
        db,
        user_id,
    ):
        return [
            notification
            for notification in self.created
            if (
                notification.user_id == user_id
                and notification.status
                == NotificationStatus.PENDING
            )
        ]

    def mark_delivered(
        self,
        db,
        notification_id,
    ):
        for notification in self.created:
            if notification.id == notification_id:
                notification.status = (
                    NotificationStatus.DELIVERED
                )
                return notification

        return None

    def mark_read(
        self,
        db,
        notification_id,
    ):
        for notification in self.created:
            if notification.id == notification_id:
                notification.status = (
                    NotificationStatus.READ
                )
                return notification

        return None


def test_creates_web_notification_from_follow_up():
    repository = FakeNotificationRepository()
    service = NotificationService(
        repository=repository,
    )

    follow_up = SimpleNamespace(
        id=10,
        user_id=1,
        title="Tareas pendientes",
        message="Todavía tienes tareas pendientes.",
    )

    notification = service.create_from_follow_up(
        db=None,
        follow_up=follow_up,
    )

    assert notification.user_id == 1
    assert notification.follow_up_id == 10
    assert notification.title == follow_up.title
    assert notification.message == follow_up.message
    assert (
        notification.channel
        == NotificationChannel.WEB
    )
    assert (
        notification.status
        == NotificationStatus.PENDING
    )
    assert len(repository.created) == 1


def test_gets_pending_notifications_for_user():
    repository = FakeNotificationRepository()
    service = NotificationService(
        repository=repository,
    )

    follow_up = SimpleNamespace(
        id=10,
        user_id=1,
        title="Tareas pendientes",
        message="Todavía tienes tareas pendientes.",
    )

    service.create_from_follow_up(
        db=None,
        follow_up=follow_up,
    )

    pending = service.get_pending_for_user(
        db=None,
        user_id=1,
    )

    assert len(pending) == 1
    assert pending[0].user_id == 1


def test_marks_notification_as_delivered_and_read():
    repository = FakeNotificationRepository()
    service = NotificationService(
        repository=repository,
    )

    follow_up = SimpleNamespace(
        id=10,
        user_id=1,
        title="Tareas pendientes",
        message="Todavía tienes tareas pendientes.",
    )

    notification = service.create_from_follow_up(
        db=None,
        follow_up=follow_up,
    )

    delivered = service.mark_delivered(
        db=None,
        notification_id=notification.id,
    )

    assert (
        delivered.status
        == NotificationStatus.DELIVERED
    )

    read = service.mark_read(
        db=None,
        notification_id=notification.id,
    )

    assert (
        read.status
        == NotificationStatus.READ
    )