import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.user_db import UserDB
from app.services.user_service import UserService
from app.services.password_service import PasswordService


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


def test_register_user_successfully(db):
    service = UserService()

    user = service.register_user(
        db,
        email="test@aura.com",
        password="PasswordSeguro123!",
        name="Usuario Prueba",
    )

    assert user.id is not None
    assert user.email == "test@aura.com"
    assert user.name == "Usuario Prueba"
    assert user.password_hash != "PasswordSeguro123!"

    assert PasswordService().verify_password(
        "PasswordSeguro123!",
        user.password_hash,
    )


def test_register_user_normalizes_email(db):
    service = UserService()

    user = service.register_user(
        db,
        email="  TEST@AURA.COM  ",
        password="PasswordSeguro123!",
    )

    assert user.email == "test@aura.com"


def test_register_user_rejects_duplicate_email(db):
    service = UserService()

    service.register_user(
        db,
        email="test@aura.com",
        password="PasswordSeguro123!",
    )

    with pytest.raises(ValueError, match="ya está registrado"):
        service.register_user(
            db,
            email="TEST@AURA.COM",
            password="OtraPassword123!",
        )


def test_register_user_rejects_short_password(db):
    service = UserService()

    with pytest.raises(ValueError, match="12 caracteres"):
        service.register_user(
            db,
            email="test@aura.com",
            password="12345",
        )


def test_register_user_rejects_invalid_email(db):
    service = UserService()

    with pytest.raises(ValueError, match="inválido"):
        service.register_user(
            db,
            email="correo-invalido",
            password="PasswordSeguro123!",
        )