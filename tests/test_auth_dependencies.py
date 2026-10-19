from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest
from fastapi import HTTPException
from starlette.requests import Request

from app.config.auth_dependencies import get_current_user
from app.models.auth_session_db import AuthSessionDB
from app.models.user_db import UserDB


def make_request(token=None):
    headers = []

    if token is not None:
        headers.append(
            (
                b"cookie",
                f"aura_auth_token={token}".encode(),
            )
        )

    return Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/web",
            "headers": headers,
            "query_string": b"",
        }
    )


def make_auth_session(revoked_at=None):
    return AuthSessionDB(
        id=1,
        user_id=10,
        token_hash="hashed-token",
        expires_at=datetime.utcnow() + timedelta(days=7),
        revoked_at=revoked_at,
    )


def test_get_current_user_without_cookie():
    request = make_request()
    db = Mock()

    with pytest.raises(HTTPException) as error:
        get_current_user(request=request, db=db)

    assert error.value.status_code == 401


def test_get_current_user_invalid_token():
    request = make_request("invalid-token")
    db = Mock()

    with patch(
        "app.config.auth_dependencies.AuthSessionService"
    ) as service_class:
        service_class.return_value.validate_session.return_value = None

        with pytest.raises(HTTPException) as error:
            get_current_user(request=request, db=db)

    assert error.value.status_code == 401


def test_get_current_user_missing_user():
    request = make_request("valid-token")
    db = Mock()

    with (
        patch(
            "app.config.auth_dependencies.AuthSessionService"
        ) as session_class,
        patch(
            "app.config.auth_dependencies.UserService"
        ) as user_class,
    ):
        session_class.return_value.validate_session.return_value = (
            make_auth_session()
        )
        user_class.return_value.get_user.return_value = None

        with pytest.raises(HTTPException) as error:
            get_current_user(request=request, db=db)

    assert error.value.status_code == 401


def test_get_current_user_valid_session():
    request = make_request("valid-token")
    db = Mock()
    user = UserDB(id=10)

    with (
        patch(
            "app.config.auth_dependencies.AuthSessionService"
        ) as session_class,
        patch(
            "app.config.auth_dependencies.UserService"
        ) as user_class,
    ):
        session_class.return_value.validate_session.return_value = (
            make_auth_session()
        )
        user_class.return_value.get_user.return_value = user

        result = get_current_user(
            request=request,
            db=db,
        )

        session_class.return_value.validate_session.assert_called_once_with(
            db=db,
            token="valid-token",
        )
        user_class.return_value.get_user.assert_called_once_with(
            db=db,
            user_id=10,
        )

    assert result is user


def test_get_current_user_revoked_session():
    request = make_request("revoked-token")
    db = Mock()

    # El servicio devuelve None cuando una sesión está revocada.
    with patch(
        "app.config.auth_dependencies.AuthSessionService"
    ) as service_class:
        service_class.return_value.validate_session.return_value = None

        with pytest.raises(HTTPException) as error:
            get_current_user(request=request, db=db)

    assert error.value.status_code == 401