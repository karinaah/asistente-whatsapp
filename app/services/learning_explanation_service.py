from app.models.explanation import (
    Explanation,
    ExplanationType,
)
from app.models.learning_insight import (
    LearningInsight,
)


class LearningExplanationService:
    def build(
        self,
        insights: list[LearningInsight],
    ) -> Explanation:
        if not insights:
            return Explanation(
                type=ExplanationType.learning,
                title="Lo que he aprendido",
                summary=(
                    "Todavía no tengo suficiente "
                    "información para detectar patrones."
                ),
                details=[],
            )

        details: list[str] = []

        for insight in insights:
            error = insight.average_error_percentage

            if error > 0:
                details.append(
                    f"En {insight.category}, las tareas "
                    f"han tomado en promedio un "
                    f"{round(error)}% más de lo estimado."
                )
            elif error < 0:
                details.append(
                    f"En {insight.category}, las tareas "
                    f"han tomado en promedio un "
                    f"{abs(round(error))}% menos de lo estimado."
                )
            else:
                details.append(
                    f"En {insight.category}, tus estimaciones "
                    "han sido precisas."
                )

        return Explanation(
            type=ExplanationType.learning,
            title="Lo que he aprendido",
            summary=(
                f"He detectado patrones en "
                f"{len(insights)} categorías."
            ),
            details=details,
        )