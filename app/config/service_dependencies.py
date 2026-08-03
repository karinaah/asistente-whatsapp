from fastapi import Depends

from app.config.settings import settings
from app.repositories.task_repository import TaskRepository
from app.services.ai_service import AIService
from app.services.assistant_service import AssistantService
from app.services.mock_ai_service import MockAIService
from app.services.openai_service import OpenAIService
from app.services.planner_service import PlannerService
from app.services.task_analyzer_service import TaskAnalyzerService
from app.services.task_service import TaskService
from app.services.temporal_parser import TemporalParser
from app.services.human_state_service import HumanStateService

def get_task_service() -> TaskService:
    return TaskService()

def get_human_state_service() -> HumanStateService:
    return HumanStateService()

def get_ai_service() -> AIService:
    if settings.USE_MOCK_AI:
        return MockAIService()

    return OpenAIService()


def get_temporal_parser() -> TemporalParser:
    return TemporalParser()


def get_task_analyzer_service(
    temporal_parser: TemporalParser = Depends(
        get_temporal_parser
    ),
) -> TaskAnalyzerService:
    return TaskAnalyzerService(
        temporal_parser=temporal_parser,
    )


def get_assistant_service(
    ai_service: AIService = Depends(get_ai_service),
    task_analyzer_service: TaskAnalyzerService = Depends(
        get_task_analyzer_service
    ),
) -> AssistantService:
    planner_service = PlannerService()
    task_repository = TaskRepository()

    return AssistantService(
        ai_service=ai_service,
        planner_service=planner_service,
        task_repository=task_repository,
        task_analyzer_service=task_analyzer_service,
    )