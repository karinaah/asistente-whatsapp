from sqlalchemy.orm import Session

from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningRequest,
    PlanningResponse,
)
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from app.services.planner_service import PlannerService
from app.services.task_service import TaskService


class PlanningWorkflowService:
    def __init__(self) -> None:
        self.task_service = TaskService()
        self.planner_service = PlannerService()
        self.adaptive_profile_service = (
            AdaptiveProfileService()
        )

    def create_plan_from_db(
        self,
        db: Session,
        request: PlanningFromDBRequest,
    ) -> PlanningResponse:
        tasks = self.task_service.get_plannable(db)

        planning_request = self.build_planning_request(
            tasks=tasks,
            request=request,
        )

        adaptive_profile = (
            self.adaptive_profile_service.get(db)
        )

        return self.planner_service.create_plan(
            request=planning_request,
            adaptive_profile=adaptive_profile,
        )


    def build_planning_request(
        self,
        tasks,
        request: PlanningFromDBRequest,
    ) -> PlanningRequest:
        return PlanningRequest(
            tasks=tasks,
            plan_date=request.plan_date,
            day_start_hour=request.day_start_hour,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
            context=request.context,
        )    