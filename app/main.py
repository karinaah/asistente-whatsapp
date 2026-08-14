import logging

from fastapi import FastAPI

from app.api.assistant import router as assistant_router
from app.api.planner import router as planner_router
from app.api.tasks import router as tasks_router
from app.config.database import Base, engine
from app.config.logging_config import configure_logging
from app.config.settings import settings
from app.models.task_db import TaskDB
from app.handlers.exception_handlers import register_exception_handlers
from app.api.decision import router as decision_router
from app.models.human_state_db import HumanStateDB
from app.api.human_state import (
    router as human_state_router,
)
from app.models.recommendation_history_db import RecommendationHistoryDB
from app.api.recommendation_history import (
    router as recommendation_history_router,
)
from app.models.task_execution_db import TaskExecutionDB
from app.api.task_execution import (
    router as task_execution_router,
)
from app.models.adaptive_profile_db import AdaptiveProfileDB
from app.api.adaptive_profile import (
    router as adaptive_profile_router,
)
from app.api import explanation_api
from app.api.assistant_chat import (
    router as assistant_chat_router,
)
from app.web.routes import router as web_router
configure_logging()

# TaskDB debe estar importado antes de create_all
Base.metadata.create_all(bind=engine)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)
register_exception_handlers(app)

@app.on_event("startup")
def on_startup() -> None:
    logger.info(
        "Iniciando %s versión %s",
        settings.app_name,
        settings.app_version,
    )


@app.get("/")
def home() -> dict[str, str]:
    return {
        "status": "ok",
        "application": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


app.include_router(tasks_router)
app.include_router(planner_router)
app.include_router(assistant_router)
app.include_router(decision_router)
app.include_router(human_state_router)
app.include_router(recommendation_history_router)
app.include_router(task_execution_router)
app.include_router(adaptive_profile_router)
app.include_router(
    explanation_api.router
)
app.include_router(assistant_chat_router)
app.include_router(web_router)