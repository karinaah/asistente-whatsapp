from sqlalchemy.orm import Session

from app.models.human_state import (
    EnergyLevel,
    FocusLevel,
    HumanState,
    StressLevel,
)
from app.repositories.human_state_repository import (
    HumanStateRepository,
)


class HumanStateService:
    def __init__(self) -> None:
        self.repository = (
            HumanStateRepository()
        )

    def save(
        self,
        db: Session,
        human_state: HumanState,
    ):
        return self.repository.save(
            db,
            human_state,
        )

    def get_latest(
        self,
        db: Session,
    ) -> HumanState | None:
        state = self.repository.get_latest(db)

        if state is None:
            return None

        return HumanState(
            energy=(
                EnergyLevel(state.energy)
                if state.energy
                else None
            ),
            focus=(
                FocusLevel(state.focus)
                if state.focus
                else None
            ),
            stress=(
                StressLevel(state.stress)
                if state.stress
                else None
            ),
            available_minutes=(
                state.available_minutes
            ),
        )