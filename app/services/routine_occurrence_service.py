from datetime import date

from app.models.routine import Routine
from app.models.task import (
    Task,
    TaskFlexibility,
    TaskStatus,
)
from sqlalchemy.orm import Session

from app.models.task_db import TaskDB
from app.repositories.task_repository import TaskRepository
from app.services.routine_service import RoutineService
class RoutineOccurrenceService:
    def occurs_on(
        self,
        routine: Routine,
        target_date: date,
    ) -> bool:
        if not routine.active:
            return False

        return target_date.weekday() in [
            int(day)
            for day in routine.weekdays
        ]

    def create_task(
        self,
        routine: Routine,
        target_date: date,
    ) -> Task | None:
        if not self.occurs_on(
            routine,
            target_date,
        ):
            return None

        return Task(
            user_id=routine.user_id,
            routine_id=routine.id,
            title=routine.title,
            description=routine.description,
            estimated_minutes=routine.estimated_minutes,
            category=routine.category,
            context=routine.context,
            workspace=routine.workspace,
            activity_type=routine.activity_type,
            flexibility=(
                TaskFlexibility.fixed
                if routine.preferred_start_time is not None
                else TaskFlexibility.flexible
            ),
            status=TaskStatus.pending,
            preferred_date=target_date,
            preferred_start_time=(
                routine.preferred_start_time
            ),

        )

    def create_and_save_occurrence(
        self,
        db: Session,
        routine: Routine,
        target_date: date,
        task_repository: TaskRepository | None = None,
    ) -> TaskDB | None:
        if routine.id is None:
            raise ValueError(
                "Routine must be persisted before "
                "creating an occurrence."
            )

        repository = (
            task_repository
            or TaskRepository()
        )

        existing = repository.get_by_routine_and_date(
            db,
            routine_id=routine.id,
            preferred_date=target_date,
        )

        if existing is not None:
            return existing

        task = self.create_task(
            routine,
            target_date,
        )

        if task is None:
            return None

        return repository.save(
            db,
            task,
        )    

    def generate_for_user(
        self,
        db: Session,
        user_id: int,
        target_date: date,
        routine_service: RoutineService | None = None,
        task_repository: TaskRepository | None = None,
    ) -> list[TaskDB]:
        routines_service = (
            routine_service
            or RoutineService()
        )

        repository = (
            task_repository
            or TaskRepository()
        )

        stored_routines = (
            routines_service.get_active_for_user(
                db,
                user_id=user_id,
            )
        )

        generated_tasks: list[TaskDB] = []

        for stored_routine in stored_routines:
            routine = Routine.model_validate(
                stored_routine
            )

            occurrence = (
                self.create_and_save_occurrence(
                    db,
                    routine,
                    target_date,
                    task_repository=repository,
                )
            )

            if occurrence is not None:
                generated_tasks.append(
                    occurrence
                )

        return generated_tasks    