from datetime import datetime

from app.models.time_block import BlockType, TimeBlock


def make_time_block(
    start: str,
    end: str,
    *,
    date: str = "2025-07-20",
    title: str = "Bloque ocupado",
    block_type: BlockType = BlockType.EVENT,
) -> TimeBlock:
    return TimeBlock(
        start_time=datetime.fromisoformat(
            f"{date}T{start}:00"
        ),
        end_time=datetime.fromisoformat(
            f"{date}T{end}:00"
        ),
        title=title,
        block_type=block_type,
    )