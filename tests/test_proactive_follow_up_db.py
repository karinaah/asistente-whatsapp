from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
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


def test_persists_proactive_follow_up():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        follow_up = ProactiveFollowUpDB(
            user_id=user.id,
            follow_up_type="pending_tasks",
            title="Tareas pendientes",
            message=(
                "Todavía tienes tareas pendientes para hoy."
            ),
            status="pending",
        )

        db.add(follow_up)
        db.commit()
        db.refresh(follow_up)

        assert follow_up.id is not None
        assert follow_up.user_id == user.id
        assert follow_up.follow_up_type == "pending_tasks"
        assert follow_up.status == "pending"
        assert follow_up.task_id is None
        assert follow_up.routine_id is None
        assert follow_up.resolved_at is None

    finally:
        db.close()