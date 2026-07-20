from datetime import datetime, time, timedelta

from app.models.schedule import (
    PlanningRequest,
    PlanningResponse,
    ScheduledTask,
)
from app.services.task_sorter import TaskSorter


class PlannerService:
    def __init__(self):
        self.task_sorter = TaskSorter()

    def create_plan(
        self,
        request: PlanningRequest,
    ) -> PlanningResponse:
        current_time = datetime.combine(
            request.plan_date,
            time(hour=request.day_start_hour),
        )

        ordered_tasks = self.task_sorter.sort(request.tasks)

        for block in request.busy_blocks:
            block.start_time = block.start_time.replace(
                tzinfo=None
            )
            block.end_time = block.end_time.replace(
                tzinfo=None
            )

        busy_blocks = sorted(
            request.busy_blocks,
            key=lambda block: block.start_time,
        )

        scheduled_tasks: list[ScheduledTask] = []
        unscheduled_tasks = []

        for task in ordered_tasks:
            task_date = (
                task.preferred_date
                or request.plan_date
            )

            task_day_start = datetime.combine(
                task_date,
                time(hour=request.day_start_hour),
            )

            if task.preferred_start_time is not None:
                preferred_datetime = datetime.combine(
                    task_date,
                    task.preferred_start_time,
                )

                if preferred_datetime > task_day_start:
                    task_day_start = preferred_datetime

            task_day_end = datetime.combine(
                task_date,
                time.min,
            ) + timedelta(
                hours=request.day_end_hour
            )

            if current_time.date() != task_date:
                current_time = task_day_start
            elif current_time < task_day_start:
                current_time = task_day_start

            task_duration = timedelta(
                minutes=task.estimated_minutes
            )

            current_time = self._find_available_time(
                current_time=current_time,
                task_duration=task_duration,
                busy_blocks=busy_blocks,
                break_minutes=request.break_minutes,
            )

            task_end = current_time + task_duration

            if task_end > task_day_end:
                unscheduled_tasks.append(task)
                continue

            scheduled_tasks.append(
                ScheduledTask(
                    task=task,
                    start_time=current_time,
                    end_time=task_end,
                )
            )

            current_time = task_end + timedelta(
                minutes=request.break_minutes
            )

        return PlanningResponse(
            scheduled_tasks=scheduled_tasks,
            unscheduled_tasks=unscheduled_tasks,
        )

    def _find_available_time(
        self,
        current_time: datetime,
        task_duration: timedelta,
        busy_blocks: list,
        break_minutes: int,
    ) -> datetime:
        for block in busy_blocks:
            task_end = current_time + task_duration

            has_collision = (
                current_time < block.end_time
                and task_end > block.start_time
            )

            if has_collision:
                current_time = block.end_time + timedelta(
                    minutes=break_minutes
                )

        return current_time