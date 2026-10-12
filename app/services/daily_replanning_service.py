from datetime import datetime
from app.models.schedule import ScheduledTask

from sqlalchemy.orm import Session

from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningRequest,
    PlanningResponse,
    ScheduledTask,
)

from app.services.daily_plan_service import DailyPlanService
from app.services.task_service import TaskService
from app.models.time_block import BlockType, TimeBlock
from app.models.task import Task, TaskFlexibility
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)

class DailyReplanningService:

    def __init__(self) -> None:
        self.daily_plan_service = DailyPlanService()
        self.task_service = TaskService()
        self.planning_workflow_service = PlanningWorkflowService()

    def get_replanning_context(
        self,
        db: Session,
        user_id: int,
        now: datetime,
    ) -> tuple[PlanningResponse, set[int], datetime]:

        plan = self.daily_plan_service.get(
            db=db,
            user_id=user_id,
            plan_date=now.date(),
        )

        if plan is None:
            raise ValueError(
                "No existe una planificación para hoy."
            )

        current_tasks = self.task_service.get_for_user(
            db=db,
            user_id=user_id,
        )

        completed_task_ids = {
            task.id
            for task in current_tasks
            if task.id is not None
            and task.status.value == "completada"
        }

        return plan, completed_task_ids, now


    def separate_tasks(
        self,
        plan: PlanningResponse,
        completed_task_ids: set[int],
        now: datetime,
    ) -> tuple[list[ScheduledTask], list[ScheduledTask]]:

        protected_tasks = []
        pending_tasks = []

        for scheduled in plan.scheduled_tasks:

            is_completed = (
                scheduled.task.id in completed_task_ids
            )

            has_started = (
                scheduled.start_time <= now
            )

            is_fixed = (
                scheduled.task.flexibility
                == TaskFlexibility.fixed
            )

            if is_completed or has_started or is_fixed:
                protected_tasks.append(scheduled)
            else:
                pending_tasks.append(scheduled)

        return protected_tasks, pending_tasks


    def build_protected_blocks(
        self,
        protected_tasks: list[ScheduledTask],
        now: datetime,
    ) -> list[TimeBlock]:

        blocks = []

        for scheduled in protected_tasks:
            if scheduled.end_time <= now:
                continue

            blocks.append(
                TimeBlock(
                    start_time=max(scheduled.start_time, now),
                    end_time=scheduled.end_time,
                    title=scheduled.task.title,
                    block_type=BlockType.TASK,
                )
            )

        return blocks

    def build_event_blocks(
        self,
        plan: PlanningResponse,
        now: datetime,
    ) -> list[TimeBlock]:

        return [
            block.model_copy(deep=True)
            for block in plan.timeline
            if block.block_type == BlockType.EVENT
            and block.end_time > now
        ]

    def collect_pending_tasks(
        self,
        plan: PlanningResponse,
        pending_scheduled_tasks: list[ScheduledTask],
        completed_task_ids: set[int],
    ) -> list[Task]:

        pending_tasks = []
        seen_ids = set()

        candidates = [
            scheduled.task
            for scheduled in pending_scheduled_tasks
        ]

        candidates.extend(plan.unscheduled_tasks)

        for task in candidates:
            if task.id in completed_task_ids:
                continue

            if task.id in seen_ids:
                continue

            pending_tasks.append(task)
            seen_ids.add(task.id)

        return pending_tasks

    def build_replanning_request(
        self,
        plan: PlanningResponse,
        completed_task_ids: set[int],
        now: datetime,
        db: Session | None = None,
        user_id: int | None = None,
    ) -> PlanningRequest:

        protected, pending = self.separate_tasks(
            plan=plan,
            completed_task_ids=completed_task_ids,
            now=now,
        )

        pending_tasks = self.collect_pending_tasks(
            plan=plan,
            pending_scheduled_tasks=pending,
            completed_task_ids=completed_task_ids,
        )

        protected_blocks = self.build_protected_blocks(
            protected_tasks=protected,
            now=now,
        )

        event_blocks = self.build_event_blocks(
            plan=plan,
            now=now,
        )

        request = PlanningFromDBRequest(
            plan_date=now.date(),
            planning_start_time=now.time(),
            busy_blocks=protected_blocks + event_blocks,
        )

        if db is None or user_id is None:
            return PlanningRequest(
                tasks=pending_tasks,
                plan_date=request.plan_date,
                planning_start_time=request.planning_start_time,
                busy_blocks=request.busy_blocks,
            )

        return self.planning_workflow_service.build_planning_request(
            db=db,
            tasks=pending_tasks,
            request=request,
            user_id=user_id,
        )
    

    def generate_proposal(
        self,
        plan: PlanningResponse,
        completed_task_ids: set[int],
        now: datetime,
        db: Session | None = None,
        user_id: int | None = None,
    ) -> PlanningResponse:

        request = self.build_replanning_request(
            plan=plan,
            completed_task_ids=completed_task_ids,
            now=now,
            db=db,
            user_id=user_id,
        )

        protected, _ = self.separate_tasks(
            plan, completed_task_ids, now
        )

        # Crear copias independientes para la propuesta.
        protected = [
            item.model_copy(deep=True)
            for item in protected
        ]

        # Sincronizar el estado de las tareas completadas.
        for scheduled in protected:
            if scheduled.task.id in completed_task_ids:
                scheduled.task.status = type(scheduled.task.status)(
                    "completada"
                )

        adaptive_profile = None

        if db is not None and user_id is not None:
            adaptive_profile = (
                self.planning_workflow_service
                .adaptive_profile_service.get(
                    db,
                    user_id=user_id,
                )
            )

        replanned = (
            self.planning_workflow_service
            .planner_service.create_plan(
                request=request,
                adaptive_profile=adaptive_profile,
            )
        )

        scheduled_tasks = (
            protected + replanned.scheduled_tasks
        )

        scheduled_tasks.sort(
            key=lambda item: item.start_time
        )

        # Conservamos los bloques históricos y los eventos
        # de la planificación confirmada.
        protected_ids = {
            (item.start_time, item.end_time)
            for item in protected
        }

        historical_blocks = [
            block.model_copy(deep=True)
            for block in plan.timeline
            if (
                block.end_time <= now
                or (
                    block.start_time,
                    block.end_time,
                ) in protected_ids
                or block.block_type == BlockType.EVENT
            )
        ]

        # Los eventos originales tienen prioridad sobre las
        # copias que el motor incorpora como bloques ocupados.
        original_events = {
            (
                block.start_time,
                block.end_time,
                block.title,
                block.block_type,
            )
            for block in historical_blocks
            if block.block_type == BlockType.EVENT
        }


        protected_block_keys = {
            (
                block.start_time,
                block.end_time,
                block.title,
                block.block_type,
            )
            for block in request.busy_blocks
            if block.block_type == BlockType.TASK
        }

        timeline = historical_blocks + [
            block
            for block in replanned.timeline
            if (
                block.start_time,
                block.end_time,
                block.title,
                block.block_type,
            ) not in original_events
            and (
                block.start_time,
                block.end_time,
                block.title,
                block.block_type,
            ) not in protected_block_keys
            and not (
                block.block_type == BlockType.EVENT
                and block.end_time <= now
            )
        ]

        # Evitar bloques idénticos duplicados.
        unique_blocks = {}

        for block in timeline:
            key = (
                block.start_time,
                block.end_time,
                block.title,
                block.block_type,
            )
            unique_blocks[key] = block

        timeline = sorted(
            unique_blocks.values(),
            key=lambda block: block.start_time,
        )

        return PlanningResponse(
            scheduled_tasks=scheduled_tasks,
            unscheduled_tasks=replanned.unscheduled_tasks,
            timeline=timeline,
        )    