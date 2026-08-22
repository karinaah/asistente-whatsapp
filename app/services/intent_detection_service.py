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
            phrase in message
            for phrase in (
                "replanifica",
                "reorganiza",
                "reorganizar",
                "replanear",
                "replantea",
                "reorganiza lo que queda",
                "reorganiza mi día",
                "reorganiza mi dia",
            )
        ):
            return AssistantIntent.replanning

        if any(
            phrase in message
            for phrase in (
                "me falta",
                "me faltan",
                "necesito más tiempo",
                "necesito mas tiempo",
                "necesito",
                "me atrasé",
                "me atrase",
                "voy atrasado",
                "voy atrasada",
            )
        ):
            return AssistantIntent.active_task_delay


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
        if any(
            keyword in message
            for keyword in (
                "preparar",
                "hacer",
                "enviar",
                "comprar",
                "ir al",
                "ir a ",
                "revisar",
                "responder",
                "estudiar",
                "entrenar",
                "llamar",
                "agendar",
                "crear tarea",
                "agrega tarea",
                "agregar tarea",
            )
        ):
            return AssistantIntent.task_creation
        return AssistantIntent.unknown