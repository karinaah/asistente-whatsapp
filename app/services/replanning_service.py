from datetime import date, time

from sqlalchemy.orm import Session

from app.models.replanning import ReplanningRequest
from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningResponse,
)
from app.models.time_block import TimeBlock
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.models.task import Task

class ReplanningService:
    def __init__(self) -> None:
        self.planning_workflow_service = (
            PlanningWorkflowService()
        )

    def replan_from_time(
        self,
        db: Session,
        plan_date: date,
        planning_start_time: time,
        day_end_hour: int = 20,
        break_minutes: int = 15,
        busy_blocks: list[TimeBlock] | None = None,
    ) -> PlanningResponse:
        tasks = (
            self.planning_workflow_service
            .task_service
            .get_plannable(db)
        )

        tasks_for_day = [
            task
            for task in tasks
            if (
                task.preferred_date is None
                or task.preferred_date == plan_date
            )
        ]

        request = PlanningFromDBRequest(
            plan_date=plan_date,
            planning_start_time=planning_start_time,
            day_end_hour=day_end_hour,
            break_minutes=break_minutes,
            busy_blocks=busy_blocks or [],
        )

        planning_request = (
            self.planning_workflow_service
            .build_planning_request(
                tasks=tasks_for_day,
                request=request,
            )
        )

        adaptive_profile = (
            self.planning_workflow_service
            .adaptive_profile_service
            .get(db)
        )

        return (
            self.planning_workflow_service
            .planner_service
            .create_plan(
                request=planning_request,
                adaptive_profile=adaptive_profile,
            )
        )


    def replan(
        self,
        db: Session,
        request: ReplanningRequest,
    ) -> PlanningResponse:
        if (
            request.active_task_id is None
            or request.remaining_minutes is None
        ):
            return self.replan_from_time(
                db=db,
                plan_date=request.plan_date,
                planning_start_time=request.planning_start_time,
                day_end_hour=request.day_end_hour,
                break_minutes=request.break_minutes,
                busy_blocks=request.busy_blocks,
            )

        tasks = (
            self.planning_workflow_service
            .task_service
            .get_plannable(db)
        )

        adjusted_tasks: list[Task] = []

        for task in tasks:
            if task.id == request.active_task_id:
                adjusted_tasks.append(
                    task.model_copy(
                        update={
                            "estimated_minutes": (
                                request.remaining_minutes
                            )
                        }
                    )
                )
            else:
                adjusted_tasks.append(task)

        planning_request = PlanningFromDBRequest(
            plan_date=request.plan_date,
            planning_start_time=request.planning_start_time,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        direct_request = (
            self.planning_workflow_service
            .build_planning_request(
                tasks=adjusted_tasks,
                request=planning_request,
            )
        )

        adaptive_profile = (
            self.planning_workflow_service
            .adaptive_profile_service
            .get(db)
        )

        return (
            self.planning_workflow_service
            .planner_service
            .create_plan(
                request=direct_request,
                adaptive_profile=adaptive_profile,
            )
        )    