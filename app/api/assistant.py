from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.assistant import AssistantRequest
from app.models.schedule import PlanningResponse
from app.services.assistant_service import AssistantService


router = APIRouter(prefix="/assistant", tags=["Assistant"])

assistant_service = AssistantService()


@router.post("/process", response_model=PlanningResponse)
def process_request(
    request: AssistantRequest,
    db: Session = Depends(get_db),
) -> PlanningResponse:
    return assistant_service.process(
        db=db,
        request=request,
    )