from openai import (
    APIConnectionError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from app.config.settings import settings
from app.exceptions.ai_exceptions import AIServiceError
from app.models.task import ExtractedTasks, Task


class OpenAIService:
    def __init__(self) -> None:
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no está configurada.")

        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def extract_tasks(self, text: str) -> list[Task]:
        try:
            response = self.client.responses.parse(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "system",
                        "content": (
                            "Extrae tareas concretas del texto del usuario. "
                            "Cada tarea debe tener un título claro, una duración "
                            "estimada razonable, prioridad y categoría. "
                            "No inventes tareas que no estén presentes."
                        ),
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                text_format=ExtractedTasks,
            )

        except AuthenticationError:
            raise AIServiceError("La API Key de OpenAI no es válida.")

        except RateLimitError:
            raise AIServiceError(
                "La cuenta de OpenAI no tiene cuota disponible."
            )

        except APIConnectionError:
            raise AIServiceError(
                "No fue posible conectar con OpenAI."
            )

        extracted_tasks = response.output_parsed

        if extracted_tasks is None:
            return []

        return extracted_tasks.tasks