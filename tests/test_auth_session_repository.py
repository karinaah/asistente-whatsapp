from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.user_db import UserDB
from app.models.auth_session_db import AuthSessionDB
from app.repositories.auth_session_repository import AuthSessionRepository


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def user(db):
    user = UserDB(name="Usuario de prueba")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_auth_session(db, user):
    repository = AuthSessionRepository()
    expires_at = datetime.utcnow() + timedelta(days=7)

    session = repository.create(
        db=db,
        user_id=user.id,
        token_hash="a" * 64,
        expires_at=expires_at,
    )

    assert session.id is not None
    assert session.user_id == user.id
    assert session.token_hash == "a" * 64
    assert session.expires_at == expires_at
    assert session.revoked_at is None


def test_get_session_by_token_hash(db, user):
    repository = AuthSessionRepository()

    created = repository.create(
        db=db,
        user_id=user.id,
        token_hash="b" * 64,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    found = repository.get_by_token_hash(
        db=db,
        token_hash="b" * 64,
    )

    assert found is not None
    assert found.id == created.id
    assert found.user_id == user.id


def test_get_nonexistent_session_returns_none(db):
    repository = AuthSessionRepository()

    found = repository.get_by_token_hash(
        db=db,
        token_hash="c" * 64,
    )

    assert found is None


def test_revoke_session(db, user):
    repository = AuthSessionRepository()

    session = repository.create(
        db=db,
        user_id=user.id,
        token_hash="d" * 64,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    revoked_at = datetime.utcnow()

    revoked = repository.revoke(
        db=db,
        session=session,
        revoked_at=revoked_at,
    )

    assert revoked.revoked_at == revoked_at

    stored = repository.get_by_token_hash(
        db=db,
        token_hash="d" * 64,
    )

    assert stored.revoked_at == revoked_at


def test_multiple_sessions_for_same_user(db, user):
    repository = AuthSessionRepository()
    expires_at = datetime.utcnow() + timedelta(days=7)

    session_1 = repository.create(
        db=db,
        user_id=user.id,
        token_hash="e" * 64,
        expires_at=expires_at,
    )

    session_2 = repository.create(
        db=db,
        user_id=user.id,
        token_hash="f" * 64,
        expires_at=expires_at,
    )

    assert session_1.id != session_2.id
    assert session_1.user_id == session_2.user_id