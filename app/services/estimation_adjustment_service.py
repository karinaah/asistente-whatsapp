from app.models.learning_insight import LearningInsight


class EstimationAdjustmentService:
    def adjust(
        self,
        estimated_minutes: int,
        insight: LearningInsight,
    ) -> int:
        if insight.executions < 3:
            return estimated_minutes

        if insight.average_estimated_minutes <= 0:
            return estimated_minutes

        adjustment_ratio = (
            insight.average_actual_minutes
            / insight.average_estimated_minutes
        )

        adjusted_minutes = round(
            estimated_minutes * adjustment_ratio
        )

        return max(1, adjusted_minutes)