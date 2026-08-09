from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.services.adaptive_profile_explanation_service import (
    AdaptiveProfileExplanationService,
)
from app.models.explanation import Explanation
from app.models.schedule import PlanningFromDBRequest, PlanningRequest
from app.services.decision_engine import DecisionEngine
from app.services.human_state_service import HumanStateService
from app.services.planner_service import PlannerService
from app.services.recommendation_explanation_service import (
    RecommendationExplanationService,
)
from app.services.task_service import TaskService
from app.services.adaptive_profile_service import AdaptiveProfileService
from app.config.service_dependencies import (
    get_adaptive_profile_service,
    get_human_state_service,
    get_task_service,
)
from datetime import datetime
from app.models.recommendation import DecisionContext

router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
)

service = AdaptiveProfileExplanationService()


@router.get("/adaptive-profile")
def explain_adaptive_profile(
    db: Session = Depends(get_db),
):
    explanation = service.explain(db)

    if explanation is None:
        return {
            "message": (
                "Todavía no existe un perfil "
                "adaptativo para explicar."
            )
        }

    return explanation

@router.post(
    "/recommendation",
    response_model=Explanation | None,
)
def explain_recommendation(
    request: PlanningFromDBRequest,
    db: Session = Depends(get_db),
    task_service: TaskService = Depends(get_task_service),
    human_state_service: HumanStateService = Depends(
        get_human_state_service
    ),
    adaptive_profile_service: AdaptiveProfileService = Depends(
        get_adaptive_profile_service
    ),
) -> Explanation | None:
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

    plan = PlannerService().create_plan(
        planning_request
    )

    human_state = (
        request.human_state
        or human_state_service.get_latest(db)
    )

    adaptive_profile = (
        adaptive_profile_service.get(db)
    )

    decision_context = DecisionContext(
        current_time=datetime.now(),
        plan=plan,
        context=request.context,
        available_minutes=request.available_minutes,
        human_state=human_state,
        adaptive_profile=adaptive_profile,
    )

    recommendation = DecisionEngine().recommend(
        decision_context
    )

    if recommendation is None:
        return None

    return RecommendationExplanationService().build(
        recommendation
    )