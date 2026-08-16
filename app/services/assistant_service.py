from sqlalchemy.orm import Session

from app.models.assistant import AssistantRequest
from app.models.schedule import PlanningRequest, PlanningResponse
from app.repositories.task_repository import TaskRepository
from app.services.ai_service import AIService
from app.services.planner_service import PlannerService
from app.services.task_analyzer_service import TaskAnalyzerService
from app.services.task_creation_workflow_service import (
    TaskCreationWorkflowService,
)


class AssistantService:
    def __init__(
        self,
        ai_service: AIService,
        planner_service: PlannerService,
        task_repository: TaskRepository,
        task_analyzer_service: TaskAnalyzerService,
    ) -> None:
        self.ai_service = ai_service
        self.planner_service = planner_service
        self.task_repository = task_repository
        self.task_analyzer_service = task_analyzer_service

        self.task_creation_workflow_service = (
            TaskCreationWorkflowService(
                ai_service=ai_service,
                task_analyzer_service=task_analyzer_service,
                task_repository=task_repository,
            )
        )

    def process(
        self,
        db: Session,
        request: AssistantRequest,
    ) -> PlanningResponse:
        saved_tasks = (
            self.task_creation_workflow_service
            .create_from_text(
                db=db,
                text=request.text,
                reference_date=request.plan_date,
            )
        )



        planning_request = PlanningRequest(
            tasks=saved_tasks,
            plan_date=request.plan_date,
            day_start_hour=request.day_start_hour,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        return self.planner_service.create_plan(
            planning_request
        )