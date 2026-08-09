from sqlalchemy.orm import Session

from app.models.adaptive_profile import AdaptiveProfile
from app.services.learning_service import LearningService
from app.services.task_execution_service import (
    TaskExecutionService,
)
from app.repositories.adaptive_profile_repository import (
    AdaptiveProfileRepository,
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

    def get(
        self,
        db: Session,
    ) -> AdaptiveProfile | None:
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
    ) -> AdaptiveProfile:
        executions = (
            self.task_execution_service
            .get_all_for_learning(db)
        )

        profile = self.learning_service.build_profile(
            executions
        )

        self.repository.save(
            db=db,
            profile=profile,
        )

        return profile