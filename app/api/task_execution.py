from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.task_execution import TaskExecution
from app.services.task_execution_service import TaskExecutionService
from app.models.task_execution_response import (
    TaskExecutionResponse,
)

router = APIRouter(
    prefix="/task-executions",
    tags=["Task Executions"],
)

service = TaskExecutionService()


@router.post(
    "",
    response_model=TaskExecution,
    status_code=201,
)
def create_task_execution(
    execution: TaskExecution,
    db: Session = Depends(get_db),
) -> TaskExecution:
    service.save(
        db=db,
        execution=execution,
    )

    return execution


@router.get(
    "",
    response_model=list[TaskExecutionResponse],
)
def get_task_executions(
    db: Session = Depends(get_db),
) -> list[TaskExecutionResponse]:
    return service.get_all(db)