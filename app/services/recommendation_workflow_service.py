from datetime import datetime

from sqlalchemy.orm import Session

from app.models.recommendation import (
    DecisionContext,
    Recommendation,
)
from app.models.schedule import PlanningFromDBRequest
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from app.services.decision_engine import DecisionEngine
from app.services.human_state_service import (
    HumanStateService,
)
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.services.recommendation_history_service import (
    RecommendationHistoryService,
)


class RecommendationWorkflowService:
    def __init__(self) -> None:
        self.planning_workflow_service = (
            PlanningWorkflowService()
        )
        self.human_state_service = (
            HumanStateService()
        )
        self.adaptive_profile_service = (
            AdaptiveProfileService()
        )
        self.recommendation_history_service = (
            RecommendationHistoryService()
        )
        self.decision_engine = DecisionEngine()

    def recommend(
        self,
        db: Session,
        request: PlanningFromDBRequest,
    ) -> Recommendation | None:
        plan = (
            self.planning_workflow_service
            .create_plan_from_db(
                db=db,
                request=request,
            )
        )

        human_state = (
            request.human_state
            or self.human_state_service.get_latest(db)
        )

        adaptive_profile = (
            self.adaptive_profile_service.get(db)
        )

        decision_context = DecisionContext(
            current_time=datetime.now(),
            plan=plan,
            context=request.context,
            available_minutes=request.available_minutes,
            human_state=human_state,
            adaptive_profile=adaptive_profile,
        )

        recommendation = (
            self.decision_engine.recommend(
                decision_context
            )
        )

        if recommendation is not None:
            self.recommendation_history_service.save(
                db=db,
                recommendation=recommendation,
                human_state=human_state,
            )

        return recommendation