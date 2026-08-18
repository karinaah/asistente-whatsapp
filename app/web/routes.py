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
from app.models.assistant_chat import AssistantChatRequest
from app.services.assistant_chat_service import AssistantChatService

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")
assistant_chat_service = AssistantChatService()

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
    workspace: str | None = None,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    tasks = task_service.get_all(db)

    if workspace in {"trabajo", "personal"}:
        tasks = [
            task
            for task in tasks
            if task.workspace.value == workspace
        ]

    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={
            "tasks": tasks,
            "selected_workspace": workspace,
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
    workspace: str = Form("personal"),
    activity_type: str = Form("other"),
    flexibility: str = Form("flexible"),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):

    task = Task(
        title=title,
        estimated_minutes=estimated_minutes,
        priority=priority,
        category=category,
        workspace=workspace,
        activity_type=activity_type,
        flexibility=flexibility,
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
    workspace: str = Form(...),
    activity_type: str = Form(...),
    flexibility: str = Form(...),
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
):
    request = TaskUpdate(
        title=title,
        estimated_minutes=estimated_minutes,
        priority=priority,
        category=category,
        workspace=workspace,
        activity_type=activity_type,
        flexibility=flexibility,
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

@router.get("/web/chat")
def chat_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={},
    )    

@router.post("/web/chat")
def chat_message(
    request: Request,
    message: str = Form(...),
    db: Session = Depends(get_db),
):
    chat_request = AssistantChatRequest(
        message=message,
    )

    response = assistant_chat_service.chat(
        db=db,
        request=chat_request,
    )

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "message": message,
            "answer": response.answer,
        },
    )