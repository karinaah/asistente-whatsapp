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
from app.models.task import Task, TaskFlexibility
from app.services.estimation_adjustment_service import (
    EstimationAdjustmentService,
)
from app.models.adaptive_profile import (
    AdaptiveProfile,
)
from app.models.planning_decision import PlanningDecision
from app.models.planning_reason import (
    PlanningReason,
    PlanningReasonCode,
)

@dataclass
class AvailableSlot:
    start_time: datetime
    end_time: datetime
    preceding_break: TimeBlock | None = None

@dataclass
class PlannerExecutionResult:
    response: PlanningResponse
    decisions: list[PlanningDecision]

class PlannerService:  
    def __init__(self):
        self.task_sorter = TaskSorter()
        self.scoring_engine = ScoringEngine()
        self.estimation_adjustment_service = (
            EstimationAdjustmentService()
        )

    def _plan(
        self,
        request: PlanningRequest,
        adaptive_profile: AdaptiveProfile | None = None,
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

        if adaptive_profile is not None:
            tasks_to_plan = (
                self._apply_profile_adjustments(
                    tasks=tasks_to_plan,
                    profile=adaptive_profile,
                )
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
        planning_decisions: list[PlanningDecision] = []

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

            if task.deadline is not None:
                deadline = task.deadline

                if deadline.tzinfo is not None:
                    deadline = deadline.replace(
                        tzinfo=None
                    )

                task_day_end = min(
                    task_day_end,
                    deadline,
                )


            task_duration = timedelta(
                minutes=task.estimated_minutes
            )


            occupied_blocks = list(busy_blocks)

            occupied_blocks.extend(
                TimeBlock(
                    start_time=scheduled.start_time,
                    end_time=scheduled.end_time,
                    title=scheduled.task.title,
                    block_type=BlockType.TASK,
                )
                for scheduled in scheduled_tasks
            )

            occupied_blocks.sort(
                key=lambda block: block.start_time
            )


            available_slots = self._find_available_slots(
                current_time=task_day_start,
                task_duration=task_duration,
                busy_blocks=occupied_blocks,
                break_minutes=request.break_minutes,
                day_end=task_day_end,
            )


            if (
                task.flexibility == TaskFlexibility.fixed
                and task.preferred_start_time is not None
            ):
                fixed_start = datetime.combine(
                    task_date,
                    task.preferred_start_time,
                )

                available_slots = [
                    slot
                    for slot in available_slots
                    if slot.start_time == fixed_start
                ]


            if (
                task.flexibility == TaskFlexibility.semi_flexible
                and task.preferred_time_of_day is not None
            ):
                preferred_time = task.preferred_time_of_day.value

                preferred_ranges = {
                    "mañana": (5, 12),
                    "tarde": (12, 18),
                    "noche": (18, 24),
                }

                preferred_range = preferred_ranges.get(
                    preferred_time
                )

                if preferred_range is not None:
                    range_start_hour, range_end_hour = (
                        preferred_range
                    )

                    range_start = datetime.combine(
                        task_date,
                        time(hour=range_start_hour),
                    )

                    range_end = datetime.combine(
                        task_date,
                        time.min,
                    ) + timedelta(
                        hours=range_end_hour,
                    )

                    available_slots = [
                        slot
                        for slot in available_slots
                        if (
                            slot.start_time >= range_start
                            and (
                                slot.start_time
                                + task_duration
                            ) <= range_end
                        )
                    ]



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


            scheduled_task = ScheduledTask(
                task=task,
                start_time=task_start,
                end_time=task_end,
            )

            scheduled_tasks.append(scheduled_task)

            reasons: list[PlanningReason] = []

            if (
                task.preferred_start_time is not None
                and task_start.time() == task.preferred_start_time
            ):
                reasons.append(
                    PlanningReason(
                        code=PlanningReasonCode.preferred_start_time,
                        message=(
                            "La tarea fue programada en "
                            "su horario de inicio preferido."
                        ),
                    )
                )

            if adaptive_profile is not None:
                multiplier = self._get_duration_multiplier(
                    task=task,
                    profile=adaptive_profile,
                )

                if multiplier != 1.0:
                    reasons.append(
                        PlanningReason(
                            code=PlanningReasonCode.adaptive_duration,
                            message=(
                                "La duración de la tarea fue ajustada "
                                "según tu historial."
                            ),
                        )
                    )

            planning_decisions.append(
                PlanningDecision(
                    scheduled_task=scheduled_task,
                    reasons=reasons,
                )
            )





        timeline = self._build_timeline(
            busy_blocks=busy_blocks,
            scheduled_tasks=scheduled_tasks,
            generated_breaks=generated_breaks,
            break_minutes=request.break_minutes,
        )


        response = PlanningResponse(
            scheduled_tasks=scheduled_tasks,
            unscheduled_tasks=unscheduled_tasks,
            timeline=timeline,
        )

        return PlannerExecutionResult(
            response=response,
            decisions=planning_decisions,
        )


    def create_plan(
        self,
        request: PlanningRequest,
        adaptive_profile: AdaptiveProfile | None = None,
    ) -> PlanningResponse:
        result = self._plan(
            request=request,
            adaptive_profile=adaptive_profile,
        )

        return result.response


    def explain_plan(
        self,
        request: PlanningRequest,
        adaptive_profile: AdaptiveProfile | None = None,
    ) -> list[PlanningDecision]:
        result = self._plan(
            request=request,
            adaptive_profile=adaptive_profile,
        )

        return result.decisions

    def create_plan_with_decisions(
        self,
        request: PlanningRequest,
        adaptive_profile: AdaptiveProfile | None = None,
    ) -> PlannerExecutionResult:
        return self._plan(
            request=request,
            adaptive_profile=adaptive_profile,
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

                if (
                    block.block_type == BlockType.TASK
                    and break_minutes > 0
                ):
                    slot_end -= timedelta(
                        minutes=break_minutes
                    )


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


            if (
                break_minutes > 0
                and block.block_type != BlockType.TASK
            ):
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
        
    def _apply_profile_adjustments(
        self,
        tasks: list[Task],
        profile: AdaptiveProfile,
    ) -> list[Task]:
        adjusted_tasks: list[Task] = []

        multipliers = {
            "trabajo": profile.work_duration_multiplier,
            "estudio": profile.study_duration_multiplier,
            "personal": profile.personal_duration_multiplier,
            "salud": profile.health_duration_multiplier,
            "otro": profile.other_duration_multiplier,
        }

        for task in tasks:
            multiplier = multipliers.get(
                task.category.value,
                1.0,
            )

            adjusted_minutes = max(
                1,
                round(
                    task.estimated_minutes * multiplier
                ),
            )

            adjusted_tasks.append(
                task.model_copy(
                    update={
                        "estimated_minutes": adjusted_minutes,
                    }
                )
            )

        return adjusted_tasks
    
    def _get_duration_multiplier(
        self,
        task: Task,
        profile: AdaptiveProfile,
    ) -> float:
        multipliers = {
            "trabajo": profile.work_duration_multiplier,
            "estudio": profile.study_duration_multiplier,
            "personal": profile.personal_duration_multiplier,
            "salud": profile.health_duration_multiplier,
            "otro": profile.other_duration_multiplier,
        }

        return multipliers.get(
            task.category.value,
            1.0,
        )    