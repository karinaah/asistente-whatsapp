from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import (
    get_human_state_service,
    get_task_service,
    get_recommendation_history_service,
)

from app.models.recommendation import (
    DecisionContext,
    Recommendation,
)
from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningRequest,
)
from app.services.decision_engine import DecisionEngine
from app.services.planner_service import PlannerService
from app.services.task_service import TaskService
from app.services.human_state_service import HumanStateService
from app.services.recommendation_history_service import (
    RecommendationHistoryService,
)

router = APIRouter(
    prefix="/decision",
    tags=["Decision"],
)

planner_service = PlannerService()
decision_engine = DecisionEngine()


@router.post(
    "/recommend",
    response_model=Recommendation | None,
)
def recommend_next_action(
    request: PlanningFromDBRequest,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
    human_state_service: HumanStateService = Depends(
        get_human_state_service
    ),
    recommendation_history_service: RecommendationHistoryService = Depends(
        get_recommendation_history_service
    ),    
) -> Recommendation | None:
    tasks = task_service.get_plannable(db)

    planning_request = PlanningRequest(
        tasks=tasks,
        plan_date=request.plan_date,
        day_start_hour=request.day_start_hour,
        day_end_hour=request.day_end_hour,
        break_minutes=request.break_minutes,
        busy_blocks=request.busy_blocks,
        context=request.context,
    )

    plan = planner_service.create_plan(
        planning_request
    )

    human_state = (
        request.human_state
        or human_state_service.get_latest(db)
    )

    decision_context = DecisionContext(
        current_time=datetime.now(),
        plan=plan,
        context=request.context,
        available_minutes=request.available_minutes,
        human_state=human_state,
    )

    recommendation = decision_engine.recommend(
        decision_context
    )

    if recommendation is not None:
        recommendation_history_service.save(
            db=db,
            recommendation=recommendation,
            human_state=human_state,
        )

    return recommendation