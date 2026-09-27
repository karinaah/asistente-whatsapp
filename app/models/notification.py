from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class NotificationChannel(str, Enum):
    WEB = "web"


class NotificationStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    READ = "read"
    DISMISSED = "dismissed"


class Notification(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    user_id: int

    follow_up_id: int | None = None

    title: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=1000)

    channel: NotificationChannel = NotificationChannel.WEB
    status: NotificationStatus = NotificationStatus.PENDING

    created_at: datetime = Field(default_factory=datetime.now)
    delivered_at: datetime | None = None
    read_at: datetime | None = None