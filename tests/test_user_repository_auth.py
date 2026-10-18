import pytest

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.user_db import UserDB
from app.repositories.user_repository import UserRepository


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(
        bind=engine,
        tables=[UserDB.__table__],
    )

    with Session(engine) as session:
        yield session

    engine.dispose()


def test_create_user_with_credentials(db):
    repository = UserRepository()

    user = repository.create(
        db,
        name="Usuario Prueba",
        email="test@aura.com",
        password_hash="hash_de_prueba",
    )

    assert user.id is not None
    assert user.name == "Usuario Prueba"
    assert user.email == "test@aura.com"
    assert user.password_hash == "hash_de_prueba"


def test_get_user_by_email(db):
    repository = UserRepository()

    created = repository.create(
        db,
        name="Usuario Prueba",
        email="test@aura.com",
        password_hash="hash_de_prueba",
    )

    found = repository.get_by_email(
        db,
        email="test@aura.com",
    )

    assert found is not None
    assert found.id == created.id


def test_get_user_by_email_not_found(db):
    repository = UserRepository()

    found = repository.get_by_email(
        db,
        email="noexiste@aura.com",
    )

    assert found is None


def test_reject_duplicate_email(db):
    repository = UserRepository()

    repository.create(
        db,
        email="test@aura.com",
        password_hash="hash_1",
    )

    with pytest.raises(IntegrityError):
        repository.create(
            db,
            email="test@aura.com",
            password_hash="hash_2",
        )

    db.rollback()


def test_create_legacy_user_without_credentials(db):
    repository = UserRepository()

    user = repository.create(
        db,
        name="Usuario Existente",
    )

    assert user.id is not None
    assert user.email is None
    assert user.password_hash is None