from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.notification import (
    Notification,
    NotificationStatus,
)
from app.models.notification_db import NotificationDB
from app.models.proactive_follow_up_db import (
    ProactiveFollowUpDB,
)
from app.models.routine_db import RoutineDB
from app.models.task_db import TaskDB
from app.models.user_db import UserDB
from app.repositories.notification_repository import (
    NotificationRepository,
)


def create_test_db():
    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False,
        },
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)()


def test_creates_and_gets_pending_notification():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = NotificationRepository()

        notification = repository.create(
            db,
            Notification(
                user_id=user.id,
                title="Tareas pendientes",
                message="Todavía tienes tareas pendientes.",
            ),
        )

        pending = repository.get_pending_by_user_id(
            db,
            user.id,
        )

        assert notification.id is not None
        assert len(pending) == 1
        assert pending[0].id == notification.id
        assert (
            pending[0].status
            == NotificationStatus.PENDING.value
        )

    finally:
        db.close()


def test_marks_notification_as_delivered():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = NotificationRepository()

        notification = repository.create(
            db,
            Notification(
                user_id=user.id,
                title="Tareas pendientes",
                message="Todavía tienes tareas pendientes.",
            ),
        )

        delivered = repository.mark_delivered(
            db,
            notification.id,
        )

        assert delivered is not None
        assert (
            delivered.status
            == NotificationStatus.DELIVERED.value
        )
        assert delivered.delivered_at is not None

    finally:
        db.close()


def test_marks_notification_as_read():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = NotificationRepository()

        notification = repository.create(
            db,
            Notification(
                user_id=user.id,
                title="Tareas pendientes",
                message="Todavía tienes tareas pendientes.",
            ),
        )

        read = repository.mark_read(
            db,
            notification.id,
        )

        assert read is not None
        assert (
            read.status
            == NotificationStatus.READ.value
        )
        assert read.delivered_at is not None
        assert read.read_at is not None

    finally:
        db.close()