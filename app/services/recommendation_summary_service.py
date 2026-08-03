from app.models.recommendation import Recommendation


class RecommendationSummaryService:
    def build_summary(
        self,
        recommendation: Recommendation,
    ) -> str:
        reason_messages = [
            reason.message.rstrip(".")
            for reason in recommendation.reasons
        ]

        if not reason_messages:
            return (
                f"Te recomiendo hacer "
                f"{recommendation.task.title}."
            )

        reasons_text = ", ".join(reason_messages)

        return (
            f"Te recomiendo hacer "
            f"{recommendation.task.title} porque "
            f"{reasons_text.lower()}."
        )