from app.models.explanation import (
    Explanation,
)
from app.services.adaptive_profile_service import (
    AdaptiveProfileService,
)
from app.services.explanation_engine import (
    ExplanationEngine,
)


class AdaptiveProfileExplanationService:
    def __init__(self) -> None:
        self.profile_service = (
            AdaptiveProfileService()
        )

        self.engine = (
            ExplanationEngine()
        )

    def explain(
        self,
        db,
    ) -> Explanation | None:
        profile = self.profile_service.get(db)

        if profile is None:
            return None

        return self.engine.explain_adaptive_profile(
            profile
        )