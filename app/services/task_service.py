from sqlalchemy.orm import Session
from app.models.task import Task, TaskStatus, TaskUpdate
from app.models.task_db import TaskDB
from app.repositories.task_repository import TaskRepository
from app.exceptions.task_exceptions import TaskNotFoundError

class TaskService:
    def __init__(self) -> None:
        self.task_repository = TaskRepository()

    def create(
        self,
        db: Session,
        task: Task,
    ) -> TaskDB:
        return self.task_repository.save(
            db=db,
            task=task,
        )

    def get_all(self, db: Session) -> list[Task]:
        tasks_db = self.task_repository.get_all(db)

        return [
            Task.model_validate(task_db)
            for task_db in tasks_db
        ]

    def get_by_id(
        self,
        db: Session,
        task_id: int,
    ) -> TaskDB:
        task = self.task_repository.get_by_id(
            db=db,
            task_id=task_id,
        )

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    def mark_completed(
        self,
        db: Session,
        task_id: int,
    ) -> TaskDB:
        task = self.task_repository.mark_completed(
            db=db,
            task_id=task_id,
        )

        if task is None:
            raise TaskNotFoundError(task_id)

        return task

    def delete(
        self,
        db: Session,
        task_id: int,
    ) -> None:
        deleted = self.task_repository.delete(
            db=db,
            task_id=task_id,
        )

        if not deleted:
            raise TaskNotFoundError(task_id)

    def update(
        self,
        db: Session,
        task_id: int,
        request: TaskUpdate,
    ) -> TaskDB:
        task = self.task_repository.update(
            db=db,
            task_id=task_id,
            title=request.title,
            description=request.description,
            estimated_minutes=request.estimated_minutes,
            priority=request.priority.value if request.priority else None,
            effort=request.effort.value if request.effort else None,
            focus_demand=(
                request.focus_demand.value
                if request.focus_demand
                else None
            ),
            category=request.category.value if request.category else None,
            context=request.context.value if request.context else None,
            workspace=request.workspace.value if request.workspace else None,
            activity_type=(
                request.activity_type.value
                if request.activity_type
                else None
            ),
            status=request.status.value if request.status else None,
            deadline=request.deadline,
            preferred_date=request.preferred_date,
            preferred_time_of_day=(
                request.preferred_time_of_day.value
                if request.preferred_time_of_day
                else None
            ),
            preferred_start_time=request.preferred_start_time,
            location=request.location,
        )

        if task is None:
            raise TaskNotFoundError(task_id)

        return task
    
    
    def get_plannable(self, db: Session) -> list[Task]:
        tasks = self.get_all(db)

        return [
            task
            for task in tasks
            if task.status in {
                TaskStatus.pending,
                TaskStatus.in_progress,
            }
        ]    