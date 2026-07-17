from sqlalchemy.orm import Session

from app.models.assistant import AssistantRequest
from app.models.schedule import PlanningRequest, PlanningResponse
from app.repositories.task_repository import TaskRepository
from app.services.mock_ai_service import MockAIService
from app.services.planner_service import PlannerService


class AssistantService:
    def __init__(self) -> None:
        self.ai_service = MockAIService()
        self.planner_service = PlannerService()
        self.task_repository = TaskRepository()

    def process(
        self,
        db: Session,
        request: AssistantRequest,
    ) -> PlanningResponse:
        tasks = self.ai_service.extract_tasks(request.text)

        for task in tasks:
            self.task_repository.save(db, task)

        planning_request = PlanningRequest(
            tasks=tasks,
            plan_date=request.plan_date,
            day_start_hour=request.day_start_hour,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        return self.planner_service.create_plan(planning_request)