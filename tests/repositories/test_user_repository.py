from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config.database import Base
from app.models.user_db import UserDB
from app.repositories.user_repository import UserRepository


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


def test_create_user():
    db = create_test_db()

    try:
        repository = UserRepository()

        user = repository.create(
            db,
            name="Cinthia",
        )

        assert user.id is not None
        assert user.name == "Cinthia"

    finally:
        db.close()


def test_get_user_by_id():
    db = create_test_db()

    try:
        repository = UserRepository()

        created_user = repository.create(
            db,
            name="Cinthia",
        )

        stored_user = repository.get_by_id(
            db,
            created_user.id,
        )

        assert stored_user is not None
        assert stored_user.id == created_user.id
        assert stored_user.name == "Cinthia"

    finally:
        db.close()