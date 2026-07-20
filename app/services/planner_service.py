from datetime import datetime, time, timedelta

from app.models.schedule import (
    PlanningRequest,
    PlanningResponse,
    ScheduledTask,
)
from app.models.time_block import BlockType, TimeBlock
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
        generated_breaks: list[TimeBlock] = []

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

            current_time, collision_break = (
                self._find_available_time(
                    current_time=current_time,
                    task_duration=task_duration,
                    busy_blocks=busy_blocks,
                    break_minutes=request.break_minutes,
                )
            )

            task_end = current_time + task_duration

            if task_end > task_day_end:
                unscheduled_tasks.append(task)
                continue

            if collision_break is not None:
                generated_breaks.append(collision_break)

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

            timeline = self._build_timeline(
                busy_blocks=busy_blocks,
                scheduled_tasks=scheduled_tasks,
                generated_breaks=generated_breaks,
                break_minutes=request.break_minutes,
            )

        return PlanningResponse(
            scheduled_tasks=scheduled_tasks,
            unscheduled_tasks=unscheduled_tasks,
            timeline=timeline,
        )

    def _build_timeline(
        self,
        busy_blocks: list[TimeBlock],
        scheduled_tasks: list[ScheduledTask],
        generated_breaks: list[TimeBlock],
        break_minutes: int,
    ) -> list[TimeBlock]:
        timeline = list(busy_blocks)
        timeline.extend(generated_breaks)

        ordered_scheduled_tasks = sorted(
            scheduled_tasks,
            key=lambda scheduled_task: scheduled_task.start_time,
        )

        for index, scheduled_task in enumerate(
            ordered_scheduled_tasks
        ):
            timeline.append(
                TimeBlock(
                    start_time=scheduled_task.start_time,
                    end_time=scheduled_task.end_time,
                    title=scheduled_task.task.title,
                    block_type=BlockType.TASK,
                )
            )

            is_last_task = (
                index == len(ordered_scheduled_tasks) - 1
            )

            if is_last_task or break_minutes <= 0:
                continue

            next_scheduled_task = ordered_scheduled_tasks[
                index + 1
            ]

            expected_next_start = (
                scheduled_task.end_time
                + timedelta(minutes=break_minutes)
            )

            has_planned_break = (
                next_scheduled_task.start_time
                == expected_next_start
            )

            if has_planned_break:
                timeline.append(
                    TimeBlock(
                        start_time=scheduled_task.end_time,
                        end_time=expected_next_start,
                        title="Descanso",
                        block_type=BlockType.BREAK,
                    )
                )

        timeline.sort(
            key=lambda block: block.start_time
        )

        return timeline


    def _find_available_time(
        self,
        current_time: datetime,
        task_duration: timedelta,
        busy_blocks: list[TimeBlock],
        break_minutes: int,
    ) -> tuple[datetime, TimeBlock | None]:
        last_collision_end: datetime | None = None

        for block in busy_blocks:
            task_end = current_time + task_duration

            has_collision = (
                current_time < block.end_time
                and task_end > block.start_time
            )

            if has_collision:
                last_collision_end = block.end_time

                current_time = block.end_time + timedelta(
                    minutes=break_minutes
                )

        collision_break = None

        if (
            last_collision_end is not None
            and break_minutes > 0
        ):
            collision_break = TimeBlock(
                start_time=last_collision_end,
                end_time=last_collision_end + timedelta(
                    minutes=break_minutes
                ),
                title="Descanso",
                block_type=BlockType.BREAK,
            )

        return current_time, collision_break