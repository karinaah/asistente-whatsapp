from sqlalchemy.orm import Session

from app.models.task import Task, TaskUpdate
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

    def get_all(self, db: Session) -> list[TaskDB]:
        return self.task_repository.get_all(db)

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
            category=request.category.value if request.category else None,
            context=request.context.value if request.context else None,
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
    
    def create(
        self,
        db: Session,
        task: Task,
    ) -> TaskDB:
        return self.task_repository.save(
            db=db,
            task=task,
        )    