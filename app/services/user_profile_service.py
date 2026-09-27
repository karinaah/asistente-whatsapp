from sqlalchemy.orm import Session

from app.models.adaptive_profile import AdaptiveProfile
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
            .update_duration_multipliers(
                db,
                user_id=user_id,
                work_multiplier=(
                    adaptive_profile
                    .work_duration_multiplier
                ),
                study_multiplier=(
                    adaptive_profile
                    .study_duration_multiplier
                ),
                personal_multiplier=(
                    adaptive_profile
                    .personal_duration_multiplier
                ),
                health_multiplier=(
                    adaptive_profile
                    .health_duration_multiplier
                ),
                other_multiplier=(
                    adaptive_profile
                    .other_duration_multiplier
                ),
                prefers_short_tasks_when_low_energy=(
                    adaptive_profile
                    .prefers_short_tasks_when_low_energy
                ),
                generated_from_executions=(
                    adaptive_profile
                    .generated_from_executions
                ),
                confidence=(
                    adaptive_profile.confidence
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
            generated_from_executions=(
                profile.generated_from_executions
            ),
            work_duration_multiplier=(
                profile.work_duration_multiplier
            ),
            study_duration_multiplier=(
                profile.study_duration_multiplier
            ),
            personal_duration_multiplier=(
                profile.personal_duration_multiplier
            ),
            health_duration_multiplier=(
                profile.health_duration_multiplier
            ),
            other_duration_multiplier=(
                profile.other_duration_multiplier
            ),
            prefers_short_tasks_when_low_energy=(
                profile
                .prefers_short_tasks_when_low_energy
            ),
            confidence=(
                profile.confidence
            ),
        )