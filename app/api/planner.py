from fastapi import APIRouter

from app.models.schedule import PlanningRequest, PlanningResponse
from app.services.planner_service import PlannerService

router = APIRouter(prefix="/planner", tags=["Planner"])

planner_service = PlannerService()


@router.post("/create", response_model=PlanningResponse)
def create_plan(request: PlanningRequest) -> PlanningResponse:
    return planner_service.create_plan(request)