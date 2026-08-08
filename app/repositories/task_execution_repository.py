from sqlalchemy.orm import Session

from app.models.task_execution import TaskExecution
from app.models.task_execution_db import (
    TaskExecutionDB,
)


class TaskExecutionRepository:
    def save(
        self,
        db: Session,
        execution: TaskExecution,
    ) -> TaskExecutionDB:
        execution_db = TaskExecutionDB(
            task_id=execution.task_id,
            estimated_minutes=execution.estimated_minutes,
            actual_minutes=execution.actual_minutes,
            started_at=execution.started_at,
            finished_at=execution.finished_at,
            category=execution.category.value,
            context=execution.context.value,
            energy=(
                execution.human_state.energy.value
                if (
                    execution.human_state
                    and execution.human_state.energy
                )
                else None
            ),
            focus=(
                execution.human_state.focus.value
                if (
                    execution.human_state
                    and execution.human_state.focus
                )
                else None
            ),
            stress=(
                execution.human_state.stress.value
                if (
                    execution.human_state
                    and execution.human_state.stress
                )
                else None
            ),
        )

        db.add(execution_db)
        db.commit()
        db.refresh(execution_db)

        return execution_db

    def get_all(
        self,
        db: Session,
    ) -> list[TaskExecutionDB]:
        return (
            db.query(TaskExecutionDB)
            .order_by(
                TaskExecutionDB.created_at.desc()
            )
            .all()
        )