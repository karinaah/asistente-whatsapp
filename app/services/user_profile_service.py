from sqlalchemy.orm import Session

from app.models.user_profile_db import UserProfileDB
from app.repositories.user_profile_repository import (
    UserProfileRepository,
)
from app.models.adaptive_profile import AdaptiveProfile

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

    def update_work_duration_multiplier(
        self,
        db: Session,
        user_id: int,
        multiplier: float,
    ) -> UserProfileDB | None:
        return (
            self.repository
            .update_work_duration_multiplier(
                db,
                user_id=user_id,
                multiplier=multiplier,
            )
        )    

    def update_from_adaptive_profile(
        self,
        db: Session,
        user_id: int,
        adaptive_profile: AdaptiveProfile,
    ) -> UserProfileDB | None:
        return (
            self.repository
            .update_work_duration_multiplier(
                db,
                user_id=user_id,
                multiplier=(
                    adaptive_profile
                    .work_duration_multiplier
                ),
            )
        )    

    def build_adaptive_profile(
        self,
        db: Session,
        user_id: int,
    ) -> AdaptiveProfile | None:
        profile = self.get_profile(
            db,
            user_id=user_id,
        )

        if profile is None:
            return None

        return AdaptiveProfile(
            generated_from_executions=0,
            work_duration_multiplier=(
                profile.work_duration_multiplier
            ),
        )    