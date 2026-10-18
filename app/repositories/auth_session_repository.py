from datetime import datetime

from sqlalchemy.orm import Session

from app.models.auth_session_db import AuthSessionDB


class AuthSessionRepository:

    def create(
        self,
        db: Session,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> AuthSessionDB:

        session = AuthSessionDB(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        db.add(session)
        db.commit()
        db.refresh(session)

        return session

    def get_by_token_hash(
        self,
        db: Session,
        token_hash: str,
    ) -> AuthSessionDB | None:

        return (
            db.query(AuthSessionDB)
            .filter(AuthSessionDB.token_hash == token_hash)
            .first()
        )

    def revoke(
        self,
        db: Session,
        session: AuthSessionDB,
        revoked_at: datetime,
    ) -> AuthSessionDB:

        session.revoked_at = revoked_at

        db.commit()
        db.refresh(session)

        return session