from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.dependencies import get_db
from app.models.assistant_chat import (
    AssistantChatRequest,
    AssistantChatResponse,
)
from app.services.assistant_chat_service import (
    AssistantChatService,
)


router = APIRouter(
    prefix="/assistant",
    tags=["Assistant"],
)

assistant_chat_service = AssistantChatService()


@router.post(
    "/chat",
    response_model=AssistantChatResponse,
)
def chat(
    request: AssistantChatRequest,
    db: Session = Depends(get_db),
) -> AssistantChatResponse:
    return assistant_chat_service.chat(
        db=db,
        request=request,
    )