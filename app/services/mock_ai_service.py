from app.models.task import Task, TaskCategory, TaskPriority


class MockAIService:
    def extract_tasks(self, text: str) -> list[Task]:
        normalized_text = text.lower()

        tasks: list[Task] = []

        if "yoga" in normalized_text:
            tasks.append(
                Task(
                    title="Hacer yoga",
                    estimated_minutes=60,
                    priority=TaskPriority.medium,
                    category=TaskCategory.health,
                )
            )

        if "tesis" in normalized_text:
            tasks.append(
                Task(
                    title="Revisar tesis",
                    estimated_minutes=120,
                    priority=TaskPriority.high,
                    category=TaskCategory.study,
                )
            )

        if "clase" in normalized_text:
            tasks.append(
                Task(
                    title="Preparar clase",
                    estimated_minutes=120,
                    priority=TaskPriority.high,
                    category=TaskCategory.work,
                )
            )

        if "creatina" in normalized_text:
            tasks.append(
                Task(
                    title="Tomar creatina",
                    estimated_minutes=5,
                    priority=TaskPriority.medium,
                    category=TaskCategory.health,
                )
            )

        if not tasks:
            tasks.append(
                Task(
                    title=text.strip(),
                    estimated_minutes=30,
                )
            )

        return tasks