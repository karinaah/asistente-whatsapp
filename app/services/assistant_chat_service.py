from app.models.assistant_chat import (
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.models.assistant_intent import (
    AssistantIntent,
)
from app.services.intent_detection_service import (
    IntentDetectionService,
)
from sqlalchemy.orm import Session

from app.models.schedule import PlanningFromDBRequest
from app.services.recommendation_workflow_service import (
    RecommendationWorkflowService,
)
from app.services.learning_explanation_service import (
    LearningExplanationService,
)
from app.services.learning_service import LearningService
from app.services.task_execution_service import (
    TaskExecutionService,
)

class AssistantChatService:
    def __init__(self) -> None:
        self.intent_detector = (
            IntentDetectionService()
        )
        self.recommendation_workflow_service = (
            RecommendationWorkflowService()
        )
        self.learning_service = LearningService()

        self.learning_explanation_service = (
            LearningExplanationService()
        )

        self.task_execution_service = (
            TaskExecutionService()
        )


    def chat(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        intent = self.intent_detector.detect(
            request.message
        )

        if intent == AssistantIntent.planning:
            answer = "Entendí que deseas planificar."


        elif intent == AssistantIntent.recommendation:
            planning_request = PlanningFromDBRequest(
                plan_date=request.plan_date,
                day_start_hour=request.day_start_hour,
                day_end_hour=request.day_end_hour,
                break_minutes=request.break_minutes,
                busy_blocks=request.busy_blocks,
                context=request.context,
                available_minutes=request.available_minutes,
                human_state=request.human_state,
            )



            recommendation = (
                self.recommendation_workflow_service.recommend(
                    db=db,
                    request=planning_request,
                )
            )

            if recommendation is None:
                answer = (
                    "No encontré una tarea para recomendarte "
                    "en este momento."
                )
            else:
                answer = (
                    recommendation.summary
                    or (
                        f"Te recomiendo hacer "
                        f"{recommendation.task.title}."
                    )
                )



        elif intent == AssistantIntent.learning:
            executions = (
                self.task_execution_service
                .get_all_for_learning(db)
            )

            insights = (
                self.learning_service
                .get_estimation_insights(
                    executions
                )
            )

            explanation = (
                self.learning_explanation_service
                .build(insights)
            )

            answer = explanation.summary

            if explanation.details:
                answer += " " + " ".join(
                    explanation.details
                )



        elif intent == AssistantIntent.explanation:
            answer = (
                "Entendí que deseas una explicación."
            )

        else:
            answer = "No entendí tu solicitud."

        return AssistantChatResponse(
            answer=answer,
        )