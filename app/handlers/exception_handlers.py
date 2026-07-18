from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.task_exceptions import TaskNotFoundError
from app.exceptions.ai_exceptions import AIServiceError

def register_exception_handlers(app: FastAPI) -> None:


    @app.exception_handler(AIServiceError)
    async def ai_service_error_handler(
        request: Request,
        exc: AIServiceError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content={
                "detail": str(exc),
            },
        )