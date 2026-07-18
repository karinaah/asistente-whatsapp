from sqlalchemy.orm import Session

from app.models.assistant import AssistantRequest
from app.models.schedule import PlanningRequest, PlanningResponse
from app.repositories.task_repository import TaskRepository
from app.services.ai_service import AIService
from app.services.planner_service import PlannerService


class AssistantService:
    def __init__(
        self,
        ai_service: AIService,
        planner_service: PlannerService,
        task_repository: TaskRepository,
    ) -> None:
        self.ai_service = ai_service
        self.planner_service = planner_service
        self.task_repository = task_repository

    def process(
        self,
        db: Session,
        request: AssistantRequest,
    ) -> PlanningResponse:
        tasks = self.ai_service.extract_tasks(request.text)

        saved_tasks = []

        for task in tasks:
            saved_task = self.task_repository.save(db, task)
            saved_tasks.append(saved_task)

        planning_request = PlanningRequest(
            tasks=saved_tasks,
            plan_date=request.plan_date,
            day_start_hour=request.day_start_hour,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        return self.planner_service.create_plan(planning_request)