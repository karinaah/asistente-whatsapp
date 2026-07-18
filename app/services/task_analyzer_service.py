from datetime import date, datetime, time, timedelta

from app.config.task_analysis_rules import (
    CATEGORY_KEYWORDS,
    TIME_OF_DAY_KEYWORDS,
)
from app.models.task import (
    PreferredTimeOfDay,
    Task,
    TaskCategory,
)


class TaskAnalyzerService:
    def analyze(
        self,
        tasks: list[Task],
        reference_date: date,
    ) -> list[Task]:
        return [
            self._analyze_task(task, reference_date)
            for task in tasks
        ]

    def _analyze_task(
        self,
        task: Task,
        reference_date: date,
    ) -> Task:
        updates = {}

        inferred_category = self._infer_category(task)

        if (
            task.category == TaskCategory.other
            and inferred_category is not None
        ):
            updates["category"] = inferred_category

        inferred_deadline = self._infer_deadline(
            task,
            reference_date,
        )

        if task.deadline is None and inferred_deadline is not None:
            updates["deadline"] = inferred_deadline

        inferred_preferred_time = (
            self._infer_preferred_time_of_day(task)
        )

        if (
            task.preferred_time_of_day is None
            and inferred_preferred_time is not None
        ):
            updates["preferred_time_of_day"] = (
                inferred_preferred_time
            )

        if not updates:
            return task

        return task.model_copy(update=updates)

    def _infer_category(
        self,
        task: Task,
    ) -> TaskCategory | None:
        searchable_text = self._build_searchable_text(task)

        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return category

        return None

    def _infer_deadline(
        self,
        task: Task,
        reference_date: date,
    ) -> datetime | None:
        searchable_text = self._build_searchable_text(task)

        if "mañana" in searchable_text:
            deadline_date = reference_date + timedelta(days=1)
            return datetime.combine(
                deadline_date,
                time(hour=23, minute=59),
            )

        if "hoy" in searchable_text:
            return datetime.combine(
                reference_date,
                time(hour=23, minute=59),
            )

        return None

    def _infer_preferred_time_of_day(
        self,
        task: Task,
    ) -> PreferredTimeOfDay | None:
        searchable_text = self._build_searchable_text(task)

        for preferred_time, keywords in TIME_OF_DAY_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return preferred_time

        return None

    def _build_searchable_text(self, task: Task) -> str:
        return " ".join(
            value
            for value in (task.title, task.description)
            if value
        ).lower()