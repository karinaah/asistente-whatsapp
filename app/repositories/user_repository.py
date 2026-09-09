from sqlalchemy.orm import Session

from app.models.user_db import UserDB


class UserRepository:
    def create(
        self,
        db: Session,
        name: str | None = None,
    ) -> UserDB:
        user = UserDB(
            name=name,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    def get_by_id(
        self,
        db: Session,
        user_id: int,
    ) -> UserDB | None:
        return (
            db.query(UserDB)
            .filter(UserDB.id == user_id)
            .first()
        )