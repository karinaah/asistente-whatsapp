import hashlib

from app.services.auth_session_service import AuthSessionService


def test_generate_token_returns_string():
    service = AuthSessionService()

    token = service.generate_token()

    assert isinstance(token, str)
    assert len(token) > 0


def test_generate_tokens_are_unique():
    service = AuthSessionService()

    tokens = {
        service.generate_token()
        for _ in range(100)
    }

    assert len(tokens) == 100


def test_hash_token_returns_sha256():
    service = AuthSessionService()

    token = "test-token"
    expected_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    assert service.hash_token(token) == expected_hash
    assert len(service.hash_token(token)) == 64


def test_hash_token_is_deterministic():
    service = AuthSessionService()

    token = service.generate_token()

    assert service.hash_token(token) == service.hash_token(token)


def test_different_tokens_have_different_hashes():
    service = AuthSessionService()

    token_1 = service.generate_token()
    token_2 = service.generate_token()

    assert service.hash_token(token_1) != service.hash_token(token_2)


def test_original_token_is_not_stored_as_hash():
    service = AuthSessionService()

    token = service.generate_token()
    token_hash = service.hash_token(token)

    assert token != token_hash
    assert token not in token_hash

from datetime import datetime, timedelta

from unittest.mock import Mock

from app.models.auth_session_db import AuthSessionDB


def test_create_session_stores_hash_not_original_token():
    repository = Mock()
    repository.create.return_value = AuthSessionDB(
        id=1,
        user_id=10,
        token_hash="stored-hash",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    service = AuthSessionService(repository=repository)

    token, session = service.create_session(
        db=Mock(),
        user_id=10,
    )

    assert token
    assert session.user_id == 10

    saved_hash = repository.create.call_args.kwargs["token_hash"]

    assert saved_hash == service.hash_token(token)
    assert saved_hash != token
    assert len(saved_hash) == 64


def test_create_session_assigns_correct_user():
    repository = Mock()
    repository.create.return_value = AuthSessionDB(
        id=1,
        user_id=25,
        token_hash="stored-hash",
        expires_at=datetime.utcnow() + timedelta(days=7),
    )

    service = AuthSessionService(repository=repository)

    service.create_session(
        db=Mock(),
        user_id=25,
    )

    assert repository.create.call_args.kwargs["user_id"] == 25


def test_create_session_expires_after_seven_days():
    repository = Mock()
    repository.create.return_value = Mock()

    service = AuthSessionService(repository=repository)

    before = datetime.utcnow()

    service.create_session(
        db=Mock(),
        user_id=10,
    )

    after = datetime.utcnow()

    expires_at = repository.create.call_args.kwargs["expires_at"]

    assert before + timedelta(days=7) <= expires_at
    assert expires_at <= after + timedelta(days=7)

def test_validate_session_accepts_valid_token():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    token = "valid-token"

    active_session = AuthSessionDB(
        id=1,
        user_id=10,
        token_hash=service.hash_token(token),
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked_at=None,
    )

    repository.get_by_token_hash.return_value = active_session

    result = service.validate_session(db=Mock(), token=token)

    assert result is active_session
    assert (
        repository.get_by_token_hash.call_args.kwargs["token_hash"]
        == service.hash_token(token)
    )


def test_validate_session_rejects_unknown_token():
    repository = Mock()
    repository.get_by_token_hash.return_value = None

    service = AuthSessionService(repository=repository)

    result = service.validate_session(
        db=Mock(),
        token="unknown-token",
    )

    assert result is None


def test_validate_session_rejects_empty_token():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    result = service.validate_session(db=Mock(), token="")

    assert result is None
    repository.get_by_token_hash.assert_not_called()


def test_validate_session_rejects_expired_session():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    expired_session = AuthSessionDB(
        id=1,
        user_id=10,
        token_hash=service.hash_token("expired-token"),
        expires_at=datetime.utcnow() - timedelta(minutes=1),
        revoked_at=None,
    )

    repository.get_by_token_hash.return_value = expired_session

    result = service.validate_session(
        db=Mock(),
        token="expired-token",
    )

    assert result is None


def test_validate_session_rejects_revoked_session():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    revoked_session = AuthSessionDB(
        id=1,
        user_id=10,
        token_hash=service.hash_token("revoked-token"),
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked_at=datetime.utcnow(),
    )

    repository.get_by_token_hash.return_value = revoked_session

    result = service.validate_session(
        db=Mock(),
        token="revoked-token",
    )

    assert result is None

def test_revoke_session_success():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    session = AuthSessionDB(
        id=1,
        user_id=10,
        token_hash=service.hash_token("valid-token"),
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked_at=None,
    )

    repository.get_by_token_hash.return_value = session

    result = service.revoke_session(
        db=Mock(),
        token="valid-token",
    )

    assert result is True
    repository.revoke.assert_called_once()

    arguments = repository.revoke.call_args.kwargs
    assert arguments["session"] is session
    assert isinstance(arguments["revoked_at"], datetime)


def test_revoke_session_unknown_token():
    repository = Mock()
    repository.get_by_token_hash.return_value = None

    service = AuthSessionService(repository=repository)

    result = service.revoke_session(
        db=Mock(),
        token="unknown-token",
    )

    assert result is False
    repository.revoke.assert_not_called()


def test_revoke_session_empty_token():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    result = service.revoke_session(
        db=Mock(),
        token="",
    )

    assert result is False
    repository.get_by_token_hash.assert_not_called()


def test_revoke_session_already_revoked():
    repository = Mock()
    service = AuthSessionService(repository=repository)

    session = AuthSessionDB(
        id=1,
        user_id=10,
        token_hash=service.hash_token("revoked-token"),
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked_at=datetime.utcnow(),
    )

    repository.get_by_token_hash.return_value = session

    result = service.revoke_session(
        db=Mock(),
        token="revoked-token",
    )

    assert result is False
    repository.revoke.assert_not_called()