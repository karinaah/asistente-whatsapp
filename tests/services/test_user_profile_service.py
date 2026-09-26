from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user_db import UserDB
from app.models.user_profile_db import UserProfileDB
from app.repositories.user_profile_repository import (
    UserProfileRepository,
)
from app.services.user_profile_service import (
    UserProfileService,
)
from datetime import datetime

from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    HumanState,
    StressLevel,
)
from app.models.task import TaskCategory, TaskContext
from app.models.task_execution import TaskExecution
from app.services.learning_service import LearningService

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


def test_user_profile_service_creates_and_retrieves_profile():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = UserProfileService(
            repository=UserProfileRepository()
        )

        created_profile = service.create_profile(
            db,
            user_id=user.id,
        )

        stored_profile = service.get_profile(
            db,
            user_id=user.id,
        )

        assert stored_profile is not None
        assert stored_profile.id == created_profile.id
        assert stored_profile.user_id == user.id

    finally:
        db.close()

def test_user_profile_service_updates_work_duration_multiplier():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = UserProfileService(
            repository=UserProfileRepository()
        )

        service.create_profile(
            db,
            user_id=user.id,
        )

        updated_profile = (
            service.update_work_duration_multiplier(
                db,
                user_id=user.id,
                multiplier=1.25,
            )
        )

        assert updated_profile is not None
        assert (
            updated_profile.work_duration_multiplier
            == 1.25
        )

    finally:
        db.close()        

def test_user_profile_service_persists_learned_profile():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        profile_service = UserProfileService(
            repository=UserProfileRepository()
        )

        profile_service.create_profile(
            db,
            user_id=user.id,
        )

        executions = [
            TaskExecution(
                task_id=1,
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
                human_state=HumanState(
                    energy=EnergyLevel.high,
                    focus=FocusLevel.high,
                    stress=StressLevel.low,
                ),
            )
        ]

        adaptive_profile = (
            LearningService().build_profile(
                executions
            )
        )

        updated_profile = (
            profile_service.update_from_adaptive_profile(
                db,
                user_id=user.id,
                adaptive_profile=adaptive_profile,
            )
        )

        assert updated_profile is not None
        assert (
            updated_profile.work_duration_multiplier
            == 1.25
        )

    finally:
        db.close()        

def test_user_profile_service_builds_adaptive_profile():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        service = UserProfileService(
            repository=UserProfileRepository()
        )

        service.create_profile(
            db,
            user_id=user.id,
        )

        service.update_work_duration_multiplier(
            db,
            user_id=user.id,
            multiplier=1.25,
        )

        adaptive_profile = (
            service.build_adaptive_profile(
                db,
                user_id=user.id,
            )
        )

        assert adaptive_profile is not None
        assert (
            adaptive_profile.work_duration_multiplier
            == 1.25
        )

    finally:
        db.close()        