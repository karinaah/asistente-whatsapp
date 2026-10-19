from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.user_db import UserDB
from app.services.auth_session_service import AuthSessionService
from app.services.user_service import UserService


AUTH_COOKIE_NAME = "aura_auth_token"


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> UserDB:
    """Obtiene el usuario desde una sesión autenticada."""

    token = request.cookies.get(AUTH_COOKIE_NAME)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticación requerida",
        )

    session_service = AuthSessionService()

    auth_session = session_service.validate_session(
        db=db,
        token=token,
    )

    if auth_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida o vencida",
        )

    user = UserService().get_user(
        db=db,
        user_id=auth_session.user_id,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )

    return user