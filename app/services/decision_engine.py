from app.models.recommendation import (
    DecisionContext,
    Recommendation,
    RecommendationReason,
    RecommendationReasonCode,
)
from app.services.decision_rules.deadline_rule import DeadlineRule
from app.services.decision_rules.preferred_time_rule import (
    PreferredTimeRule,
)
from app.services.decision_rules.priority_rule import PriorityRule
from app.services.decision_scoring import DecisionRuleWeights


class DecisionEngine:
    def __init__(self) -> None:
        self.rules = [
            PriorityRule(),
            DeadlineRule(),
            PreferredTimeRule(),
        ]

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
            return self._build_recommendation(
                scheduled_task=active_task,
                base_score=DecisionRuleWeights.ACTIVE_TASK,
                message=(
                    "Esta tarea está programada "
                    "para realizarse ahora."
                ),
                context=context,
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

        return self._build_recommendation(
            scheduled_task=next_task,
            base_score=DecisionRuleWeights.UPCOMING_TASK,
            message=(
                "Esta es la próxima tarea "
                "programada en tu agenda."
            ),
            context=context,
        )

    def _build_reasons(
        self,
        scheduled_task,
        base_score: float,
        message: str,
        context: DecisionContext,
    ) -> list[RecommendationReason]:
        reasons = [
            RecommendationReason(
                code=RecommendationReasonCode.earliest_available,
                message=message,
                score=base_score,
            )
        ]

        for rule in self.rules:
            reasons.extend(
                rule.evaluate(
                    scheduled_task,
                    context,
                )
            )

        return reasons

    def _build_recommendation(
        self,
        scheduled_task,
        base_score: float,
        message: str,
        context: DecisionContext,
    ) -> Recommendation:
        reasons = self._build_reasons(
            scheduled_task=scheduled_task,
            base_score=base_score,
            message=message,
            context=context,
        )

        return Recommendation(
            task=scheduled_task.task,
            scheduled_task=scheduled_task,
            score=sum(
                reason.score
                for reason in reasons
            ),
            reasons=reasons,
        )