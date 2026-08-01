from app.models.recommendation import (
    DecisionContext,
    Recommendation,
    RecommendationReason,
    RecommendationReasonCode,
)


class DecisionEngine:
    def recommend(
        self,
        context: DecisionContext,
    ) -> Recommendation | None:
        scheduled_tasks = context.plan.scheduled_tasks

        if not scheduled_tasks:
            return None

        active_task = next(
            (
                scheduled
                for scheduled in scheduled_tasks
                if scheduled.start_time
                <= context.current_time
                < scheduled.end_time
            ),
            None,
        )

        if active_task is not None:
            reasons = self._build_reasons(
                scheduled_task=active_task,
                base_score=100.0,
                message=(
                    "Esta tarea está programada "
                    "para realizarse ahora."
                ),
            )

            return Recommendation(
                task=active_task.task,
                scheduled_task=active_task,
                score=sum(
                    reason.score
                    for reason in reasons
                ),
                reasons=reasons,
            )

        upcoming_tasks = [
            scheduled
            for scheduled in scheduled_tasks
            if scheduled.start_time >= context.current_time
        ]

        if not upcoming_tasks:
            return None

        next_task = min(
            upcoming_tasks,
            key=lambda scheduled: scheduled.start_time,
        )

        reasons = self._build_reasons(
            scheduled_task=next_task,
            base_score=50.0,
            message=(
                "Esta es la próxima tarea "
                "programada en tu agenda."
            ),
        )

        return Recommendation(
            task=next_task.task,
            scheduled_task=next_task,
            score=sum(
                reason.score
                for reason in reasons
            ),
            reasons=reasons,
        )

    def _build_reasons(
        self,
        scheduled_task,
        base_score: float,
        message: str,
    ) -> list[RecommendationReason]:
        reasons = [
            RecommendationReason(
                code=RecommendationReasonCode.earliest_available,
                message=message,
                score=base_score,
            )
        ]

        if scheduled_task.task.priority.value == "alta":
            reasons.append(
                RecommendationReason(
                    code=RecommendationReasonCode.high_priority,
                    message="La tarea tiene prioridad alta.",
                    score=30.0,
                )
            )

        deadline = scheduled_task.task.deadline

        if (
            deadline is not None
            and deadline.date()
            == scheduled_task.start_time.date()
        ):
            reasons.append(
                RecommendationReason(
                    code=RecommendationReasonCode.deadline_soon,
                    message="La tarea vence hoy.",
                    score=40.0,
                )
            )

        return reasons