from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.recommendation import Recommendation
from app.models.schedule import PlanningFromDBRequest
from app.services.recommendation_workflow_service import (
    RecommendationWorkflowService,
)


router = APIRouter(
    prefix="/decision",
    tags=["Decision"],
)

recommendation_workflow_service = (
    RecommendationWorkflowService()
)


@router.post(
    "/recommend",
    response_model=Recommendation | None,
)
def recommend_next_action(
    request: PlanningFromDBRequest,
    db: Session = Depends(get_db),
) -> Recommendation | None:
    return recommendation_workflow_service.recommend(
        db=db,
        request=request,
    )