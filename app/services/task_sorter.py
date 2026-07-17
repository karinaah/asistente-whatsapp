from app.models.task import Task, TaskPriority


class TaskSorter:
    priority_order = {
        TaskPriority.high: 0,
        TaskPriority.medium: 1,
        TaskPriority.low: 2,
    }

    def sort(self, tasks: list[Task]) -> list[Task]:
        return sorted(
            tasks,
            key=lambda task: (
                self.priority_order[task.priority],
                task.deadline or task.created_at,
                -task.estimated_minutes,
            ),
        )