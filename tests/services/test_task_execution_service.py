from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.models.task_execution_db import TaskExecutionDB
from app.models.user_db import UserDB
from app.services.task_execution_service import (
    TaskExecutionService,
)


def create_test_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    return TestingSessionLocal()


def create_execution(
    task_id: int,
) -> TaskExecution:
    return TaskExecution(
        task_id=task_id,
        estimated_minutes=60,
        actual_minutes=75,
        started_at=datetime.fromisoformat(
            "2026-08-08T09:00:00"
        ),
        finished_at=datetime.fromisoformat(
            "2026-08-08T10:15:00"
        ),
        category=TaskCategory.work,
        context=TaskContext.work,
    )


def test_save_execution_with_user():
    db = create_test_db()

    try:
        user = UserDB(name="Cinthia")

        db.add(user)
        db.commit()
        db.refresh(user)

        service = TaskExecutionService()

        stored = service.save(
            db,
            create_execution(task_id=1),
            user_id=user.id,
        )

        assert stored.user_id == user.id

    finally:
        db.close()


def test_get_all_for_learning_filters_by_user():
    db = create_test_db()

    try:
        user_a = UserDB(name="Usuario A")
        user_b = UserDB(name="Usuario B")

        db.add_all([user_a, user_b])
        db.commit()
        db.refresh(user_a)
        db.refresh(user_b)

        service = TaskExecutionService()

        service.save(
            db,
            create_execution(task_id=1),
            user_id=user_a.id,
        )

        service.save(
            db,
            create_execution(task_id=2),
            user_id=user_b.id,
        )

        executions = service.get_all_for_learning(
            db,
            user_id=user_a.id,
        )

        assert len(executions) == 1
        assert executions[0].task_id == 1

    finally:
        db.close()