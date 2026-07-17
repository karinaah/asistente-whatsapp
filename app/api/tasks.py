from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.exceptions.task_exceptions import TaskNotFoundError
from app.models.task import Task, TaskRequest, TaskResponse, TaskUpdate
from app.services.mock_ai_service import MockAIService
from app.services.task_service import TaskService


router = APIRouter(prefix="/tasks", tags=["Tasks"])

mock_ai_service = MockAIService()
task_service = TaskService()


@router.post("/extract", response_model=TaskResponse)
def extract_tasks(request: TaskRequest) -> TaskResponse:
    tasks = mock_ai_service.extract_tasks(request.text)

    return TaskResponse(tasks=tasks)


@router.get("/", response_model=list[Task])
def get_tasks(
    db: Session = Depends(get_db),
):
    return task_service.get_all(db)


@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    try:
        return task_service.mark_completed(
            db=db,
            task_id=task_id,
        )
    except TaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    try:
        task_service.delete(
            db=db,
            task_id=task_id,
        )

        return {
            "message": "Tarea eliminada correctamente",
            "task_id": task_id,
        }

    except TaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.get("/{task_id}", response_model=Task)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
):
    try:
        return task_service.get_by_id(
            db=db,
            task_id=task_id,
        )
    except TaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    request: TaskUpdate,
    db: Session = Depends(get_db),
):
    try:
        return task_service.update(
            db=db,
            task_id=task_id,
            request=request,
        )
    except TaskNotFoundError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error