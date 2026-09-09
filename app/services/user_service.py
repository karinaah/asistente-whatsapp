from sqlalchemy.orm import Session

from app.models.user_db import UserDB
from app.repositories.user_repository import UserRepository


class UserService:
    def __init__(
        self,
        repository: UserRepository | None = None,
    ):
        self.repository = (
            repository
            or UserRepository()
        )

    def create_user(
        self,
        db: Session,
        name: str | None = None,
    ) -> UserDB:
        return self.repository.create(
            db,
            name=name,
        )

    def get_user(
        self,
        db: Session,
        user_id: int,
    ) -> UserDB | None:
        return self.repository.get_by_id(
            db,
            user_id=user_id,
        )