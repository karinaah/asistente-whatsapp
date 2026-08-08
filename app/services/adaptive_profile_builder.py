from app.models.adaptive_profile import (
    AdaptiveProfile,
)
from app.models.learning_insight import (
    LearningInsight,
)
from app.models.productivity_insight import (
    ProductivityInsight,
)


class AdaptiveProfileBuilder:
    def build(
        self,
        estimation_insights: list[LearningInsight],
        productivity: ProductivityInsight,
    ) -> AdaptiveProfile:
        profile = AdaptiveProfile(
            generated_from_executions=sum(
                insight.executions
                for insight in estimation_insights
            )
        )

        for insight in estimation_insights:
            multiplier = (
                insight.average_actual_minutes
                / insight.average_estimated_minutes
            )

            match insight.category:
                case "trabajo":
                    profile.work_duration_multiplier = (
                        round(multiplier, 2)
                    )

                case "estudio":
                    profile.study_duration_multiplier = (
                        round(multiplier, 2)
                    )

                case "personal":
                    profile.personal_duration_multiplier = (
                        round(multiplier, 2)
                    )

                case "salud":
                    profile.health_duration_multiplier = (
                        round(multiplier, 2)
                    )

                case _:
                    profile.other_duration_multiplier = (
                        round(multiplier, 2)
                    )

        if (
            productivity.low_energy_average_error
            >
            productivity.high_energy_average_error
        ):
            profile.prefers_short_tasks_when_low_energy = (
                True
            )

        profile.confidence = min(
            1.0,
            profile.generated_from_executions / 20,
        )

        return profile