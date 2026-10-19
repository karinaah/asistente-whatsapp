from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config.database import Base
from app.models.user_db import UserDB
from app.models.auth_session_db import AuthSessionDB
from app.services.auth_session_service import AuthSessionService


def test_complete_auth_session_lifecycle():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Crear tablas únicamente en memoria
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)

    try:
        with SessionLocal() as db:
            user = UserDB(name="Usuario de integración")
            db.add(user)
            db.commit()
            db.refresh(user)

            service = AuthSessionService()

            # 1. Crear sesión
            token, session = service.create_session(
                db=db,
                user_id=user.id,
            )

            assert token
            assert session.id is not None
            assert session.user_id == user.id
            assert session.token_hash == service.hash_token(token)
            assert session.token_hash != token

            # 2. Validar sesión
            valid_session = service.validate_session(
                db=db,
                token=token,
            )

            assert valid_session is not None
            assert valid_session.id == session.id

            # 3. Revocar sesión
            revoked = service.revoke_session(
                db=db,
                token=token,
            )

            assert revoked is True

            # 4. Comprobar que ya no es válida
            invalid_session = service.validate_session(
                db=db,
                token=token,
            )

            assert invalid_session is None

            # 5. No permitir una segunda revocación
            assert service.revoke_session(
                db=db,
                token=token,
            ) is False

    finally:
        engine.dispose()