from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    low = "baja"
    medium = "media"
    high = "alta"

class TaskEffort(str, Enum):
    low = "bajo"
    medium = "medio"
    high = "alto"

class TaskFocusDemand(str, Enum):
    low = "bajo"
    medium = "medio"
    high = "alto"

class TaskStatus(str, Enum):
    pending = "pendiente"
    in_progress = "en_progreso"
    completed = "completada"
    cancelled = "cancelada"    


class TaskCategory(str, Enum):
    work = "trabajo"
    study = "estudio"
    personal = "personal"
    health = "salud"
    errands = "tramites"
    other = "otro"

class TaskContext(str, Enum):
    work = "trabajo"
    personal = "personal"

class PreferredTimeOfDay(str, Enum):
    morning = "mañana"
    afternoon = "tarde"
    evening = "noche"

class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    estimated_minutes: int = Field(gt=0, le=1440)
    priority: TaskPriority = TaskPriority.medium
    effort: TaskEffort = TaskEffort.medium
    focus_demand: TaskFocusDemand = TaskFocusDemand.medium
    category: TaskCategory = TaskCategory.other
    context: TaskContext = TaskContext.personal 
    status: TaskStatus = TaskStatus.pending
    deadline: datetime | None = None
    preferred_date: date | None = None
    preferred_time_of_day: PreferredTimeOfDay | None = None
    preferred_start_time: time | None = None
    location: str | None = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
class TaskRequest(BaseModel):
    text: str = Field(min_length=1)


class TaskResponse(BaseModel):
    tasks: list[Task]

class ExtractedTasks(BaseModel):
    tasks: list[Task]

class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    estimated_minutes: int | None = Field(default=None, gt=0, le=1440)
    priority: TaskPriority | None = None
    effort: TaskEffort | None = None
    focus_demand: TaskFocusDemand | None = None
    category: TaskCategory | None = None
    context: TaskContext | None = None
    status: TaskStatus | None = None
    deadline: datetime | None = None
    preferred_date: date | None = None
    preferred_time_of_day: PreferredTimeOfDay | None = None
    preferred_start_time: time | None = None
    location: str | None = None

