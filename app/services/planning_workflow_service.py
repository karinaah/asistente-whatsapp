from sqlalchemy.orm import Session

from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningRequest,
    PlanningResponse,
)
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from app.services.planner_service import PlannerService
from app.services.task_service import TaskService
from app.models.planning_decision import (
    PlanningDecision,
)
from app.services.routine_occurrence_service import (
    RoutineOccurrenceService,
)
from app.services.recurring_availability_service import (
    RecurringAvailabilityService,
)
from app.services.calendar_service import CalendarService
class PlanningWorkflowService:
    def __init__(self) -> None:
        self.task_service = TaskService()
        self.planner_service = PlannerService()
        self.adaptive_profile_service = (
            AdaptiveProfileService()
        )
        self.routine_occurrence_service = (
            RoutineOccurrenceService()
        )
        self.recurring_availability_service = (
            RecurringAvailabilityService()
        )
        self.calendar_service = CalendarService()
    def generate_routines_for_plan(
        self,
        db: Session,
        request: PlanningFromDBRequest,
        user_id: int | None,
    ) -> None:
        if user_id is None:
            return

        self.routine_occurrence_service.generate_for_user(
            db,
            user_id=user_id,
            target_date=request.plan_date,
        )
        
    def create_plan_from_db(
        self,
        db: Session,
        request: PlanningFromDBRequest,
        user_id: int | None = None,
    ) -> PlanningResponse:
        self.generate_routines_for_plan(
            db,
            request=request,
            user_id=user_id,
        )


        tasks = self.task_service.get_plannable(
            db,
            user_id=user_id,
        )
        tasks = [
            task
            for task in tasks
            if (
                task.preferred_date is None
                or task.preferred_date == request.plan_date
            )
        ]


        planning_request = self.build_planning_request(
            db=db,
            tasks=tasks,
            request=request,
            user_id=user_id,
        )        

        adaptive_profile = (
            self.adaptive_profile_service.get(
                db,
                user_id=user_id,
            )
        )

        return self.planner_service.create_plan(
            request=planning_request,
            adaptive_profile=adaptive_profile,
        )


    def build_planning_request(
        self,
        db: Session,
        tasks,
        request: PlanningFromDBRequest,
        user_id: int | None = None,
    ) -> PlanningRequest:
        day_start_hour = request.day_start_hour
        day_end_hour = request.day_end_hour
        busy_blocks = list(request.busy_blocks)

        if user_id is not None:
            (
                day_start_hour,
                day_end_hour,
            ) = (
                self.recurring_availability_service
                .resolve_day_hours(
                    db,
                    user_id=user_id,
                    target_date=request.plan_date,
                    fallback_start_hour=(
                        request.day_start_hour
                    ),
                    fallback_end_hour=(
                        request.day_end_hour
                    ),
                )
            )

            availability_blocks = (
                self.recurring_availability_service
                .build_unavailable_blocks(
                    db,
                    user_id=user_id,
                    target_date=request.plan_date,
                )
            )

            busy_blocks.extend(
                availability_blocks
            )
            calendar_blocks = (
                self.calendar_service.get_busy_blocks(
                    target_date=request.plan_date,
                )
            )

            busy_blocks.extend(
                calendar_blocks
            )
        return PlanningRequest(
            tasks=tasks,
            plan_date=request.plan_date,
            day_start_hour=day_start_hour,
            planning_start_time=(
                request.planning_start_time
            ),
            day_end_hour=day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=busy_blocks,
            context=request.context,
        )
    
    def explain_plan_from_db(
        self,
        db: Session,
        request: PlanningFromDBRequest,
        user_id: int | None = None,
    ) -> list[PlanningDecision]:
        self.generate_routines_for_plan(
            db,
            request=request,
            user_id=user_id,
        )

        tasks = self.task_service.get_plannable(
            db,
            user_id=user_id,
        )

        tasks = [
            task
            for task in tasks
            if (
                task.preferred_date is None
                or task.preferred_date == request.plan_date
            )
        ]


        planning_request = self.build_planning_request(
            db=db,
            tasks=tasks,
            request=request,
            user_id=user_id,
        )
        adaptive_profile = (
            self.adaptive_profile_service.get(
                db,
                user_id=user_id,
            )
        )        

        return self.planner_service.explain_plan(
            request=planning_request,
            adaptive_profile=adaptive_profile,
        )    
    

    def create_plan_with_decisions_from_db(
        self,
        db: Session,
        request: PlanningFromDBRequest,
        user_id: int | None = None,
    ):
        self.generate_routines_for_plan(
            db,
            request=request,
            user_id=user_id,
        )

        tasks = self.task_service.get_plannable(
            db,
            user_id=user_id,
        )


        tasks = [
            task
            for task in tasks
            if (
                task.preferred_date is None
                or task.preferred_date == request.plan_date
            )
        ]


        planning_request = self.build_planning_request(
            db=db,
            tasks=tasks,
            request=request,
            user_id=user_id,
        )

        adaptive_profile = (
            self.adaptive_profile_service.get(
                db,
                user_id=user_id,
            )
        )


        return (
            self.planner_service
            .create_plan_with_decisions(
                request=planning_request,
                adaptive_profile=adaptive_profile,
            )
        )    