from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    description: str | None = None
    color: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    description: str | None = None
    color: str | None = None
    is_active: bool | None = None


class ProjectOut(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    color: str | None = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
