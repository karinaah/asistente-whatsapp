from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user_db import UserDB
from app.models.user_profile_db import UserProfileDB
from app.repositories.user_profile_repository import (
    UserProfileRepository,
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


def test_create_user_profile():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = UserProfileRepository()

        profile = repository.create(
            db,
            user_id=user.id,
        )

        assert profile.id is not None
        assert profile.user_id == user.id

    finally:
        db.close()


def test_get_profile_by_user_id():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = UserProfileRepository()

        created_profile = repository.create(
            db,
            user_id=user.id,
        )

        stored_profile = repository.get_by_user_id(
            db,
            user_id=user.id,
        )

        assert stored_profile is not None
        assert stored_profile.id == created_profile.id
        assert stored_profile.user_id == user.id

    finally:
        db.close()


def test_update_work_duration_multiplier():
    db = create_test_db()

    try:
        user = UserDB(
            name="Cinthia",
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        repository = UserProfileRepository()

        repository.create(
            db,
            user_id=user.id,
        )

        updated_profile = (
            repository.update_work_duration_multiplier(
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