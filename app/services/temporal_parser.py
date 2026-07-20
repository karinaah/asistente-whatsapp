from datetime import date, datetime, time, timedelta
from typing import Any

from app.config.task_analysis_rules import TIME_OF_DAY_KEYWORDS
from app.models.task import PreferredTimeOfDay
import re

class TemporalParser:
    """Interpreta información temporal a partir de texto."""

    def parse(
        self,
        text: str,
        reference_date: date,
    ) -> dict[str, Any]:
        searchable_text = text.lower()

        preferred_start_time = self._infer_preferred_start_time(
            searchable_text
        )

        preferred_time_of_day = (
            self._infer_preferred_time_of_day(
                searchable_text
            )
        )

        if (
            preferred_time_of_day is None
            and preferred_start_time is not None
        ):
            preferred_time_of_day = (
                self._infer_time_of_day_from_time(
                    preferred_start_time
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
            "preferred_start_time": preferred_start_time,
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
    
    def _infer_preferred_start_time(
        self,
        searchable_text: str,
    ) -> time | None:
        pattern = (
            r"\ba\s+las?\s+"
            r"(?P<hour>\d{1,2})"
            r"(?:[:.](?P<minute>\d{2}))?"
            r"\s*(?P<period>am|pm|a\.m\.|p\.m\.)?"
            r"\b"
        )

        match = re.search(pattern, searchable_text)

        if match is None:
            return None

        hour = int(match.group("hour"))
        minute = int(match.group("minute") or 0)
        period = match.group("period")

        if minute > 59:
            return None

        if period is not None:
            normalized_period = period.replace(".", "")

            if hour < 1 or hour > 12:
                return None

            if normalized_period == "pm" and hour != 12:
                hour += 12

            if normalized_period == "am" and hour == 12:
                hour = 0

        elif hour > 23:
            return None

        return time(
            hour=hour,
            minute=minute,
        )
    
    def _infer_time_of_day_from_time(
        self,
        preferred_start_time: time,
    ) -> PreferredTimeOfDay:
        hour = preferred_start_time.hour

        if hour < 12:
            return PreferredTimeOfDay.morning

        if hour < 18:
            return PreferredTimeOfDay.afternoon

        return PreferredTimeOfDay.evening