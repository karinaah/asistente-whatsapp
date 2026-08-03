from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.human_state import HumanState
from app.services.human_state_service import (
    HumanStateService,
)

router = APIRouter(
    prefix="/human-state",
    tags=["Human State"],
)

service = HumanStateService()


@router.post(
    "",
    response_model=HumanState,
)
def save_human_state(
    human_state: HumanState,
    db: Session = Depends(get_db),
) -> HumanState:
    service.save(
        db=db,
        human_state=human_state,
    )

    return human_state


@router.get(
    "/latest",
    response_model=HumanState | None,
)
def get_latest_human_state(
    db: Session = Depends(get_db),
) -> HumanState | None:
    return service.get_latest(db)