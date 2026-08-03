from datetime import date, time
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.task_db import TaskDB
from app.models.task import TaskStatus

class TaskRepository:
    def save(self, db: Session, task: Task) -> TaskDB:
        task_db = TaskDB(
            title=task.title,
            description=task.description,
            estimated_minutes=task.estimated_minutes,
            priority=task.priority.value,
            effort=task.effort.value,
            category=task.category.value,
            context=task.context.value,
            status=task.status.value,
            deadline=task.deadline,
            preferred_date=task.preferred_date,
            preferred_time_of_day=(
                task.preferred_time_of_day.value
                if task.preferred_time_of_day is not None
                else None
            ),
            preferred_start_time=task.preferred_start_time,
            location=task.location,
        )


        db.add(task_db)
        db.commit()
        db.refresh(task_db)

        return task_db

    def get_all(self, db: Session) -> list[TaskDB]:
        return db.query(TaskDB).order_by(TaskDB.id.desc()).all()

    def get_by_id(
        self,
        db: Session,
        task_id: int,
    ) -> TaskDB | None:
        return (
            db.query(TaskDB)
            .filter(TaskDB.id == task_id)
            .first()
        )    

    def mark_completed(
        self,
        db: Session,
        task_id: int,
    ) -> TaskDB | None:
        task_db = (
            db.query(TaskDB)
            .filter(TaskDB.id == task_id)
            .first()
        )

        if task_db is None:
            return None

        task_db.status = TaskStatus.completed.value

        db.commit()
        db.refresh(task_db)

        return task_db    
    
    def delete(
        self,
        db: Session,
        task_id: int,
    ) -> bool:
        task_db = (
            db.query(TaskDB)
            .filter(TaskDB.id == task_id)
            .first()
        )

        if task_db is None:
            return False

        db.delete(task_db)
        db.commit()

        return True  

    def update(
        self,
        db: Session,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        estimated_minutes: int | None = None,
        priority: str | None = None,
        effort: str | None = None,
        category: str | None = None,
        context: str | None = None,
        status: str | None = None,
        deadline=None,
        preferred_date: date | None = None,
        preferred_time_of_day: str | None = None,
        preferred_start_time: time | None = None,
        location: str | None = None,
    ) -> TaskDB | None:
        task_db = (
            db.query(TaskDB)
            .filter(TaskDB.id == task_id)
            .first()
        )

        if task_db is None:
            return None

        if title is not None:
            task_db.title = title

        if description is not None:
            task_db.description = description

        if estimated_minutes is not None:
            task_db.estimated_minutes = estimated_minutes

        if priority is not None:
            task_db.priority = priority

        if effort is not None:
            task_db.effort = effort

        if category is not None:
            task_db.category = category

        if context is not None:
            task_db.context = context

        if status is not None:
            task_db.status = status

        if deadline is not None:
            task_db.deadline = deadline

        if preferred_date is not None:
            task_db.preferred_date = preferred_date

        if preferred_time_of_day is not None:
            task_db.preferred_time_of_day = preferred_time_of_day

        if preferred_start_time is not None:
            task_db.preferred_start_time = preferred_start_time       

        if location is not None:
            task_db.location = location

        db.commit()
        db.refresh(task_db)

        return task_db      
    