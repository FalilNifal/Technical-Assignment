from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ProjectBriefResponse(BaseModel):
    id: UUID
    name: str
    color: str | None = None

    class Config:
        from_attributes = True


class ReportCreateRequest(BaseModel):
    project_id: UUID
    week_start: date
    week_end: date

    tasks_completed: str = Field(default="", max_length=5000)
    tasks_planned: str = Field(default="", max_length=5000)
    blockers: str | None = Field(default=None, max_length=3000)
    hours_worked: Decimal | None = Field(default=None, ge=0, le=168)
    notes: str | None = Field(default=None, max_length=3000)

    @field_validator("tasks_completed", "tasks_planned")
    @classmethod
    def strip_required_text(cls, value: str) -> str:
        return value.strip() if value else ""

    @field_validator("blockers", "notes")
    @classmethod
    def strip_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()
        return stripped if stripped else None


class ReportUpdateRequest(BaseModel):
    project_id: UUID | None = None

    tasks_completed: str | None = Field(default=None, max_length=5000)
    tasks_planned: str | None = Field(default=None, max_length=5000)
    blockers: str | None = Field(default=None, max_length=3000)
    hours_worked: Decimal | None = Field(default=None, ge=0, le=168)
    notes: str | None = Field(default=None, max_length=3000)

    @field_validator("tasks_completed", "tasks_planned", "blockers", "notes")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None

        stripped = value.strip()
        return stripped if stripped else ""


class ReportMemberResponse(BaseModel):
    id: UUID
    full_name: str
    email: str

    class Config:
        from_attributes = True


class ReportResponse(BaseModel):
    id: UUID

    user_id: UUID
    project: ProjectBriefResponse

    week_start: date
    week_end: date

    tasks_completed: str
    tasks_planned: str
    blockers: str | None
    hours_worked: Decimal | None
    notes: str | None

    status: str
    submitted_at: datetime | None
    is_late: bool

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportListItemResponse(BaseModel):
    id: UUID
    project: ProjectBriefResponse

    week_start: date
    week_end: date

    status: str
    submitted_at: datetime | None
    is_late: bool
    hours_worked: Decimal | None
    updated_at: datetime

    class Config:
        from_attributes = True


class ReportListResponse(BaseModel):
    reports: list[ReportListItemResponse]
    total: int


class CurrentWeekReportsResponse(BaseModel):
    week_start: date
    week_end: date
    reports: list[ReportListItemResponse]


class SubmitReportResponse(BaseModel):
    id: UUID
    status: str
    submitted_at: datetime
    is_late: bool
