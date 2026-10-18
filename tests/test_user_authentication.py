import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.user_db import UserDB
from app.services.user_service import UserService


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


def test_authenticate_valid_credentials(db):
    service = UserService()

    created = service.register_user(
        db,
        email="test@aura.com",
        password="PasswordSeguro123!",
        name="Usuario Prueba",
    )

    authenticated = service.authenticate_user(
        db,
        email="test@aura.com",
        password="PasswordSeguro123!",
    )

    assert authenticated is not None
    assert authenticated.id == created.id


def test_authenticate_wrong_password(db):
    service = UserService()

    service.register_user(
        db,
        email="test@aura.com",
        password="PasswordSeguro123!",
    )

    authenticated = service.authenticate_user(
        db,
        email="test@aura.com",
        password="ClaveIncorrecta123!",
    )

    assert authenticated is None


def test_authenticate_unknown_email(db):
    service = UserService()

    authenticated = service.authenticate_user(
        db,
        email="noexiste@aura.com",
        password="PasswordSeguro123!",
    )

    assert authenticated is None


def test_authenticate_normalized_email(db):
    service = UserService()

    created = service.register_user(
        db,
        email="test@aura.com",
        password="PasswordSeguro123!",
    )

    authenticated = service.authenticate_user(
        db,
        email="  TEST@AURA.COM  ",
        password="PasswordSeguro123!",
    )

    assert authenticated is not None
    assert authenticated.id == created.id


def test_authenticate_legacy_user_without_password(db):
    service = UserService()

    legacy_user = service.create_user(
        db,
        name="Usuario Antiguo",
    )

    assert legacy_user.password_hash is None

    authenticated = service.authenticate_user(
        db,
        email="antiguo@aura.com",
        password="PasswordSeguro123!",
    )

    assert authenticated is None