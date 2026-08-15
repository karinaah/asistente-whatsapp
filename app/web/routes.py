from datetime import date


from fastapi import APIRouter, Depends, Request
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