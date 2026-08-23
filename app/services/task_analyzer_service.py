from datetime import date

from app.config.task_analysis_rules import (
    ACTIVITY_TYPE_KEYWORDS,
    CATEGORY_KEYWORDS,
    PRIORITY_KEYWORDS,
    WORKSPACE_KEYWORDS,
)
from app.models.task import (
    ActivityType,
    Task,
    TaskCategory,
    TaskContext,
    TaskPriority,
    TaskWorkspace,
)
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


        inferred_priority = self._infer_priority(
            searchable_text
        )

        if (
            task.priority == TaskPriority.medium
            and inferred_priority is not None
        ):
            updates["priority"] = inferred_priority



        inferred_activity_type = self._infer_activity_type(
            searchable_text
        )

        if (
            task.activity_type == ActivityType.other
            and inferred_activity_type is not None
        ):
            updates["activity_type"] = inferred_activity_type

        inferred_workspace = self._infer_workspace(
            searchable_text
        )

        if inferred_workspace is not None:
            updates["workspace"] = inferred_workspace

            if inferred_workspace == TaskWorkspace.work:
                updates["context"] = TaskContext.work
            elif inferred_workspace == TaskWorkspace.personal:
                updates["context"] = TaskContext.personal

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

        inferred_preferred_start_time = temporal_data[
            "preferred_start_time"
        ]

        if (
            task.preferred_start_time is None
            and inferred_preferred_start_time is not None
        ):
            updates["preferred_start_time"] = (
                inferred_preferred_start_time
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

    def _infer_priority(
        self,
        searchable_text: str,
    ) -> TaskPriority | None:
        for priority, keywords in PRIORITY_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return priority

        return None


    def _infer_activity_type(
        self,
        searchable_text: str,
    ) -> ActivityType | None:
        for activity_type, keywords in ACTIVITY_TYPE_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return activity_type

        return None

    def _infer_workspace(
        self,
        searchable_text: str,
    ) -> TaskWorkspace | None:
        for workspace, keywords in WORKSPACE_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return workspace

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