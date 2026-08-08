from sqlalchemy.orm import Session

from app.models.task_execution import TaskExecution
from app.models.task_execution_db import TaskExecutionDB
from app.repositories.task_execution_repository import (
    TaskExecutionRepository,
)
from app.models.task_execution_response import (
    TaskExecutionResponse,
)
from app.models.human_state import HumanState

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
    
    def get_all_for_learning(
        self,
        db: Session,
    ) -> list[TaskExecution]:
        executions = self.repository.get_all(db)

        return [
            TaskExecution(
                task_id=item.task_id,
                estimated_minutes=item.estimated_minutes,
                actual_minutes=item.actual_minutes,
                started_at=item.started_at,
                finished_at=item.finished_at,
                category=item.category,
                context=item.context,
                human_state=(
                    HumanState(
                        energy=item.energy,
                        focus=item.focus,
                        stress=item.stress,
                    )
                    if any(
                        [
                            item.energy,
                            item.focus,
                            item.stress,
                        ]
                    )
                    else None
                ),
            )
            for item in executions
        ]    