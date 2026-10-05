from datetime import date, timedelta

from app.models.task import (
    Task,
    TaskFlexibility,
)
from app.services.task_sorter import TaskSorter


class DailyTaskSelectionService:
    DAILY_LOAD_TARGET_MINUTES = 480
    MIN_FLEXIBLE_BUDGET_MINUTES = 60

    def __init__(self) -> None:
        self.task_sorter = TaskSorter()

    def select_for_day(
        self,
        tasks: list[Task],
        plan_date: date,
    ) -> list[Task]:
        ordered_tasks = self.task_sorter.sort(tasks)
        urgent_deadline_date = (
            plan_date + timedelta(days=1)
        )
        committed_tasks = [
            task
            for task in ordered_tasks
            if (
                task.flexibility
                != TaskFlexibility.flexible
                or task.preferred_date == plan_date
                or (
                    task.deadline is not None
                    and task.deadline.date()
                    <= urgent_deadline_date
                )
            )
        ]

        flexible_backlog = [
            task
            for task in ordered_tasks
            if (
                task.flexibility
                == TaskFlexibility.flexible
                and task.preferred_date is None
                and (
                    task.deadline is None
                    or task.deadline.date()
                    > urgent_deadline_date
                )
            )
        ]

        committed_minutes = sum(
            task.estimated_minutes
            for task in committed_tasks
        )

        flexible_budget = max(
            self.MIN_FLEXIBLE_BUDGET_MINUTES,
            self.DAILY_LOAD_TARGET_MINUTES
            - committed_minutes,
        )

        selected_flexible_tasks: list[Task] = []
        used_flexible_minutes = 0

        for task in flexible_backlog:
            if (
                used_flexible_minutes
                + task.estimated_minutes
                > flexible_budget
            ):
                continue

            selected_flexible_tasks.append(task)
            used_flexible_minutes += task.estimated_minutes

        return (
            committed_tasks
            + selected_flexible_tasks
        )