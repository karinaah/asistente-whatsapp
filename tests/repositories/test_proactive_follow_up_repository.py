from datetime import date, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base

from app.models.proactive_follow_up import (
    FollowUpStatus,
    FollowUpType,
    ProactiveFollowUp,
)

from app.models.routine_db import RoutineDB
from app.models.task_db import TaskDB
from app.models.user_db import UserDB
from app.repositories.proactive_follow_up_repository import (
    ProactiveFollowUpRepository,
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


def test_creates_and_gets_pending_follow_up():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ProactiveFollowUpRepository()

        repository.create(
            db,
            ProactiveFollowUp(
                user_id=user.id,
                follow_up_type=(
                    FollowUpType.PENDING_TASKS
                ),
                title="Tareas pendientes",
                message="Aún tienes tareas pendientes.",
            ),
        )

        pending = repository.get_pending_by_user_id(
            db,
            user.id,
        )

        assert len(pending) == 1
        assert pending[0].user_id == user.id
        assert (
            pending[0].follow_up_type
            == FollowUpType.PENDING_TASKS.value
        )
        assert pending[0].status == "pending"

    finally:
        db.close()


def test_detects_existing_follow_up_for_same_day():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ProactiveFollowUpRepository()

        repository.create(
            db,
            ProactiveFollowUp(
                user_id=user.id,
                follow_up_type=(
                    FollowUpType.PENDING_TASKS
                ),
                title="Tareas pendientes",
                message="Aún tienes tareas pendientes.",
                created_at=datetime(
                    2026,
                    9,
                    27,
                    15,
                    0,
                ),
            ),
        )

        exists = repository.exists_for_day(
            db,
            user_id=user.id,
            follow_up_type=(
                FollowUpType.PENDING_TASKS
            ),
            target_date=date(2026, 9, 27),
        )

        assert exists is True

        exists_next_day = repository.exists_for_day(
            db,
            user_id=user.id,
            follow_up_type=(
                FollowUpType.PENDING_TASKS
            ),
            target_date=date(2026, 9, 28),
        )

        assert exists_next_day is False

    finally:
        db.close()

def test_resolves_pending_follow_up():
    db = create_test_db()

    try:
        user = UserDB(name="Test User")
        db.add(user)
        db.commit()
        db.refresh(user)

        repository = ProactiveFollowUpRepository()

        follow_up = repository.create(
            db,
            ProactiveFollowUp(
                user_id=user.id,
                follow_up_type=(
                    FollowUpType.PENDING_TASKS
                ),
                title="Tareas pendientes",
                message="Aún tienes tareas pendientes.",
            ),
        )

        resolved = repository.resolve(
            db,
            follow_up_id=follow_up.id,
            status=FollowUpStatus.COMPLETED,
        )

        assert resolved is not None
        assert (
            resolved.status
            == FollowUpStatus.COMPLETED.value
        )
        assert resolved.resolved_at is not None

    finally:
        db.close()        