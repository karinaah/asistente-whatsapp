from app.models.adaptive_profile import (
    AdaptiveProfile,
)
from app.models.explanation import (
    Explanation,
    ExplanationType,
)


class ExplanationEngine:
    def explain_adaptive_profile(
        self,
        profile: AdaptiveProfile,
    ) -> Explanation:
        details: list[str] = []

        if (
            profile.work_duration_multiplier
            > 1.0
        ):
            percentage = round(
                (
                    profile.work_duration_multiplier
                    - 1
                )
                * 100
            )

            details.append(
                "Las tareas de trabajo suelen "
                f"tomarte aproximadamente un "
                f"{percentage}% más de tiempo "
                "del estimado."
            )

        if (
            profile.prefers_short_tasks_when_low_energy
        ):
            details.append(
                "He detectado que con baja "
                "energía rindes mejor en "
                "tareas cortas."
            )

        confidence = round(
            profile.confidence * 100
        )

        summary = (
            f"He aprendido a partir de "
            f"{profile.generated_from_executions} "
            f"ejecuciones. "
            f"Actualmente mi nivel de "
            f"confianza es de {confidence}%."
        )

        return Explanation(
            type=ExplanationType.adaptive_profile,
            title="Lo que he aprendido sobre ti",
            summary=summary,
            details=details,
        )