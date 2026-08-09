from app.models.explanation import (
    Explanation,
    ExplanationType,
)
from app.models.recommendation import Recommendation


class RecommendationExplanationService:
    def build(
        self,
        recommendation: Recommendation,
    ) -> Explanation:
        details = [
            reason.message
            for reason in recommendation.reasons
        ]

        summary = (
            recommendation.summary
            or (
                f"Te recomiendo hacer "
                f"{recommendation.task.title}."
            )
        )

        return Explanation(
            type=ExplanationType.recommendation,
            title=(
                f"Por qué te recomiendo "
                f"{recommendation.task.title}"
            ),
            summary=summary,
            details=details,
        )