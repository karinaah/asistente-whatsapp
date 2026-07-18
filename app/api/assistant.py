from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import get_assistant_service
from app.models.assistant import AssistantRequest
from app.models.schedule import PlanningResponse
from app.services.assistant_service import AssistantService


router = APIRouter(prefix="/assistant", tags=["Assistant"])


@router.post("/process", response_model=PlanningResponse)
def process_request(
    request: AssistantRequest,
    db: Session = Depends(get_db),
    assistant_service: AssistantService = Depends(get_assistant_service),
) -> PlanningResponse:
    return assistant_service.process(
        db=db,
        request=request,
    )