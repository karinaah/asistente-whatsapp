from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class BlockType(str, Enum):
    TASK = "task"
    EVENT = "event"
    BREAK = "break"


class TimeBlock(BaseModel):
    start_time: datetime
    end_time: datetime
    title: str
    block_type: BlockType