from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user_db import UserDB
from app.services.user_service import UserService


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


def test_user_service_creates_and_retrieves_user():
    db = create_test_db()

    try:
        service = UserService()

        created_user = service.create_user(
            db,
            name="Cinthia",
        )

        stored_user = service.get_user(
            db,
            user_id=created_user.id,
        )

        assert stored_user is not None
        assert stored_user.id == created_user.id
        assert stored_user.name == "Cinthia"

    finally:
        db.close()