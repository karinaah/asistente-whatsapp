import hashlib
import secrets

from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.auth_session_db import AuthSessionDB
from app.repositories.auth_session_repository import AuthSessionRepository


class AuthSessionService:
    """Gestiona los tokens y las sesiones de autenticación."""

    TOKEN_BYTES = 32
    SESSION_DURATION_DAYS = 7

    def __init__(
        self,
        repository: AuthSessionRepository | None = None,
    ):
        self.repository = repository or AuthSessionRepository()

    def generate_token(self) -> str:
        """Genera un token criptográficamente seguro."""
        return secrets.token_urlsafe(self.TOKEN_BYTES)

    def hash_token(self, token: str) -> str:
        """Calcula el hash SHA-256 del token."""
        return hashlib.sha256(
            token.encode("utf-8")
        ).hexdigest()

    def create_session(
        self,
        db: Session,
        user_id: int,
    ) -> tuple[str, AuthSessionDB]:
        """Crea una sesión y devuelve el token original y su registro."""

        token = self.generate_token()
        token_hash = self.hash_token(token)

        expires_at = datetime.utcnow() + timedelta(
            days=self.SESSION_DURATION_DAYS
        )

        session = self.repository.create(
            db=db,
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        return token, session