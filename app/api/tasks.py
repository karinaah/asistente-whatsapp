from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.task import Task, TaskRequest, TaskResponse, TaskUpdate
from app.config.service_dependencies import (
    get_ai_service,
    get_task_service,
)
from app.services.task_service import TaskService
from app.services.ai_service import AIService

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/extract", response_model=TaskResponse)
def extract_tasks(
    request: TaskRequest,
    ai_service: AIService = Depends(get_ai_service),
) -> TaskResponse:
    tasks = ai_service.extract_tasks(request.text)

    return TaskResponse(tasks=tasks)


@router.get("/", response_model=list[Task])
def get_tasks(
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.get_all(db)


@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.mark_completed(
        db=db,
        task_id=task_id,
    )


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    task_service.delete(
        db=db,
        task_id=task_id,
    )

    return {
        "message": "Tarea eliminada correctamente",
        "task_id": task_id,
    }


@router.get("/{task_id}", response_model=Task)
def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.get_by_id(
        db=db,
        task_id=task_id,
    )


@router.patch("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    request: TaskUpdate,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.update(
        db=db,
        task_id=task_id,
        request=request,
    )

@router.post("/", response_model=Task, status_code=201)
def create_task(
    task: Task,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    return task_service.create(
        db=db,
        task=task,
    )