from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.config.service_dependencies import (
    get_adaptive_profile_service,
    get_human_state_service,
)
from app.models.explanation import Explanation
from app.models.recommendation import DecisionContext
from app.models.schedule import PlanningFromDBRequest
from app.services.adaptive_profile_explanation_service import (
    AdaptiveProfileExplanationService,
)
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from app.services.decision_engine import DecisionEngine
from app.services.human_state_service import HumanStateService
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.services.recommendation_explanation_service import (
    RecommendationExplanationService,
)
from app.services.planning_explanation_service import (
    PlanningExplanationService,
)
from app.models.schedule import (
    PlanningFromDBRequest,
    PlanningRequest,
)
from app.services.learning_explanation_service import (
    LearningExplanationService,
)
from app.services.learning_service import LearningService
from app.services.task_execution_service import (
    TaskExecutionService,
)


router = APIRouter(
    prefix="/explanations",
    tags=["Explanations"],
)

adaptive_profile_explanation_service = (
    AdaptiveProfileExplanationService()
)

planning_workflow_service = (
    PlanningWorkflowService()
)

decision_engine = DecisionEngine()

recommendation_explanation_service = (
    RecommendationExplanationService()
)

planning_explanation_service = (
    PlanningExplanationService()
)
learning_service = LearningService()

learning_explanation_service = (
    LearningExplanationService()
)

task_execution_service = (
    TaskExecutionService()
)


@router.get("/adaptive-profile")
def explain_adaptive_profile(
    db: Session = Depends(get_db),
):
    explanation = (
        adaptive_profile_explanation_service.explain(db)
    )

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
    human_state_service: HumanStateService = Depends(
        get_human_state_service
    ),
    adaptive_profile_service: AdaptiveProfileService = Depends(
        get_adaptive_profile_service
    ),
) -> Explanation | None:
    plan = planning_workflow_service.create_plan_from_db(
        db=db,
        request=request,
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

    recommendation = decision_engine.recommend(
        decision_context
    )

    if recommendation is None:
        return None

    return recommendation_explanation_service.build(
        recommendation
    )


@router.post(
    "/planning",
    response_model=list[Explanation],
)
def explain_planning(
    request: PlanningFromDBRequest,
    db: Session = Depends(get_db),
) -> list[Explanation]:
    tasks = (
        planning_workflow_service.task_service
        .get_plannable(db)
    )

    adaptive_profile = (
        planning_workflow_service
        .adaptive_profile_service
        .get(db)
    )

    planning_request = PlanningRequest(
        tasks=tasks,
        plan_date=request.plan_date,
        day_start_hour=request.day_start_hour,
        day_end_hour=request.day_end_hour,
        break_minutes=request.break_minutes,
        busy_blocks=request.busy_blocks,
        context=request.context,
    )

    decisions = (
        planning_workflow_service
        .planner_service
        .explain_plan(
            request=planning_request,
            adaptive_profile=adaptive_profile,
        )
    )

    return [
        planning_explanation_service.build(
            decision
        )
        for decision in decisions
    ]


@router.get(
    "/learning",
    response_model=Explanation,
)
def explain_learning(
    db: Session = Depends(get_db),
) -> Explanation:
    executions = (
        task_execution_service.get_all_for_learning(db)
    )

    insights = learning_service.get_estimation_insights(
        executions
    )

    return learning_explanation_service.build(
        insights
    )