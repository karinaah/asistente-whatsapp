from sqlalchemy.orm import Session

from app.models.adaptive_profile import AdaptiveProfile
from app.services.learning_service import LearningService
from app.services.task_execution_service import (
    TaskExecutionService,
)
from app.repositories.adaptive_profile_repository import (
    AdaptiveProfileRepository,
)
from app.services.user_profile_service import (
    UserProfileService,
)


class AdaptiveProfileService:
    def __init__(self) -> None:
        self.repository = (
            AdaptiveProfileRepository()
        )
        self.learning_service = LearningService()
        self.task_execution_service = (
            TaskExecutionService()
        )
        self.user_profile_service = (
            UserProfileService()
        )


    def get(
        self,
        db: Session,
        user_id: int | None = None,
    ) -> AdaptiveProfile | None:
        if user_id is not None:
            return (
                self.user_profile_service
                .build_adaptive_profile(
                    db,
                    user_id=user_id,
                )
            )

        entity = self.repository.get(db)

        if entity is None:
            return None

        return AdaptiveProfile.model_validate(
            entity,
            from_attributes=True,
        )


    def rebuild(
        self,
        db: Session,
        user_id: int | None = None,
    ) -> AdaptiveProfile:
        executions = (
            self.task_execution_service
            .get_all_for_learning(
                db,
                user_id=user_id,
            )
        )

        profile = self.learning_service.build_profile(
            executions
        )

        if user_id is None:
            self.repository.save(
                db=db,
                profile=profile,
            )
        else:
            user_profile = (
                self.user_profile_service
                .get_profile(
                    db,
                    user_id=user_id,
                )
            )

            if user_profile is None:
                self.user_profile_service.create_profile(
                    db,
                    user_id=user_id,
                )

            self.user_profile_service.update_from_adaptive_profile(
                db,
                user_id=user_id,
                adaptive_profile=profile,
            )

        return profile