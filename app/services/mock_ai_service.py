import re

from app.models.task import Task, TaskCategory, TaskPriority


class MockAIService:
    def extract_tasks(self, text: str) -> list[Task]:
        normalized_text = text.lower()
        estimated_minutes = self._extract_duration_minutes(normalized_text)

        tasks: list[Task] = []

        if "yoga" in normalized_text:
            tasks.append(
                Task(
                    title="Hacer yoga",
                    estimated_minutes=estimated_minutes or 60,
                    priority=TaskPriority.medium,
                    category=TaskCategory.health,
                )
            )

        if "tesis" in normalized_text:
            tasks.append(
                Task(
                    title="Revisar tesis",
                    estimated_minutes=estimated_minutes or 120,
                    priority=TaskPriority.high,
                    category=TaskCategory.study,
                )
            )

        if "clase" in normalized_text:
            tasks.append(
                Task(
                    title="Preparar clase",
                    estimated_minutes=estimated_minutes or 120,
                    priority=TaskPriority.high,
                    category=TaskCategory.work,
                )
            )

        if "creatina" in normalized_text:
            tasks.append(
                Task(
                    title="Tomar creatina",
                    estimated_minutes=estimated_minutes or 5,
                    priority=TaskPriority.medium,
                    category=TaskCategory.health,
                )
            )

        clean_title = text.strip()

        urgent_meeting_match = re.search(
            r"(?:me apareció|apareció|tengo|surgió|surgio)\s+"
            r"(?:una\s+)?reunión\s+urgente",
            normalized_text,
        )

        if urgent_meeting_match:
            clean_title = "Reunión urgente"


        if not tasks:
            tasks.append(
                Task(
                    title=clean_title,
                    estimated_minutes=estimated_minutes or 30,
                )
            )

        return tasks

    def _extract_duration_minutes(self, text: str) -> int | None:
        hours_match = re.search(
            r"(\d+(?:[.,]\d+)?)\s*(?:horas?|hrs?|h)\b",
            text,
        )
        minutes_match = re.search(
            r"(\d+)\s*(?:minutos?|mins?|min)\b",
            text,
        )

        total_minutes = 0

        if hours_match:
            hours = float(hours_match.group(1).replace(",", "."))
            total_minutes += round(hours * 60)

        if minutes_match:
            total_minutes += int(minutes_match.group(1))

        return total_minutes or None