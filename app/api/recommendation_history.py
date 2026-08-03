from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import (
    get_recommendation_history_service,
)
from app.models.recommendation_history import (
    RecommendationHistory,
)
from app.services.recommendation_history_service import (
    RecommendationHistoryService,
)

router = APIRouter(
    prefix="/recommendation-history",
    tags=["Recommendation History"],
)


@router.get(
    "",
    response_model=list[RecommendationHistory],
)
def get_recommendation_history(
    db: Session = Depends(get_db),
    service: RecommendationHistoryService = Depends(
        get_recommendation_history_service
    ),
):
    return service.get_all(db)