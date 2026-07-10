from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class DashboardSummaryResponse(BaseModel):
    week_start: date
    week_end: date

    total_team_members: int
    total_reports: int
    submitted_reports: int
    draft_reports: int
    late_reports: int
    pending_members: int

    submission_percentage: float
    blocker_count: int
    total_hours_reported: Decimal


class ProjectDistributionItem(BaseModel):
    project_id: UUID
    project_name: str
    project_color: str | None = None
    report_count: int
    submitted_count: int
    blocker_count: int
    total_hours: Decimal


class ProjectDistributionResponse(BaseModel):
    items: list[ProjectDistributionItem]


class ActivityTimelineItem(BaseModel):
    id: UUID
    type: str
    title: str
    description: str
    actor_id: UUID | None = None
    actor_name: str | None = None
    project_id: UUID | None = None
    project_name: str | None = None
    report_id: UUID | None = None
    created_at: datetime


class ActivityTimelineResponse(BaseModel):
    items: list[ActivityTimelineItem]


class TeamPerformanceItem(BaseModel):
    member_id: UUID
    member_name: str
    member_email: str

    report_count: int
    submitted_count: int
    draft_count: int
    late_count: int
    blocker_count: int
    total_hours: Decimal

    submission_status: str
    last_submitted_at: datetime | None = None


class TeamPerformanceResponse(BaseModel):
    items: list[TeamPerformanceItem]


class BlockerItem(BaseModel):
    report_id: UUID
    member_id: UUID
    member_name: str
    project_id: UUID
    project_name: str
    blockers: str
    week_start: date
    week_end: date
    submitted_at: datetime | None


class BlockerListResponse(BaseModel):
    items: list[BlockerItem]


class TeamMemberItem(BaseModel):
    member_id: UUID
    member_name: str
    member_email: str


class TeamMemberListResponse(BaseModel):
    items: list[TeamMemberItem]


class TeamReportItem(BaseModel):
    report_id: UUID
    member_id: UUID
    member_name: str
    project_id: UUID
    project_name: str
    project_color: str | None = None
    week_start: date
    week_end: date
    tasks_completed: str
    tasks_planned: str
    blockers: str | None = None
    hours_worked: Decimal | None = None
    notes: str | None = None
    status: str
    is_late: bool
    submitted_at: datetime | None = None


class TeamReportListResponse(BaseModel):
    items: list[TeamReportItem]
    total: int
