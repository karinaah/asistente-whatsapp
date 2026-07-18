from fastapi import Depends

from app.config.settings import settings
from app.services.ai_service import AIService
from app.services.assistant_service import AssistantService
from app.services.mock_ai_service import MockAIService
from app.services.openai_service import OpenAIService
from app.services.task_service import TaskService


def get_task_service() -> TaskService:
    return TaskService()


def get_ai_service() -> AIService:
    if settings.USE_MOCK_AI:
        return MockAIService()

    return OpenAIService()


def get_assistant_service(
    ai_service: AIService = Depends(get_ai_service),
) -> AssistantService:
    return AssistantService(ai_service=ai_service)