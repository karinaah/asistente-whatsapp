from datetime import date

from app.config.task_analysis_rules import CATEGORY_KEYWORDS
from app.models.task import Task, TaskCategory
from app.services.temporal_parser import TemporalParser


class TaskAnalyzerService:
    def __init__(
        self,
        temporal_parser: TemporalParser,
    ) -> None:
        self.temporal_parser = temporal_parser

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

        searchable_text = self._build_searchable_text(task)

        temporal_data = self.temporal_parser.parse(
            text=searchable_text,
            reference_date=reference_date,
        )

        inferred_category = self._infer_category(
            searchable_text
        )

        if (
            task.category == TaskCategory.other
            and inferred_category is not None
        ):
            updates["category"] = inferred_category

        inferred_deadline = temporal_data["deadline"]

        if (
            task.deadline is None
            and inferred_deadline is not None
        ):
            updates["deadline"] = inferred_deadline

        inferred_preferred_date = temporal_data[
            "preferred_date"
        ]

        if (
            task.preferred_date is None
            and inferred_preferred_date is not None
        ):
            updates["preferred_date"] = (
                inferred_preferred_date
            )


        inferred_preferred_time = temporal_data[
            "preferred_time_of_day"
        ]

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
        searchable_text: str,
    ) -> TaskCategory | None:
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return category

        return None

    def _build_searchable_text(
        self,
        task: Task,
    ) -> str:
        return " ".join(
            value
            for value in (
                task.title,
                task.description,
            )
            if value
        ).lower()