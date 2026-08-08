from sqlalchemy.orm import Session

from app.models.task_execution import TaskExecution
from app.models.task_execution_db import TaskExecutionDB
from app.repositories.task_execution_repository import (
    TaskExecutionRepository,
)
from app.models.task_execution_response import (
    TaskExecutionResponse,
)

class TaskExecutionService:
    def __init__(self) -> None:
        self.repository = TaskExecutionRepository()

    def save(
        self,
        db: Session,
        execution: TaskExecution,
    ) -> TaskExecutionDB:
        return self.repository.save(
            db=db,
            execution=execution,
        )

    
    def get_all(
        self,
        db: Session,
    ) -> list[TaskExecutionResponse]:
        executions = self.repository.get_all(db)

        return [
            TaskExecutionResponse.model_validate(item)
            for item in executions
        ]    