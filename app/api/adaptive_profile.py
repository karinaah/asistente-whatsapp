from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.adaptive_profile import AdaptiveProfile
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)

router = APIRouter(
    prefix="/adaptive-profile",
    tags=["Adaptive Profile"],
)

service = AdaptiveProfileService()


@router.get(
    "",
    response_model=AdaptiveProfile | None,
)
def get_adaptive_profile(
    db: Session = Depends(get_db),
) -> AdaptiveProfile | None:
    return service.get(db)


@router.post(
    "/rebuild",
    response_model=AdaptiveProfile,
)
def rebuild_adaptive_profile(
    db: Session = Depends(get_db),
) -> AdaptiveProfile:
    return service.rebuild(db)