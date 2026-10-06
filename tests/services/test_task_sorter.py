from datetime import datetime

from app.models.task import Task
from app.services.task_sorter import TaskSorter


def test_task_with_deadline_is_sorted_before_task_without_deadline():
    sorter = TaskSorter()

    older_task_without_deadline = Task(
        title="Lavar ropa",
        estimated_minutes=60,
        created_at=datetime(2026, 10, 1, 10, 0),
    )

    urgent_task = Task(
        title="Código tesis",
        estimated_minutes=120,
        deadline=datetime(2026, 10, 6, 12, 0),
        created_at=datetime(2026, 10, 5, 10, 0),
    )

    result = sorter.sort(
        [
            older_task_without_deadline,
            urgent_task,
        ]
    )

    assert result[0].title == "Código tesis"
    assert result[1].title == "Lavar ropa"