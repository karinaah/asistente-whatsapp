from datetime import date


from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import (
    get_planning_workflow_service,
    get_task_service,
)
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.models.schedule import PlanningFromDBRequest
from app.services.task_service import TaskService
from app.models.task import Task, TaskUpdate
router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/web")
def home(
    request: Request,
    db: Session = Depends(get_db),
    planning_workflow_service: PlanningWorkflowService = Depends(
        get_planning_workflow_service
    ),
):
    today = date.today()
    planning_request = PlanningFromDBRequest()

    plan = planning_workflow_service.create_plan_from_db(
        db=db,
        request=planning_request,
    )

    return templates.TemplateResponse(
        request=request,
        name="today.html",
        context={
            "today": today,
            "plan": plan,
        },

    )

@router.post("/web/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    task_service.mark_completed(
        db=db,
        task_id=task_id,
    )

    return RedirectResponse(
        url="/web",
        status_code=303,
    )

@router.get("/web/tasks")
def tasks_page(
    request: Request,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.get_all(db)

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
        },
    )


@router.post("/web/tasks/{task_id}/delete")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    task_service.delete(
        db=db,
        task_id=task_id,
    )

    return RedirectResponse(
        url="/web/tasks",
        status_code=303,
    )


@router.post("/web/tasks/create")
def create_task_from_web(
    title: str = Form(...),
    estimated_minutes: int = Form(...),
    priority: str = Form("media"),
    category: str = Form("otro"),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    task = Task(
        title=title,
        estimated_minutes=estimated_minutes,
        priority=priority,
        category=category,
    )

    task_service.create(
        db=db,
        task=task,
    )

    return RedirectResponse(
        url="/web/tasks",
        status_code=303,
    )

@router.post("/web/tasks/{task_id}/edit")
def edit_task_from_web(
    task_id: int,
    title: str = Form(...),
    estimated_minutes: int = Form(...),
    priority: str = Form(...),
    category: str = Form(...),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    request = TaskUpdate(
        title=title,
        estimated_minutes=estimated_minutes,
        priority=priority,
        category=category,
    )

    task_service.update(
        db=db,
        task_id=task_id,
        request=request,
    )

    return RedirectResponse(
        url="/web/tasks",
        status_code=303,
    )