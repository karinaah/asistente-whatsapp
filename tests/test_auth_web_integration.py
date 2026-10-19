import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.config.dependencies import get_db
from app.main import app

# Importar los modelos para registrar sus tablas en Base.metadata
from app.models.user_db import UserDB
from app.models.auth_session_db import AuthSessionDB


@pytest.fixture
def auth_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    previous_override = app.dependency_overrides.get(get_db)

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as client:
            yield client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override

        engine.dispose()


def test_auth_web_pages_available(auth_client):
    login_response = auth_client.get("/auth/login")
    register_response = auth_client.get("/auth/register")

    assert login_response.status_code == 200
    assert register_response.status_code == 200

    assert 'action="/auth/login/form"' in login_response.text
    assert 'action="/auth/register/form"' in register_response.text

    assert 'name="email"' in login_response.text
    assert 'name="password"' in register_response.text

def test_complete_auth_web_flow(auth_client):
    # 1. Registrar un usuario
    register_response = auth_client.post(
        "/auth/register/form",
        data={
            "name": "Usuario Integracion",
            "email": "integracion@example.com",
            "password": "SecurePassword123!",
        },
        follow_redirects=False,
    )

    assert register_response.status_code == 303
    assert register_response.headers["location"] == "/auth/login"

    # 2. Iniciar sesion
    login_response = auth_client.post(
        "/auth/login/form",
        data={
            "email": "integracion@example.com",
            "password": "SecurePassword123!",
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    assert login_response.headers["location"] == "/web"

    # 3. Comprobar que se genero la cookie
    token = auth_client.cookies.get("aura_auth_token")

    assert token is not None
    assert len(token) > 20

    # 4. Comprobar que la sesion es valida
    from app.services.auth_session_service import AuthSessionService
    from app.config.dependencies import get_db

    db = next(
        app.dependency_overrides[get_db]()
    )

    try:
        session = AuthSessionService().validate_session(
            db=db,
            token=token,
        )

        assert session is not None
    finally:
        db.close()

    # 5. Cerrar sesion
    logout_response = auth_client.post("/auth/logout")

    assert logout_response.status_code == 200
    assert auth_client.cookies.get("aura_auth_token") is None

    # 6. Comprobar que el token anterior ya no funciona
    db = next(
        app.dependency_overrides[get_db]()
    )

    try:
        revoked_session = AuthSessionService().validate_session(
            db=db,
            token=token,
        )

        assert revoked_session is None
    finally:
        db.close()


def test_authenticated_user_can_access_web(auth_client):
    # 1. Registrar usuario
    register_response = auth_client.post(
        "/auth/register/form",
        data={
            "name": "Usuario Web",
            "email": "usuario_web@example.com",
            "password": "SecurePassword123!",
        },
        follow_redirects=False,
    )

    assert register_response.status_code == 303

    # 2. Iniciar sesion
    login_response = auth_client.post(
        "/auth/login/form",
        data={
            "email": "usuario_web@example.com",
            "password": "SecurePassword123!",
        },
        follow_redirects=False,
    )

    assert login_response.status_code == 303
    assert auth_client.cookies.get("aura_auth_token") is not None

    # 3. Acceder a la pagina principal
    response = auth_client.get(
        "/web",
        follow_redirects=False,
    )

    assert response.status_code == 200


def test_legacy_user_cookie_cannot_access_web(auth_client):
    # Simular una cookie antigua sin autenticacion
    auth_client.cookies.set(
        "aura_user_id",
        "1",
    )

    # Comprobar que no existe una sesion autenticada
    assert auth_client.cookies.get("aura_auth_token") is None

    # Intentar acceder a la pagina principal
    response = auth_client.get(
        "/web",
        follow_redirects=False,
    )

    # La cookie antigua no debe permitir el acceso
    assert response.status_code == 401