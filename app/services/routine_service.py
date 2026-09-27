from sqlalchemy.orm import Session

from app.models.routine import Routine
from app.models.routine_db import RoutineDB
from app.repositories.routine_repository import (
    RoutineRepository,
)


class RoutineService:
    def __init__(
        self,
        repository: RoutineRepository | None = None,
    ):
        self.repository = (
            repository
            or RoutineRepository()
        )

    def create(
        self,
        db: Session,
        routine: Routine,
    ) -> RoutineDB:
        return self.repository.create(
            db,
            routine=routine,
        )

    def get_for_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[RoutineDB]:
        return self.repository.get_by_user_id(
            db,
            user_id=user_id,
        )

    def get_active_for_user(
        self,
        db: Session,
        user_id: int,
    ) -> list[RoutineDB]:
        return (
            self.repository
            .get_active_by_user_id(
                db,
                user_id=user_id,
            )
        )