from datetime import datetime
from sqlalchemy.orm import Session

from app.models.assistant_chat import (
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.models.assistant_intent import (
    AssistantIntent,
)
from app.models.schedule import PlanningFromDBRequest
from app.models.replanning import ReplanningRequest
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
from app.services.conversation_memory_service import (
    ConversationMemoryService,
)
from app.repositories.task_repository import TaskRepository
from app.services.mock_ai_service import MockAIService
from app.services.task_analyzer_service import TaskAnalyzerService
from app.services.task_creation_workflow_service import (
    TaskCreationWorkflowService,
)
from app.services.temporal_parser import TemporalParser
from app.services.replanning_service import ReplanningService
import re

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


        self.replanning_service = (
            ReplanningService()
        )

        self.planning_explanation_service = (
            PlanningExplanationService()
        )

        self.recommendation_history_service = (
            RecommendationHistoryService()
        )
        self.conversation_memory_service = (
            ConversationMemoryService()
        )
        self.task_creation_workflow_service = (
            TaskCreationWorkflowService(
                ai_service=MockAIService(),
                task_analyzer_service=TaskAnalyzerService(
                    temporal_parser=TemporalParser(),
                ),
                task_repository=TaskRepository(),
            )
        )
    def chat(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        context = (
            self.conversation_memory_service
            .get_context()
        )

        if context.awaiting_remaining_minutes:
            return self._handle_remaining_minutes_follow_up(
                db=db,
                request=request,
            )        

        intent = self.intent_detector.detect(
            request.message
        )
        self.conversation_memory_service.set_last_intent(
            intent
        )

        if intent == AssistantIntent.planning:
            return self._handle_planning(
                db=db,
                request=request,
            )

        if intent == AssistantIntent.replanning:
            return self._handle_replanning(
                db=db,
                request=request,
            )

        if intent == AssistantIntent.active_task_delay:
            return self._handle_active_task_delay(
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
        
        if intent == AssistantIntent.follow_up:
            return self._handle_follow_up(
                db=db,
                request=request,
            )
        if intent == AssistantIntent.task_creation:
            return self._handle_task_creation(
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
        now = datetime.now()

        planning_start_time = None

        if request.plan_date == now.date():
            planning_start_time = now.time().replace(
                second=0,
                microsecond=0,
            )        
        planning_request = PlanningFromDBRequest(
            plan_date=request.plan_date,
            day_start_hour=request.day_start_hour,
            planning_start_time=planning_start_time,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
            context=request.context,
            available_minutes=request.available_minutes,
            human_state=request.human_state,
        )

        result = (
            self.planning_workflow_service
            .create_plan_with_decisions_from_db(
                db=db,
                request=planning_request,
            )
        )

        self.conversation_memory_service.set_last_plan(
            result.response
        )

        decisions = result.decisions

        if not decisions:
            return AssistantChatResponse(
                answer=(
                    "No encontré tareas para "
                    "planificar en este momento."
                )
            )



        scheduled_tasks = sorted(
            result.response.scheduled_tasks,
            key=lambda scheduled: scheduled.start_time,
        )

        parts = [
            (
                f"{scheduled.task.title} "
                f"a las "
                f"{scheduled.start_time.strftime('%H:%M')}"
            )
            for scheduled in scheduled_tasks
        ]

        answer = (
            "He organizado tu día así: "
            + "; ".join(parts)
            + "."
        )

        unscheduled_count = len(
            result.response.unscheduled_tasks
        )


        if unscheduled_count == 1:
            answer += (
                " Quedó 1 tarea sin programar."
            )
        elif unscheduled_count > 1:
            answer += (
                f" Quedaron {unscheduled_count} "
                f"tareas sin programar."
            )


        return AssistantChatResponse(
            answer=answer
        )

    def _handle_replanning(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        now = datetime.now()

        replanning_request = ReplanningRequest(
            plan_date=request.plan_date,
            planning_start_time=now.time().replace(
                second=0,
                microsecond=0,
            ),
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        result = self.replanning_service.replan(
            db=db,
            request=replanning_request,
        )

        self.conversation_memory_service.set_last_plan(
            result
        )

        if not result.scheduled_tasks:
            return AssistantChatResponse(
                answer=(
                    "No encontré tareas pendientes "
                    "para reorganizar en este momento."
                )
            )

        scheduled_tasks = sorted(
            result.scheduled_tasks,
            key=lambda scheduled: scheduled.start_time,
        )

        parts = [
            (
                f"{scheduled.task.title} "
                f"a las "
                f"{scheduled.start_time.strftime('%H:%M')}"
            )
            for scheduled in scheduled_tasks
        ]

        answer = (
            "Reorganicé lo que queda de tu día desde las "
            f"{replanning_request.planning_start_time.strftime('%H:%M')}: "
            + "; ".join(parts)
            + "."
        )

        unscheduled_count = len(
            result.unscheduled_tasks
        )

        if unscheduled_count == 1:
            answer += (
                " Quedó 1 tarea sin programar."
            )
        elif unscheduled_count > 1:
            answer += (
                f" Quedaron {unscheduled_count} "
                f"tareas sin programar."
            )

        return AssistantChatResponse(
            answer=answer
        )



    def _handle_active_task_delay(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        context = (
            self.conversation_memory_service
            .get_context()
        )

        plan = context.last_plan

        if plan is None or not plan.scheduled_tasks:
            return AssistantChatResponse(
                answer=(
                    "No tengo un plan reciente para "
                    "identificar qué tarea estás haciendo."
                )
            )

        remaining_minutes = (
            self._extract_remaining_minutes(
                request.message
            )
        )

        now = datetime.now()

        active_scheduled = (
            self._find_active_scheduled_task(
                plan=plan,
                now=now,
            )
        )

        if active_scheduled is None:
            return AssistantChatResponse(
                answer=(
                    "No pude identificar una tarea activa "
                    "en tu plan actual."
                )
            )

        active_task = active_scheduled.task

        if active_task.id is None:
            return AssistantChatResponse(
                answer=(
                    "No pude identificar correctamente "
                    "la tarea activa para reorganizar el día."
                )
            )

        if remaining_minutes is None:
            (
                self.conversation_memory_service
                .set_awaiting_remaining_minutes(
                    active_task.id
                )
            )

            return AssistantChatResponse(
                answer=(
                    "¿Cuánto tiempo crees que te falta "
                    f"para terminar {active_task.title}?"
                )
            )

        replanning_request = ReplanningRequest(
            plan_date=request.plan_date,
            planning_start_time=now.time().replace(
                second=0,
                microsecond=0,
            ),
            active_task_id=active_task.id,
            remaining_minutes=remaining_minutes,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        result = self.replanning_service.replan(
            db=db,
            request=replanning_request,
        )

        self.conversation_memory_service.set_last_plan(
            result
        )

        scheduled_tasks = sorted(
            result.scheduled_tasks,
            key=lambda scheduled: scheduled.start_time,
        )

        parts = [
            (
                f"{scheduled.task.title} "
                f"a las "
                f"{scheduled.start_time.strftime('%H:%M')}"
            )
            for scheduled in scheduled_tasks
        ]

        answer = (
            f"Entendido. Consideraré que te quedan "
            f"{remaining_minutes} minutos en "
            f"{active_task.title}. "
            f"Reorganicé lo que queda de tu día: "
            + "; ".join(parts)
            + "."
        )

        return AssistantChatResponse(
            answer=answer
        )


    def _handle_remaining_minutes_follow_up(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        context = (
            self.conversation_memory_service
            .get_context()
        )

        remaining_minutes = (
            self._extract_remaining_minutes(
                request.message
            )
        )

        if remaining_minutes is None:
            return AssistantChatResponse(
                answer=(
                    "No entendí cuánto tiempo te falta. "
                    "Por ejemplo, puedes decir 30 minutos "
                    "o 1 hora."
                )
            )

        plan = context.last_plan

        if plan is None:
            self.conversation_memory_service.clear_awaiting_remaining_minutes()

            return AssistantChatResponse(
                answer=(
                    "Perdí el plan reciente, así que no puedo "
                    "reorganizar la tarea pendiente."
                )
            )

        task_id = context.pending_active_task_id

        active_scheduled = next(
            (
                scheduled
                for scheduled in plan.scheduled_tasks
                if scheduled.task.id == task_id
            ),
            None,
        )

        if active_scheduled is None:
            self.conversation_memory_service.clear_awaiting_remaining_minutes()

            return AssistantChatResponse(
                answer=(
                    "No pude encontrar la tarea que estaba "
                    "pendiente en tu plan."
                )
            )

        active_task = active_scheduled.task

        now = datetime.now()

        replanning_request = ReplanningRequest(
            plan_date=request.plan_date,
            planning_start_time=now.time().replace(
                second=0,
                microsecond=0,
            ),
            active_task_id=task_id,
            remaining_minutes=remaining_minutes,
            day_end_hour=request.day_end_hour,
            break_minutes=request.break_minutes,
            busy_blocks=request.busy_blocks,
        )

        result = self.replanning_service.replan(
            db=db,
            request=replanning_request,
        )

        self.conversation_memory_service.set_last_plan(
            result
        )

        self.conversation_memory_service.clear_awaiting_remaining_minutes()

        scheduled_tasks = sorted(
            result.scheduled_tasks,
            key=lambda scheduled: scheduled.start_time,
        )

        parts = [
            (
                f"{scheduled.task.title} "
                f"a las "
                f"{scheduled.start_time.strftime('%H:%M')}"
            )
            for scheduled in scheduled_tasks
        ]

        answer = (
            f"Perfecto. Consideraré que te quedan "
            f"{remaining_minutes} minutos en "
            f"{active_task.title}. "
            f"Reorganicé lo que queda de tu día: "
            + "; ".join(parts)
            + "."
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

        self.conversation_memory_service.set_last_recommendation(
            recommendation
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

        # Primero intenta usar la memoria conversacional
        context = (
            self.conversation_memory_service
            .get_context()
        )

        if context.last_recommendation is not None:
            recommendation = (
                context.last_recommendation
            )

            answer = (
                recommendation.summary
                or (
                    f"Te recomendé "
                    f"{recommendation.task.title}."
                )
            )

            return AssistantChatResponse(
                answer=answer
            )

        # Si no hay memoria, usa el historial (fallback)
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

    def _extract_remaining_minutes(
        self,
        message: str,
    ) -> int | None:
        normalized_message = message.lower()

        hours_match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(?:horas?|hrs?|h)\b",
            normalized_message,
        )

        minutes_match = re.search(
            r"(\d+)\s*(?:minutos?|mins?|min)\b",
            normalized_message,
        )

        total_minutes = 0

        if hours_match:
            hours = float(
                hours_match.group(1).replace(",", ".")
            )
            total_minutes += round(hours * 60)

        if minutes_match:
            total_minutes += int(
                minutes_match.group(1)
            )

        return total_minutes or None




    def _find_active_scheduled_task(
        self,
        plan,
        now: datetime,
    ):
        scheduled_tasks = sorted(
            plan.scheduled_tasks,
            key=lambda scheduled: scheduled.start_time,
        )

        for scheduled in scheduled_tasks:
            if (
                scheduled.start_time
                <= now
                < scheduled.end_time
            ):
                return scheduled

        return None


    def _handle_follow_up(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        context = (
            self.conversation_memory_service
            .get_context()
        )

        plan = context.last_plan

        if plan is None or not plan.scheduled_tasks:
            return AssistantChatResponse(
                answer=(
                    "Todavía no tengo un plan reciente "
                    "para decirte qué sigue."
                )
            )

        scheduled_tasks = plan.scheduled_tasks

        if context.last_recommendation is not None:
            recommended_task = (
                context.last_recommendation.task
            )

            for index, scheduled in enumerate(
                scheduled_tasks
            ):
                same_task = (
                    scheduled.task.id == recommended_task.id
                    if (
                        scheduled.task.id is not None
                        and recommended_task.id is not None
                    )
                    else (
                        scheduled.task.title
                        == recommended_task.title
                    )
                )

                if same_task:
                    next_index = index + 1

                    if next_index < len(scheduled_tasks):
                        next_task = scheduled_tasks[
                            next_index
                        ]

                        return AssistantChatResponse(
                            answer=(
                                f"Después sigue "
                                f"{next_task.task.title}, "
                                f"programada para las "
                                f"{next_task.start_time.strftime('%H:%M')}."
                            )
                        )

                    return AssistantChatResponse(
                        answer=(
                            "Esa es la última tarea "
                            "de tu plan actual."
                        )
                    )

        if len(scheduled_tasks) >= 2:
            next_task = scheduled_tasks[1]

            return AssistantChatResponse(
                answer=(
                    f"Después sigue "
                    f"{next_task.task.title}, "
                    f"programada para las "
                    f"{next_task.start_time.strftime('%H:%M')}."
                )
            )

        return AssistantChatResponse(
            answer=(
                "No hay otra tarea después "
                "en tu plan actual."
            )
        )
    
    def _handle_task_creation(
        self,
        db: Session,
        request: AssistantChatRequest,
    ) -> AssistantChatResponse:
        tasks = (
            self.task_creation_workflow_service
            .create_from_text(
                db=db,
                text=request.message,
                reference_date=request.plan_date,
            )
        )

        if not tasks:
            return AssistantChatResponse(
                answer="No pude crear una tarea a partir de tu mensaje."
            )

        if len(tasks) == 1:
            task = tasks[0]

            should_replan = (
                task.priority.value == "alta"
                and (
                    task.preferred_date is None
                    or task.preferred_date == request.plan_date
                )
            )

            if should_replan:
                now = datetime.now()

                replanning_request = ReplanningRequest(
                    plan_date=request.plan_date,
                    planning_start_time=now.time().replace(
                        second=0,
                        microsecond=0,
                    ),
                    day_end_hour=request.day_end_hour,
                    break_minutes=request.break_minutes,
                    busy_blocks=request.busy_blocks,
                )

                result = self.replanning_service.replan(
                    db=db,
                    request=replanning_request,
                )

                self.conversation_memory_service.set_last_plan(
                    result
                )

                scheduled_tasks = sorted(
                    result.scheduled_tasks,
                    key=lambda scheduled: scheduled.start_time,
                )

                parts = [
                    (
                        f"{scheduled.task.title} "
                        f"a las "
                        f"{scheduled.start_time.strftime('%H:%M')}"
                    )
                    for scheduled in scheduled_tasks
                ]

                answer = (
                    f"Creé la tarea urgente '{task.title}' "
                    f"y reorganicé lo que queda de tu día: "
                    + "; ".join(parts)
                    + "."
                )

                return AssistantChatResponse(
                    answer=answer
                )

            return AssistantChatResponse(
                answer=(
                    f"Creé la tarea '{task.title}'. "
                    f"Workspace: {task.workspace.value}. "
                    f"Tipo de actividad: {task.activity_type.value}."
                )
            )




        titles = ", ".join(
            task.title
            for task in tasks
        )

        return AssistantChatResponse(
            answer=(
                f"Creé {len(tasks)} tareas: {titles}."
            )
        )    