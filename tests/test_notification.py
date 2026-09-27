from app.models.notification import (
    Notification,
    NotificationChannel,
    NotificationStatus,
)


def test_creates_pending_web_notification():
    notification = Notification(
        user_id=1,
        title="Tareas pendientes",
        message="Todavía tienes tareas pendientes para hoy.",
    )

    assert notification.user_id == 1
    assert notification.follow_up_id is None
    assert (
        notification.channel
        == NotificationChannel.WEB
    )
    assert (
        notification.status
        == NotificationStatus.PENDING
    )
    assert notification.delivered_at is None
    assert notification.read_at is None


def test_notification_can_reference_follow_up():
    notification = Notification(
        user_id=1,
        follow_up_id=10,
        title="Tareas pendientes",
        message="Todavía tienes tareas pendientes para hoy.",
    )

    assert notification.follow_up_id == 10