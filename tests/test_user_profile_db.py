from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user_db import UserDB
from app.models.user_profile_db import UserProfileDB


def test_user_can_have_persistent_profile():
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

        profile = UserProfileDB(
            user_id=user.id,
        )

        db.add(profile)
        db.commit()
        db.refresh(profile)

        assert profile.id is not None
        assert profile.user_id == user.id
        assert profile.work_duration_multiplier == 1.0
    finally:
        db.close()