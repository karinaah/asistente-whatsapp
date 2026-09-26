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