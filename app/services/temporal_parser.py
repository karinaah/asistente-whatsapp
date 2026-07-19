from datetime import date, datetime, time, timedelta
from typing import Any

from app.config.task_analysis_rules import TIME_OF_DAY_KEYWORDS
from app.models.task import PreferredTimeOfDay


class TemporalParser:
    """Interpreta información temporal a partir de texto."""

    def parse(
        self,
        text: str,
        reference_date: date,
    ) -> dict[str, Any]:
        searchable_text = text.lower()

        preferred_time_of_day = (
            self._infer_preferred_time_of_day(
                searchable_text
            )
        )

        deadline = self._infer_deadline(
            searchable_text,
            reference_date,
        )

        preferred_date = self._infer_preferred_date(
            searchable_text,
            reference_date,
        )

        return {
            "deadline": deadline,
            "preferred_date": preferred_date,
            "preferred_time_of_day": preferred_time_of_day,
        }

    def _infer_preferred_time_of_day(
        self,
        searchable_text: str,
    ) -> PreferredTimeOfDay | None:
        for preferred_time, keywords in TIME_OF_DAY_KEYWORDS.items():
            if any(
                keyword in searchable_text
                for keyword in keywords
            ):
                return preferred_time

        return None

    def _infer_deadline(
        self,
        searchable_text: str,
        reference_date: date,
    ) -> datetime | None:
        text_without_time_expressions = (
            self._remove_time_of_day_expressions(
                searchable_text
            )
        )

        deadline_keywords = (
            "vence",
            "fecha límite",
            "fecha limite",
            "antes de",
            "para",
        )

        has_deadline_expression = any(
            keyword in text_without_time_expressions
            for keyword in deadline_keywords
        )

        if not has_deadline_expression:
            return None

        if "pasado mañana" in text_without_time_expressions:
            deadline_date = reference_date + timedelta(days=2)

            return datetime.combine(
                deadline_date,
                time(hour=23, minute=59),
            )

        if "mañana" in text_without_time_expressions:
            deadline_date = reference_date + timedelta(days=1)

            return datetime.combine(
                deadline_date,
                time(hour=23, minute=59),
            )

        if "hoy" in text_without_time_expressions:
            return datetime.combine(
                reference_date,
                time(hour=23, minute=59),
            )

        return None

    def _infer_preferred_date(
        self,
        searchable_text: str,
        reference_date: date,
    ) -> date | None:
        text_without_time_expressions = (
            self._remove_time_of_day_expressions(
                searchable_text
            )
        )

        if "pasado mañana" in text_without_time_expressions:
            return reference_date + timedelta(days=2)

        if "mañana" in text_without_time_expressions:
            return reference_date + timedelta(days=1)

        if "hoy" in text_without_time_expressions:
            return reference_date

        return None

    def _remove_time_of_day_expressions(
        self,
        searchable_text: str,
    ) -> str:
        cleaned_text = searchable_text

        for keywords in TIME_OF_DAY_KEYWORDS.values():
            for keyword in keywords:
                cleaned_text = cleaned_text.replace(
                    keyword,
                    "",
                )

        return cleaned_text