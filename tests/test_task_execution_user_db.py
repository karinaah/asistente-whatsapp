from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.task_execution_db import TaskExecutionDB
from app.models.user_db import UserDB


def test_task_execution_can_be_associated_with_user():
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

    db = TestingSessionLocal()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        execution = TaskExecutionDB(
            user_id=user.id,
            task_id=1,
            estimated_minutes=60,
            actual_minutes=75,
            started_at=datetime.fromisoformat(
                "2026-08-08T09:00:00"
            ),
            finished_at=datetime.fromisoformat(
                "2026-08-08T10:15:00"
            ),
            category="trabajo",
            context="trabajo",
        )

        db.add(execution)
        db.commit()
        db.refresh(execution)

        assert execution.id is not None
        assert execution.user_id == user.id

    finally:
        db.close()