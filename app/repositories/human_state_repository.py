from sqlalchemy.orm import Session

from app.models.human_state import HumanState
from app.models.human_state_db import HumanStateDB


class HumanStateRepository:
    def save(
        self,
        db: Session,
        human_state: HumanState,
    ) -> HumanStateDB:
        state_db = HumanStateDB(
            energy=(
                human_state.energy.value
                if human_state.energy
                else None
            ),
            focus=(
                human_state.focus.value
                if human_state.focus
                else None
            ),
            stress=(
                human_state.stress.value
                if human_state.stress
                else None
            ),
            available_minutes=(
                human_state.available_minutes
            ),
        )

        db.add(state_db)
        db.commit()
        db.refresh(state_db)

        return state_db

    def get_latest(
        self,
        db: Session,
    ) -> HumanStateDB | None:
        return (
            db.query(HumanStateDB)
            .order_by(
                HumanStateDB.created_at.desc()
            )
            .first()
        )