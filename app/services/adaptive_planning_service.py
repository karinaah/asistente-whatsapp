from sqlalchemy.orm import Session

from app.models.schedule import (
    PlanningRequest,
    PlanningResponse,
)
from app.services.learning_service import LearningService
from app.services.planner_service import PlannerService
from app.services.task_execution_service import (
    TaskExecutionService,
)
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)

class AdaptivePlanningService:
    def __init__(self) -> None:
        self.task_execution_service = (
            TaskExecutionService()
        )
        self.learning_service = LearningService()
        self.planner_service = PlannerService()
        self.adaptive_profile_service = (
            AdaptiveProfileService()
        )

    def create_plan(
        self,
        db: Session,
        request: PlanningRequest,
    ) -> PlanningResponse:
        executions = (
            self.task_execution_service
            .get_all_for_learning(db)
        )

        profile = self.adaptive_profile_service.get(db)

        if profile is None:
            profile = self.adaptive_profile_service.rebuild(db)

        return self.planner_service.create_plan(
            request=request,
            adaptive_profile=profile,
        )