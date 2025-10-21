from enum import Enum
from typing import Optional

from pydantic import BaseModel, field_validator


class Status(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskInput(BaseModel):
    title: str
    description: Optional[str] = None
    status: Status = Status.OPEN

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if not (1 <= len(v) <= 255):
            raise ValueError("title must be between 1 and 255 characters")
        return v


class Task(TaskInput):
    id: str
    created_at: str
    updated_at: str
