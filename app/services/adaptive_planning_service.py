from sqlalchemy.orm import Session

from app.models.schedule import (
    PlanningRequest,
    PlanningResponse,
)

from app.services.planner_service import PlannerService

from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)

class AdaptivePlanningService:
    def __init__(self) -> None:
        self.planner_service = PlannerService()
        self.adaptive_profile_service = (
            AdaptiveProfileService()
        )


    def create_plan(
        self,
        db: Session,
        request: PlanningRequest,
        user_id: int | None = None,
    ) -> PlanningResponse:
        profile = self.adaptive_profile_service.get(
            db,
            user_id=user_id,
        )

        if profile is None:
            profile = self.adaptive_profile_service.rebuild(
                db,
                user_id=user_id,
            )

        return self.planner_service.create_plan(
            request=request,
            adaptive_profile=profile,
        )    