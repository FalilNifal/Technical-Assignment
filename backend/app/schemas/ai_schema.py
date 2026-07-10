from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field


class GenerateTeamInsightsRequest(BaseModel):
    week_start: date
    week_end: date
    project_id: UUID | None = None
    member_id: UUID | None = None


class TeamInsightsResponseBody(BaseModel):
    summary: str
    achievements: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class TeamInsightsContext(BaseModel):
    reports_used: int
    week_start: date
    week_end: date
    project_id: UUID | None = None
    member_id: UUID | None = None
    model_name: str | None = None
    generated_by_fallback: bool = False


class TeamInsightsResponse(BaseModel):
    id: UUID | None = None
    insights: TeamInsightsResponseBody
    context: TeamInsightsContext
    created_at: datetime | None = None


class AISummaryListItem(BaseModel):
    id: UUID
    week_start: date
    week_end: date
    project_id: UUID | None = None
    member_id: UUID | None = None
    reports_used_count: int
    model_name: str | None = None
    created_at: datetime
