from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.services.adaptive_profile_explanation_service import (
    AdaptiveProfileExplanationService,
)

router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
)

service = AdaptiveProfileExplanationService()


@router.get("/adaptive-profile")
def explain_adaptive_profile(
    db: Session = Depends(get_db),
):
    explanation = service.explain(db)

    if explanation is None:
        return {
            "message": (
                "Todavía no existe un perfil "
                "adaptativo para explicar."
            )
        }

    return explanation