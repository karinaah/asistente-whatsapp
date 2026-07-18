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