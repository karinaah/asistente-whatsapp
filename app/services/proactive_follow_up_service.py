from datetime import date

from sqlalchemy.orm import Session

from app.models.proactive_follow_up import (
    FollowUpType,
    ProactiveFollowUp,
)
from app.models.proactive_follow_up_db import (
    ProactiveFollowUpDB,
)
from app.models.task import TaskStatus
from app.repositories.proactive_follow_up_repository import (
    ProactiveFollowUpRepository,
)
from app.services.task_service import TaskService
from app.services.notification_service import (
    NotificationService,
)


class ProactiveFollowUpService:
    def __init__(
        self,
        repository: ProactiveFollowUpRepository | None = None,
        task_service: TaskService | None = None,
        notification_service: NotificationService | None = None,
    ):
        self.repository = (
            repository
            or ProactiveFollowUpRepository()
        )
        self.task_service = (
            task_service
            or TaskService()
        )
        self.notification_service = (
            notification_service
            or NotificationService()
        )

    def check_pending_tasks(
        self,
        db: Session,
        user_id: int,
        target_date: date,
    ) -> ProactiveFollowUpDB | None:
        tasks = self.task_service.get_plannable(
            db,
            user_id=user_id,
        )

        pending_tasks = [
            task
            for task in tasks
            if (
                task.status
                in {
                    TaskStatus.pending,
                    TaskStatus.in_progress,
                }
                and (
                    task.preferred_date is None
                    or task.preferred_date
                    == target_date
                )
            )
        ]

        if not pending_tasks:
            return None

        already_exists = (
            self.repository.exists_for_day(
                db,
                user_id=user_id,
                follow_up_type=(
                    FollowUpType.PENDING_TASKS
                ),
                target_date=target_date,
            )
        )

        if already_exists:
            return None

        follow_up = ProactiveFollowUp(
            user_id=user_id,
            follow_up_type=(
                FollowUpType.PENDING_TASKS
            ),
            title="Tareas pendientes",
            message=(
                f"Todavía tienes "
                f"{len(pending_tasks)} "
                f"tarea(s) pendiente(s) para hoy."
            ),
        )

        created_follow_up = self.repository.create(
            db,
            follow_up,
        )

        self.notification_service.create_from_follow_up(
            db,
            created_follow_up,
        )

        return created_follow_up