from app.models.task import Task


def make_task(**overrides) -> Task:
    data = {
        "title": "Tarea de prueba",
        "estimated_minutes": 50,
        "priority": "media",
        "effort": "medio",
    }

    data.update(overrides)

    return Task(**data)