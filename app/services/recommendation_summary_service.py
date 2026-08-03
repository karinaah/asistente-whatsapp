from app.models.recommendation import (
    Recommendation,
    RecommendationReasonCode,
)


class RecommendationSummaryService:
    def build_summary(
        self,
        recommendation: Recommendation,
    ) -> str:
        title = recommendation.task.title

        reason_codes = {
            reason.code
            for reason in recommendation.reasons
        }

        sentences = [
            f"Te recomiendo hacer {title}."
        ]

        planning_reasons = []

        if (
            RecommendationReasonCode.earliest_available
            in reason_codes
        ):
            planning_reasons.append(
                "es tu próxima tarea programada"
            )

        if (
            RecommendationReasonCode.high_priority
            in reason_codes
        ):
            planning_reasons.append(
                "tiene prioridad alta"
            )

        if (
            RecommendationReasonCode.deadline_soon
            in reason_codes
        ):
            planning_reasons.append(
                "vence hoy"
            )

        if RecommendationReasonCode.overdue in reason_codes:
            planning_reasons.append(
                "está vencida"
            )

        if planning_reasons:
            sentences.append(
                self._join_reasons(planning_reasons)
                + "."
            )

        context_reasons = []

        if (
            RecommendationReasonCode.fits_available_time
            in reason_codes
        ):
            context_reasons.append(
                "cabe en el tiempo que tienes disponible"
            )

        if (
            RecommendationReasonCode.context_match
            in reason_codes
        ):
            context_reasons.append(
                "coincide con tu contexto actual"
            )

        if (
            RecommendationReasonCode.preferred_time_match
            in reason_codes
        ):
            context_reasons.append(
                "coincide con tu horario preferido"
            )

        if context_reasons:
            sentences.append(
                self._join_reasons(context_reasons)
                + "."
            )

        human_reasons = []

        if (
            RecommendationReasonCode.energy_match
            in reason_codes
        ):
            human_reasons.append(
                "tu nivel de energía es adecuado"
            )

        if (
            RecommendationReasonCode.focus_match
            in reason_codes
        ):
            human_reasons.append(
                "tu nivel de enfoque es adecuado"
            )


        if human_reasons:
            human_text = self._join_reasons(
                human_reasons,
                capitalize=False,
            )

            sentences.append(
                f"Además, {human_text}."
            )


        if (
            RecommendationReasonCode.high_stress_penalty
            in reason_codes
        ):
            sentences.append(
                "Sin embargo, tu nivel de estrés es alto, "
                "así que conviene abordarla con cautela."
            )

        return " ".join(sentences)

 
    def _join_reasons(
        self,
        reasons: list[str],
        capitalize: bool = True,
    ) -> str:
        if len(reasons) == 1:
            text = reasons[0]
        else:
            text = (
                ", ".join(reasons[:-1])
                + f" y {reasons[-1]}"
            )

        if capitalize:
            return text.capitalize()

        return text    