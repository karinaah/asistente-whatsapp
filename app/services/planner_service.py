from dataclasses import dataclass
from datetime import datetime, time, timedelta

from app.models.schedule import (
    PlanningRequest,
    PlanningResponse,
    ScheduledTask,
)
from app.models.time_block import BlockType, TimeBlock
from app.services.task_sorter import TaskSorter
from app.services.scoring_engine import ScoringEngine
from app.models.learning_insight import LearningInsight
from app.models.task import Task
from app.services.estimation_adjustment_service import (
    EstimationAdjustmentService,
)


@dataclass
class AvailableSlot:
    start_time: datetime
    end_time: datetime
    preceding_break: TimeBlock | None = None


class PlannerService:  
    def __init__(self):
        self.task_sorter = TaskSorter()
        self.scoring_engine = ScoringEngine()
        self.estimation_adjustment_service = (
            EstimationAdjustmentService()
        )

    def create_plan(
        self,
        request: PlanningRequest,
        learning_insights: list[LearningInsight] | None = None,
    ) -> PlanningResponse:        
        current_time = datetime.combine(
            request.plan_date,
            time(hour=request.day_start_hour),
        )


        tasks_to_plan = request.tasks

        if request.context is not None:
            tasks_to_plan = [
                task
                for task in request.tasks
                if task.context == request.context
            ]

        if learning_insights:
            tasks_to_plan = self._apply_estimation_adjustments(
                tasks=tasks_to_plan,
                insights=learning_insights,
            )

        ordered_tasks = self.task_sorter.sort(tasks_to_plan)



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

            available_slots = self._find_available_slots(
                current_time=current_time,
                task_duration=task_duration,
                busy_blocks=busy_blocks,
                break_minutes=request.break_minutes,
                day_end=task_day_end,
            )

            if not available_slots:
                unscheduled_tasks.append(task)
                continue

            selected_slot = self._choose_best_slot(
                available_slots=available_slots,
                task=task,
            )                       

            task_start = selected_slot.start_time
            task_end = task_start + task_duration

            if task_end > task_day_end:
                unscheduled_tasks.append(task)
                continue

            if selected_slot.preceding_break is not None:
                generated_breaks.append(
                    selected_slot.preceding_break
                )

            scheduled_tasks.append(
                ScheduledTask(
                    task=task,
                    start_time=task_start,
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

    def _choose_best_slot(
        self,
        available_slots: list[AvailableSlot],
        task,
    ) -> AvailableSlot:
        earliest_start = min(
            slot.start_time
            for slot in available_slots
        )

        return max(
            available_slots,
            key=lambda slot: self.scoring_engine.score(
                slot=slot,
                task=task,
                earliest_start=earliest_start,
                available_slots=available_slots,
            ),
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

    def _find_available_slots(
        self,
        current_time: datetime,
        task_duration: timedelta,
        busy_blocks: list[TimeBlock],
        break_minutes: int,
        day_end: datetime,
    ) -> list[AvailableSlot]:
        available_slots: list[AvailableSlot] = []

        slot_start = current_time
        preceding_break: TimeBlock | None = None

        for block in busy_blocks:
            if block.end_time <= slot_start:
                continue

            has_free_time_before_block = (
                slot_start < block.start_time
            )

            if has_free_time_before_block:
                slot_end = block.start_time

                task_fits = (
                    slot_start + task_duration
                    <= slot_end
                )

                if task_fits:
                    available_slots.append(
                        AvailableSlot(
                            start_time=slot_start,
                            end_time=slot_end,
                            preceding_break=preceding_break,
                        )
                    )

            if block.end_time >= day_end:
                slot_start = day_end
                preceding_break = None
                break

            slot_start = block.end_time + timedelta(
                minutes=break_minutes
            )

            if break_minutes > 0:
                preceding_break = TimeBlock(
                    start_time=block.end_time,
                    end_time=slot_start,
                    title="Descanso",
                    block_type=BlockType.BREAK,
                )
            else:
                preceding_break = None

        task_fits_at_end = (
            slot_start + task_duration
            <= day_end
        )

        if task_fits_at_end:
            available_slots.append(
                AvailableSlot(
                    start_time=slot_start,
                    end_time=day_end,
                    preceding_break=preceding_break,
                )
            )

        return available_slots
    
    def _apply_estimation_adjustments(
        self,
        tasks: list[Task],
        insights: list[LearningInsight],
    ) -> list[Task]:
        insights_by_category = {
            insight.category: insight
            for insight in insights
        }

        adjusted_tasks: list[Task] = []

        for task in tasks:
            insight = insights_by_category.get(
                task.category.value
            )

            if insight is None:
                adjusted_tasks.append(task)
                continue

            adjusted_minutes = (
                self.estimation_adjustment_service.adjust(
                    estimated_minutes=task.estimated_minutes,
                    insight=insight,
                )
            )

            adjusted_task = task.model_copy(
                update={
                    "estimated_minutes": adjusted_minutes,
                }
            )

            adjusted_tasks.append(adjusted_task)

        return adjusted_tasks