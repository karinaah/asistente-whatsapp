from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.notification_db import NotificationDB
from app.models.proactive_follow_up_db import (
    ProactiveFollowUpDB,
)
from app.models.routine_db import RoutineDB
from app.models.task_db import TaskDB
from app.models.user_db import UserDB


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


def test_persists_notification():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        notification = NotificationDB(
            user_id=user.id,
            title="Tareas pendientes",
            message=(
                "Todavía tienes tareas pendientes para hoy."
            ),
            channel="web",
            status="pending",
        )

        db.add(notification)
        db.commit()
        db.refresh(notification)

        assert notification.id is not None
        assert notification.user_id == user.id
        assert notification.follow_up_id is None
        assert notification.channel == "web"
        assert notification.status == "pending"
        assert notification.delivered_at is None
        assert notification.read_at is None

    finally:
        db.close()