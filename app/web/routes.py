from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import (
    get_planning_workflow_service,
)
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.models.schedule import PlanningFromDBRequest
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