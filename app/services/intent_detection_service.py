from app.models.assistant_intent import (
    AssistantIntent,
)


class IntentDetectionService:
    def detect(
        self,
        message: str,
    ) -> AssistantIntent:
        message = message.lower()

        if any(
            keyword in message
            for keyword in (
                "plan",
                "planifica",
                "agenda",
                "organiza",
            )
        ):
            return AssistantIntent.planning

        if any(
            keyword in message
            for keyword in (
                "qué hago",
                "que hago",
                "recomienda",
                "siguiente tarea",
            )
        ):
            return AssistantIntent.recommendation

        if any(
            keyword in message
            for keyword in (
                "aprend",
                "patrón",
                "patron",
            )
        ):
            return AssistantIntent.learning

        if any(
            keyword in message
            for keyword in (
                "por qué",
                "por que",
                "explica",
            )
        ):
            return AssistantIntent.explanation

        if any(
            phrase in message
            for phrase in (
                "y después",
                "y despues",
                "qué sigue",
                "que sigue",
                "la siguiente",
                "siguiente",
            )
        ):
            return AssistantIntent.follow_up

        return AssistantIntent.unknown