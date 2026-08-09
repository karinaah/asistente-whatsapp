from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.adaptive_profile_db import AdaptiveProfileDB
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from datetime import datetime

from app.models.task_execution import TaskExecution

def test_get_returns_none_when_profile_does_not_exist():
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
        service = AdaptiveProfileService()

        profile = service.get(db)

        assert profile is None
    finally:
        db.close()


def test_rebuild_generates_and_persists_profile(monkeypatch):
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
        service = AdaptiveProfileService()

        executions = [
            TaskExecution(
                task_id=1,
                estimated_minutes=60,
                actual_minutes=72,
                started_at=datetime.fromisoformat(
                    "2026-08-01T09:00:00"
                ),
                finished_at=datetime.fromisoformat(
                    "2026-08-01T10:12:00"
                ),
                category="trabajo",
                context="trabajo",
            ),
            TaskExecution(
                task_id=2,
                estimated_minutes=60,
                actual_minutes=72,
                started_at=datetime.fromisoformat(
                    "2026-08-02T09:00:00"
                ),
                finished_at=datetime.fromisoformat(
                    "2026-08-02T10:12:00"
                ),
                category="trabajo",
                context="trabajo",
            ),
            TaskExecution(
                task_id=3,
                estimated_minutes=60,
                actual_minutes=72,
                started_at=datetime.fromisoformat(
                    "2026-08-03T09:00:00"
                ),
                finished_at=datetime.fromisoformat(
                    "2026-08-03T10:12:00"
                ),
                category="trabajo",
                context="trabajo",
            ),
        ]

        monkeypatch.setattr(
            service.task_execution_service,
            "get_all_for_learning",
            lambda db: executions,
        )

        rebuilt_profile = service.rebuild(db)

        stored_profile = service.get(db)

        assert rebuilt_profile.generated_from_executions == 3
        assert rebuilt_profile.work_duration_multiplier == 1.2

        assert stored_profile is not None
        assert stored_profile.generated_from_executions == 3
        assert stored_profile.work_duration_multiplier == 1.2

    finally:
        db.close()        