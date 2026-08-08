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


class AdaptivePlanningService:
    def __init__(self) -> None:
        self.task_execution_service = (
            TaskExecutionService()
        )
        self.learning_service = LearningService()
        self.planner_service = PlannerService()

    def create_plan(
        self,
        db: Session,
        request: PlanningRequest,
    ) -> PlanningResponse:
        executions = (
            self.task_execution_service
            .get_all_for_learning(db)
        )

        learning_data = (
            self.learning_service.generate_insights(
                executions
            )
        )

        estimation_insights = learning_data[
            "estimation"
        ]

        return self.planner_service.create_plan(
            request=request,
            learning_insights=estimation_insights,
        )