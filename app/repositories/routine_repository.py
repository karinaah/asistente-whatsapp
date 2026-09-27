from sqlalchemy.orm import Session

from app.models.routine import Routine
from app.models.routine_db import RoutineDB


class RoutineRepository:
    def create(
        self,
        db: Session,
        routine: Routine,
    ) -> RoutineDB:
        db_routine = RoutineDB(
            user_id=routine.user_id,
            title=routine.title,
            description=routine.description,
            weekdays=[
                int(day)
                for day in routine.weekdays
            ],
            preferred_start_time=(
                routine.preferred_start_time
            ),
            estimated_minutes=(
                routine.estimated_minutes
            ),
            category=routine.category.value,
            context=routine.context.value,
            workspace=routine.workspace.value,
            activity_type=routine.activity_type.value,
            active=routine.active,
            created_at=routine.created_at,
            updated_at=routine.updated_at,
        )

        db.add(db_routine)
        db.commit()
        db.refresh(db_routine)

        return db_routine

    def get_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> list[RoutineDB]:
        return (
            db.query(RoutineDB)
            .filter(
                RoutineDB.user_id == user_id
            )
            .order_by(RoutineDB.id)
            .all()
        )

    def get_active_by_user_id(
        self,
        db: Session,
        user_id: int,
    ) -> list[RoutineDB]:
        return (
            db.query(RoutineDB)
            .filter(
                RoutineDB.user_id == user_id,
                RoutineDB.active.is_(True),
            )
            .order_by(RoutineDB.id)
            .all()
        )