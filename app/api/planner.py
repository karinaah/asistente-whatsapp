from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import get_task_service
from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningRequest,
    PlanningResponse,
)
from app.services.planner_service import PlannerService
from app.services.task_service import TaskService

router = APIRouter(prefix="/planner", tags=["Planner"])

planner_service = PlannerService()


@router.post("/create", response_model=PlanningResponse)
def create_plan(request: PlanningRequest) -> PlanningResponse:
    return planner_service.create_plan(request)


@router.post("/create-from-db", response_model=PlanningResponse)
def create_plan_from_db(
    request: PlanningFromDBRequest,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
) -> PlanningResponse:
    tasks = task_service.get_all(db)

    planning_request = PlanningRequest(
        tasks=tasks,
        plan_date=request.plan_date,
        day_start_hour=request.day_start_hour,
        day_end_hour=request.day_end_hour,
        break_minutes=request.break_minutes,
        busy_blocks=request.busy_blocks,
        context=request.context,
    )

    return planner_service.create_plan(planning_request)