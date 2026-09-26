from sqlalchemy.orm import Session

from app.models.user_profile_db import UserProfileDB
from app.repositories.user_profile_repository import (
    UserProfileRepository,
)


class UserProfileService:
    def __init__(
        self,
        repository: UserProfileRepository | None = None,
    ):
        self.repository = (
            repository
            or UserProfileRepository()
        )

    def create_profile(
        self,
        db: Session,
        user_id: int,
    ) -> UserProfileDB:
        return self.repository.create(
            db,
            user_id=user_id,
        )

    def get_profile(
        self,
        db: Session,
        user_id: int,
    ) -> UserProfileDB | None:
        return self.repository.get_by_user_id(
            db,
            user_id=user_id,
        )