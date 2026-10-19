from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.user_db import UserDB
from app.config.settings import settings

client = TestClient(app)


def test_register_success():
    user = UserDB(
        id=10,
        email="test@example.com",
        name="Usuario Test",
        password_hash="hashed-password",
    )

    with patch(
        "app.api.auth.UserService"
    ) as service_class:
        service_class.return_value.register_user.return_value = user

        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123!",
                "name": "Usuario Test",
            },
        )

    assert response.status_code == 201
    assert response.json() == {
        "id": 10,
        "email": "test@example.com",
        "name": "Usuario Test",
    }

    assert "password" not in response.json()
    assert "password_hash" not in response.json()


def test_register_duplicate_email():
    with patch(
        "app.api.auth.UserService"
    ) as service_class:
        service_class.return_value.register_user.side_effect = (
            ValueError("El correo ya está registrado")
        )

        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123!",
            },
        )

    assert response.status_code == 409


def test_register_short_password():
    with patch(
        "app.api.auth.UserService"
    ) as service_class:
        service_class.return_value.register_user.side_effect = (
            ValueError(
                "La contraseña debe tener al menos 12 caracteres"
            )
        )

        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",
            },
        )

    assert response.status_code == 422

def test_login_success():
    user = UserDB(
        id=10,
        email="test@example.com",
        name="Usuario Test",
        password_hash="hashed-password",
    )

    with (
        patch("app.api.auth.UserService") as user_service_class,
        patch("app.api.auth.AuthSessionService") as session_service_class,
    ):
        user_service_class.return_value.authenticate_user.return_value = user

        session_service = session_service_class.return_value
        session_service.create_session.return_value = (
            "secure-test-token",
            object(),
        )
        session_service.SESSION_DURATION_DAYS = 7

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "SecurePassword123!",
            },
        )

        user_service_class.return_value.authenticate_user.assert_called_once()
        session_service.create_session.assert_called_once_with(
            db=user_service_class.return_value.authenticate_user.call_args.kwargs.get(
                "db"
            ),
            user_id=10,
        )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Inicio de sesión exitoso",
        "user_id": 10,
    }

    assert response.cookies.get("aura_auth_token") == "secure-test-token"

    cookie_header = response.headers["set-cookie"].lower()

    assert "httponly" in cookie_header
    assert "secure" in cookie_header
    assert "samesite=lax" in cookie_header
    assert "max-age=604800" in cookie_header


def test_login_invalid_credentials():
    with (
        patch("app.api.auth.UserService") as user_service_class,
        patch("app.api.auth.AuthSessionService") as session_service_class,
    ):
        user_service_class.return_value.authenticate_user.return_value = None

        response = client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "incorrect-password",
            },
        )

        session_service_class.assert_not_called()

    assert response.status_code == 401
    assert response.json()["detail"] == (
        "Correo o contraseña incorrectos"
    )
    assert "aura_auth_token" not in response.headers.get(
        "set-cookie", ""
    )


def test_login_missing_password():
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
        },
    )

    assert response.status_code == 422

def test_logout_with_valid_token():
    with patch(
        "app.api.auth.AuthSessionService"
    ) as service_class:
        response = client.post(
            "/auth/logout",
            cookies={
                "aura_auth_token": "valid-test-token",
            },
        )

        service_class.return_value.revoke_session.assert_called_once()

        arguments = (
            service_class.return_value
            .revoke_session.call_args.kwargs
        )

        assert arguments["token"] == "valid-test-token"

    assert response.status_code == 200
    assert response.json() == {
        "message": "Sesión cerrada correctamente",
    }

    cookie_header = response.headers["set-cookie"].lower()

    assert "aura_auth_token=" in cookie_header
    assert "max-age=0" in cookie_header
    assert "httponly" in cookie_header
    assert ("secure" in cookie_header.split("; ")) == settings.cookie_secure


def test_logout_without_token():
    with patch(
        "app.api.auth.AuthSessionService"
    ) as service_class:
        response = client.post(
            "/auth/logout",
        )

        service_class.assert_not_called()

    assert response.status_code == 200
    assert "aura_auth_token=" in response.headers["set-cookie"]


def test_logout_with_unknown_token():
    with patch(
        "app.api.auth.AuthSessionService"
    ) as service_class:
        service_class.return_value.revoke_session.return_value = False

        response = client.post(
            "/auth/logout",
            cookies={
                "aura_auth_token": "unknown-token",
            },
        )

        service_class.return_value.revoke_session.assert_called_once()

    assert response.status_code == 200
    assert "aura_auth_token=" in response.headers["set-cookie"]


def test_login_form_success():
    user = UserDB(
        id=10,
        email="test@example.com",
        name="Usuario Test",
        password_hash="hashed-password",
    )

    with (
        patch("app.api.auth.UserService") as user_service_class,
        patch("app.api.auth.AuthSessionService") as session_service_class,
    ):
        user_service_class.return_value.authenticate_user.return_value = user

        session_service = session_service_class.return_value
        session_service.create_session.return_value = (
            "secure-form-token",
            object(),
        )
        session_service.SESSION_DURATION_DAYS = 7

        response = client.post(
            "/auth/login/form",
            data={
                "email": "test@example.com",
                "password": "SecurePassword123!",
            },
            follow_redirects=False,
        )

        session_service.create_session.assert_called_once()
        assert session_service.create_session.call_args.kwargs["user_id"] == 10

    assert response.status_code == 303
    assert response.headers["location"] == "/web"

    cookie_header = response.headers["set-cookie"].lower()

    assert "aura_auth_token=secure-form-token" in cookie_header
    assert "httponly" in cookie_header
    assert "secure" in cookie_header
    assert "samesite=lax" in cookie_header


def test_login_form_invalid_credentials():
    with (
        patch("app.api.auth.UserService") as user_service_class,
        patch("app.api.auth.AuthSessionService") as session_service_class,
    ):
        user_service_class.return_value.authenticate_user.return_value = None

        response = client.post(
            "/auth/login/form",
            data={
                "email": "test@example.com",
                "password": "incorrect-password",
            },
            follow_redirects=False,
        )

        session_service_class.assert_not_called()

    assert response.status_code == 401
    assert "text/html" in response.headers["content-type"]
    assert "login-error" in response.text
    assert "aura_auth_token=" not in response.headers.get(
        "set-cookie", ""
    )


def test_login_form_missing_password():
    response = client.post(
        "/auth/login/form",
        data={
            "email": "test@example.com",
        },
        follow_redirects=False,
    )

    assert response.status_code == 422

def test_login_cookie_secure_by_environment():
    user = UserDB(
        id=10,
        email="test@example.com",
        name="Usuario Test",
        password_hash="hashed-password",
    )

    original_environment = settings.environment

    try:
        for environment, expected_secure in [
            ("development", False),
            ("production", True),
        ]:
            settings.environment = environment

            with (
                patch("app.api.auth.UserService") as user_service_class,
                patch("app.api.auth.AuthSessionService") as session_service_class,
            ):
                user_service_class.return_value.authenticate_user.return_value = user

                session_service = session_service_class.return_value
                session_service.create_session.return_value = (
                    "test-token",
                    object(),
                )
                session_service.SESSION_DURATION_DAYS = 7

                response = client.post(
                    "/auth/login/form",
                    data={
                        "email": "test@example.com",
                        "password": "SecurePassword123!",
                    },
                    follow_redirects=False,
                )

            assert response.status_code == 303

            cookie_attributes = [
                part.strip().lower()
                for part in response.headers["set-cookie"].split(";")
            ]

            assert ("secure" in cookie_attributes) == expected_secure
            assert "httponly" in cookie_attributes
            assert "samesite=lax" in cookie_attributes

    finally:
        settings.environment = original_environment

def test_register_form_success():
    with patch("app.api.auth.UserService") as service_class:
        response = client.post(
            "/auth/register/form",
            data={
                "name": "Usuario Test",
                "email": "test@example.com",
                "password": "SecurePassword123!",
            },
            follow_redirects=False,
        )

        service_class.return_value.register_user.assert_called_once()

        arguments = (
            service_class.return_value
            .register_user.call_args.kwargs
        )

        assert arguments["email"] == "test@example.com"
        assert arguments["password"] == "SecurePassword123!"
        assert arguments["name"] == "Usuario Test"

    assert response.status_code == 303
    assert response.headers["location"] == "/auth/login"


def test_register_form_duplicate_email():
    with patch("app.api.auth.UserService") as service_class:
        service_class.return_value.register_user.side_effect = ValueError(
            "El correo ya está registrado"
        )

        response = client.post(
            "/auth/register/form",
            data={
                "name": "Usuario Test",
                "email": "test@example.com",
                "password": "SecurePassword123!",
            },
            follow_redirects=False,
        )

    assert response.status_code == 400
    assert "text/html" in response.headers["content-type"]
    assert "login-error" in response.text


def test_register_form_missing_password():
    with patch("app.api.auth.UserService") as service_class:
        response = client.post(
            "/auth/register/form",
            data={
                "name": "Usuario Test",
                "email": "test@example.com",
            },
            follow_redirects=False,
        )

        service_class.return_value.register_user.assert_not_called()

    assert response.status_code == 422