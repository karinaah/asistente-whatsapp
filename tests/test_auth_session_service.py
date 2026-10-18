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