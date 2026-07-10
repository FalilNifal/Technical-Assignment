from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.permissions import require_manager_or_admin
from app.db.session import get_db
from app.models.user import User
from app.schemas.dashboard_schema import (
    ActivityTimelineResponse,
    BlockerListResponse,
    DashboardSummaryResponse,
    ProjectDistributionResponse,
    TeamMemberListResponse,
    TeamPerformanceResponse,
    TeamReportListResponse,
)
from app.services.dashboard_service import DashboardService
from app.utils.dashboard_filters import resolve_dashboard_week


router = APIRouter(prefix="/dashboard", tags=["Manager Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
)
def get_dashboard_summary(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    member_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        resolved_start, resolved_end = resolve_dashboard_week(week_start, week_end)

        return DashboardService.get_summary(
            db=db,
            week_start=resolved_start,
            week_end=resolved_end,
            project_id=project_id,
            member_id=member_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/project-distribution",
    response_model=ProjectDistributionResponse,
)
def get_project_distribution(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    member_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        resolved_start, resolved_end = resolve_dashboard_week(week_start, week_end)

        return DashboardService.get_project_distribution(
            db=db,
            week_start=resolved_start,
            week_end=resolved_end,
            member_id=member_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/team-performance",
    response_model=TeamPerformanceResponse,
)
def get_team_performance(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        resolved_start, resolved_end = resolve_dashboard_week(week_start, week_end)

        return DashboardService.get_team_performance(
            db=db,
            week_start=resolved_start,
            week_end=resolved_end,
            project_id=project_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/blockers",
    response_model=BlockerListResponse,
)
def get_blockers(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    member_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        resolved_start, resolved_end = resolve_dashboard_week(week_start, week_end)

        return DashboardService.get_blockers(
            db=db,
            week_start=resolved_start,
            week_end=resolved_end,
            project_id=project_id,
            member_id=member_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/members",
    response_model=TeamMemberListResponse,
)
def list_team_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    return DashboardService.list_team_members(db=db)


@router.get(
    "/reports",
    response_model=TeamReportListResponse,
)
def list_team_reports(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    member_id: UUID | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        resolved_start, resolved_end = resolve_dashboard_week(week_start, week_end)

        return DashboardService.list_team_reports(
            db=db,
            week_start=resolved_start,
            week_end=resolved_end,
            project_id=project_id,
            member_id=member_id,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/activity",
    response_model=ActivityTimelineResponse,
)
def get_activity_timeline(
    week_start: date | None = Query(default=None),
    week_end: date | None = Query(default=None),
    project_id: UUID | None = Query(default=None),
    member_id: UUID | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin),
):
    try:
        resolved_start, resolved_end = resolve_dashboard_week(week_start, week_end)

        return DashboardService.get_activity_timeline(
            db=db,
            week_start=resolved_start,
            week_end=resolved_end,
            project_id=project_id,
            member_id=member_id,
            limit=limit,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
