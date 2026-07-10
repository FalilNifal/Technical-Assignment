from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.models.weekly_report import ReportStatus
from app.schemas.report_schema import (
    CurrentWeekReportsResponse,
    ReportCreateRequest,
    ReportListResponse,
    ReportResponse,
    ReportUpdateRequest,
    SubmitReportResponse,
)
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_report(
    payload: ReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ReportService.create_report(db, current_user, payload)

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except FileExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/me",
    response_model=ReportListResponse,
)
def get_my_reports(
    project_id: UUID | None = Query(default=None),
    report_status: ReportStatus | None = Query(default=None, alias="status"),
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reports, total = ReportService.get_my_reports(
        db=db,
        current_user=current_user,
        project_id=project_id,
        status=report_status,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        offset=offset,
    )

    return ReportListResponse(
        reports=reports,
        total=total,
    )


@router.get(
    "/me/current",
    response_model=CurrentWeekReportsResponse,
)
def get_current_week_reports(
    week_start: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resolved_week_start, resolved_week_end, reports = ReportService.get_current_week_reports(
        db=db,
        current_user=current_user,
        week_start=week_start,
    )

    return CurrentWeekReportsResponse(
        week_start=resolved_week_start,
        week_end=resolved_week_end,
        reports=reports,
    )


@router.get(
    "/{report_id}",
    response_model=ReportResponse,
)
def get_report_by_id(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ReportService.get_report_by_id(db, current_user, report_id)

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )


@router.patch(
    "/{report_id}",
    response_model=ReportResponse,
)
def update_report(
    report_id: UUID,
    payload: ReportUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return ReportService.update_report(db, current_user, report_id, payload)

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    except FileExistsError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/{report_id}/submit",
    response_model=SubmitReportResponse,
)
def submit_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        report = ReportService.submit_report(db, current_user, report_id)

        return SubmitReportResponse(
            id=report.id,
            status=report.status.value,
            submitted_at=report.submitted_at,
            is_late=report.is_late,
        )

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.delete(
    "/{report_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_draft_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        ReportService.delete_draft_report(db, current_user, report_id)
        return None

    except LookupError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(error),
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
