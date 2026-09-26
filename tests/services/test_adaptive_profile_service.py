from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.adaptive_profile_db import AdaptiveProfileDB
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from datetime import datetime

from app.models.task_execution import TaskExecution
from app.models.user_db import UserDB
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
            lambda db, user_id=None: executions,
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

def test_rebuild_uses_executions_for_requested_user(
    monkeypatch,
):
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
                actual_minutes=90,
                started_at=datetime.fromisoformat(
                    "2026-08-01T09:00:00"
                ),
                finished_at=datetime.fromisoformat(
                    "2026-08-01T10:30:00"
                ),
                category="trabajo",
                context="trabajo",
            ),
        ]

        received_user_ids = []

        def get_executions(
            db,
            user_id=None,
        ):
            received_user_ids.append(user_id)
            return executions

        monkeypatch.setattr(
            service.task_execution_service,
            "get_all_for_learning",
            get_executions,
        )

        profile = service.rebuild(
            db,
            user_id=123,
        )

        assert received_user_ids == [123]
        assert profile.generated_from_executions == 1
        assert profile.work_duration_multiplier == 1.5

    finally:
        db.close()      

def test_rebuild_persists_learning_in_user_profile(
    monkeypatch,
):
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

        service = AdaptiveProfileService()

        executions = [
            TaskExecution(
                task_id=1,
                estimated_minutes=60,
                actual_minutes=90,
                started_at=datetime.fromisoformat(
                    "2026-08-01T09:00:00"
                ),
                finished_at=datetime.fromisoformat(
                    "2026-08-01T10:30:00"
                ),
                category="trabajo",
                context="trabajo",
            ),
        ]

        monkeypatch.setattr(
            service.task_execution_service,
            "get_all_for_learning",
            lambda db, user_id=None: executions,
        )

        rebuilt_profile = service.rebuild(
            db,
            user_id=user.id,
        )

        stored_user_profile = (
            service.user_profile_service
            .get_profile(
                db,
                user_id=user.id,
            )
        )

        assert rebuilt_profile.work_duration_multiplier == 1.5

        assert stored_user_profile is not None
        assert (
            stored_user_profile.work_duration_multiplier
            == 1.5
        )

        # El camino por usuario no debe crear
        # el antiguo perfil global.
        assert service.get(db) is None

    finally:
        db.close()    

def test_get_returns_user_specific_profile():
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

        service = AdaptiveProfileService()

        service.user_profile_service.create_profile(
            db,
            user_id=user.id,
        )

        service.user_profile_service.update_work_duration_multiplier(
            db,
            user_id=user.id,
            multiplier=1.25,
        )

        profile = service.get(
            db,
            user_id=user.id,
        )

        assert profile is not None
        assert profile.work_duration_multiplier == 1.25

    finally:
        db.close()              