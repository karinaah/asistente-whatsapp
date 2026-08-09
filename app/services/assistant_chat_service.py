from sqlalchemy.orm import Session

from app.models.assistant_chat import (
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.models.assistant_intent import (
    AssistantIntent,
)
from app.models.schedule import PlanningFromDBRequest
from app.services.intent_detection_service import (
    IntentDetectionService,
)
from app.services.learning_explanation_service import (
    LearningExplanationService,
)
from app.services.learning_service import LearningService
from app.services.recommendation_workflow_service import (
    RecommendationWorkflowService,
)
from app.services.task_execution_service import (
    TaskExecutionService,
)
from app.services.planning_workflow_service import (
    PlanningWorkflowService,
)
from app.services.planning_explanation_service import (
    PlanningExplanationService,
)
import json

from app.services.recommendation_history_service import (
    RecommendationHistoryService,
)

class AssistantChatService:
    def __init__(self) -> None:
        self.intent_detector = IntentDetectionService()

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
        self.planning_workflow_service = (
            PlanningWorkflowService()
        )

        self.planning_explanation_service = (
            PlanningExplanationService()
        )

        self.recommendation_history_service = (
            RecommendationHistoryService()
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
            return self._handle_planning(
                db=db,
                request=request,
            )

        if intent == AssistantIntent.recommendation:
            return self._handle_recommendation(
                db=db,
                request=request,
            )

        if intent == AssistantIntent.learning:
            return self._handle_learning(
                db=db,
                request=request,
            )

        if intent == AssistantIntent.explanation:
            return self._handle_explanation(
                db=db,
                request=request,
            )

        return AssistantChatResponse(
            answer="No entendí tu solicitud."
        )

    
    def _handle_planning(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
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

        decisions = (
            self.planning_workflow_service
            .explain_plan_from_db(
                db=db,
                request=planning_request,
            )
        )



        if not decisions:
            return AssistantChatResponse(
                answer=(
                    "No encontré tareas para "
                    "planificar en este momento."
                )
            )

        explanations = [
            self.planning_explanation_service.build(
                decision
            )
            for decision in decisions
        ]

        answer = " ".join(
            explanation.summary
            for explanation in explanations
        )

        return AssistantChatResponse(
            answer=answer
        )


    def _handle_recommendation(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
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
            self.recommendation_workflow_service
            .recommend(
                db=db,
                request=planning_request,
            )
        )

        if recommendation is None:
            return AssistantChatResponse(
                answer=(
                    "No encontré una tarea para "
                    "recomendarte en este momento."
                )
            )

        answer = (
            recommendation.summary
            or (
                f"Te recomiendo hacer "
                f"{recommendation.task.title}."
            )
        )

        return AssistantChatResponse(
            answer=answer
        )

    def _handle_learning(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
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

        return AssistantChatResponse(
            answer=answer
        )

    def _handle_explanation(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        latest = (
            self.recommendation_history_service
            .get_latest(db)
        )

        if latest is None:
            return AssistantChatResponse(
                answer=(
                    "Todavía no tengo una recomendación "
                    "reciente para explicar."
                )
            )

        reasons = json.loads(
            latest.reasons_json
        )

        details = [
            reason["message"]
            for reason in reasons
        ]


        if latest.summary:
            answer = latest.summary
        else:
            answer = (
                f"Te recomendé {latest.task_title}."
            )

            if details:
                answer += " " + " ".join(details)


        return AssistantChatResponse(
            answer=answer
        )