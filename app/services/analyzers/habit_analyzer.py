from app.models.habit_insight import HabitInsight
from app.models.task_execution import TaskExecution


class HabitAnalyzer:
    def analyze(
        self,
        executions: list[TaskExecution],
    ) -> HabitInsight:
        if not executions:
            return HabitInsight(
                executions=0,
                average_actual_minutes=0.0,
            )

        average_actual_minutes = (
            sum(
                execution.actual_minutes
                for execution in executions
            )
            / len(executions)
        )

        return HabitInsight(
            executions=len(executions),
            average_actual_minutes=round(
                average_actual_minutes,
                2,
            ),
        )