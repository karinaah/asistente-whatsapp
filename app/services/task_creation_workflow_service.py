from datetime import date

from sqlalchemy.orm import Session

from app.models.task import Task
from app.repositories.task_repository import TaskRepository
from app.services.ai_service import AIService
from app.services.task_analyzer_service import TaskAnalyzerService


class TaskCreationWorkflowService:
    def __init__(
        self,
        ai_service: AIService,
        task_analyzer_service: TaskAnalyzerService,
        task_repository: TaskRepository,
    ) -> None:
        self.ai_service = ai_service
        self.task_analyzer_service = task_analyzer_service
        self.task_repository = task_repository

    def create_from_text(
        self,
        db: Session,
        text: str,
        reference_date: date,
    ) -> list[Task]:
        extracted_tasks = self.ai_service.extract_tasks(
            text
        )

        analyzed_tasks = self.task_analyzer_service.analyze(
            extracted_tasks,
            reference_date=reference_date,
        )

        saved_tasks = []

        for task in analyzed_tasks:
            saved_task = self.task_repository.save(
                db=db,
                task=task,
            )

            saved_tasks.append(
                Task.model_validate(saved_task)
            )

        return saved_tasks