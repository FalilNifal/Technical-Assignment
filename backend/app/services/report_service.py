from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session, joinedload

from app.models.activity_log import ActivityLog
from app.models.project import Project
from app.models.user import User
from app.models.weekly_report import ReportStatus, WeeklyReport
from app.schemas.report_schema import ReportCreateRequest, ReportUpdateRequest
from app.utils.dates import get_current_week_range, is_late_submission, validate_week_range


class ReportService:
    @staticmethod
    def _get_project_or_raise(db: Session, project_id: UUID) -> Project:
        project = (
            db.query(Project)
            .filter(Project.id == project_id, Project.is_active.is_(True))
            .first()
        )

        if not project:
            raise LookupError("Active project not found")

        return project

    @staticmethod
    def _get_report_or_raise(db: Session, report_id: UUID) -> WeeklyReport:
        report = (
            db.query(WeeklyReport)
            .options(joinedload(WeeklyReport.project))
            .filter(WeeklyReport.id == report_id)
            .first()
        )

        if not report:
            raise LookupError("Report not found")

        return report

    @staticmethod
    def _ensure_owner(report: WeeklyReport, current_user: User) -> None:
        if report.user_id != current_user.id:
            raise PermissionError("You can only access your own reports")


    @staticmethod
    def _record_report_activity(
        db: Session,
        current_user: User,
        report: WeeklyReport,
        action: str,
        project_name: str | None = None,
    ) -> None:
        project_label = project_name or (report.project.name if report.project else "Unknown project")
        action_labels = {
            "REPORT_CREATED": "created a draft weekly report",
            "REPORT_UPDATED": "updated a weekly report",
            "REPORT_SUBMITTED": "submitted a weekly report",
        }
        action_label = action_labels.get(action, "changed a weekly report")

        db.add(
            ActivityLog(
                actor_id=current_user.id,
                action=action,
                entity_type="WEEKLY_REPORT",
                entity_id=report.id,
                details=f"{current_user.full_name} {action_label} for {project_label}.",
            )
        )
    @staticmethod
    def create_report(
        db: Session,
        current_user: User,
        payload: ReportCreateRequest,
    ) -> WeeklyReport:
        validate_week_range(payload.week_start, payload.week_end)

        project = ReportService._get_project_or_raise(db, payload.project_id)

        existing_report = (
            db.query(WeeklyReport)
            .filter(
                WeeklyReport.user_id == current_user.id,
                WeeklyReport.project_id == payload.project_id,
                WeeklyReport.week_start == payload.week_start,
            )
            .first()
        )

        if existing_report:
            raise FileExistsError("A report already exists for this project and week")

        report = WeeklyReport(
            user_id=current_user.id,
            project_id=payload.project_id,
            week_start=payload.week_start,
            week_end=payload.week_end,
            tasks_completed=payload.tasks_completed,
            tasks_planned=payload.tasks_planned,
            blockers=payload.blockers,
            hours_worked=payload.hours_worked,
            notes=payload.notes,
            status=ReportStatus.DRAFT,
        )

        db.add(report)
        db.flush()
        ReportService._record_report_activity(db, current_user, report, "REPORT_CREATED", project.name)
        db.commit()
        db.refresh(report)

        return ReportService._get_report_or_raise(db, report.id)

    @staticmethod
    def update_report(
        db: Session,
        current_user: User,
        report_id: UUID,
        payload: ReportUpdateRequest,
    ) -> WeeklyReport:
        report = ReportService._get_report_or_raise(db, report_id)
        ReportService._ensure_owner(report, current_user)

        if report.status == ReportStatus.ARCHIVED:
            raise ValueError("Archived reports cannot be edited")

        if payload.project_id is not None:
            ReportService._get_project_or_raise(db, payload.project_id)

            duplicate_report = (
                db.query(WeeklyReport)
                .filter(
                    WeeklyReport.user_id == current_user.id,
                    WeeklyReport.project_id == payload.project_id,
                    WeeklyReport.week_start == report.week_start,
                    WeeklyReport.id != report.id,
                )
                .first()
            )

            if duplicate_report:
                raise FileExistsError("A report already exists for this project and week")

            report.project_id = payload.project_id

        update_data = payload.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "project_id":
                continue

            setattr(report, field, value)

        ReportService._record_report_activity(db, current_user, report, "REPORT_UPDATED")
        db.commit()
        db.refresh(report)

        return ReportService._get_report_or_raise(db, report.id)

    @staticmethod
    def submit_report(
        db: Session,
        current_user: User,
        report_id: UUID,
    ) -> WeeklyReport:
        report = ReportService._get_report_or_raise(db, report_id)
        ReportService._ensure_owner(report, current_user)

        if report.status == ReportStatus.ARCHIVED:
            raise ValueError("Archived reports cannot be submitted")

        if report.status == ReportStatus.SUBMITTED:
            raise ValueError("This report has already been submitted")

        if not report.tasks_completed.strip():
            raise ValueError("Tasks completed is required before submission")

        if not report.tasks_planned.strip():
            raise ValueError("Tasks planned is required before submission")

        submitted_at = datetime.now(timezone.utc)

        report.status = ReportStatus.SUBMITTED
        report.submitted_at = submitted_at
        report.is_late = is_late_submission(report.week_end, submitted_at)
        ReportService._record_report_activity(db, current_user, report, "REPORT_SUBMITTED")

        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def get_my_reports(
        db: Session,
        current_user: User,
        project_id: UUID | None = None,
        status: ReportStatus | None = None,
        from_date: date | None = None,
        to_date: date | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[WeeklyReport], int]:
        query = (
            db.query(WeeklyReport)
            .options(joinedload(WeeklyReport.project))
            .filter(WeeklyReport.user_id == current_user.id)
        )

        if project_id:
            query = query.filter(WeeklyReport.project_id == project_id)

        if status:
            query = query.filter(WeeklyReport.status == status)

        if from_date:
            query = query.filter(WeeklyReport.week_start >= from_date)

        if to_date:
            query = query.filter(WeeklyReport.week_end <= to_date)

        total = query.count()

        reports = (
            query.order_by(WeeklyReport.week_start.desc(), WeeklyReport.updated_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

        return reports, total

    @staticmethod
    def get_current_week_reports(
        db: Session,
        current_user: User,
        week_start: date | None = None,
    ) -> tuple[date, date, list[WeeklyReport]]:
        if week_start is None:
            week_start, week_end = get_current_week_range()
        else:
            week_end = date.fromordinal(week_start.toordinal() + 6)

        reports = (
            db.query(WeeklyReport)
            .options(joinedload(WeeklyReport.project))
            .filter(
                WeeklyReport.user_id == current_user.id,
                WeeklyReport.week_start == week_start,
            )
            .order_by(WeeklyReport.updated_at.desc())
            .all()
        )

        return week_start, week_end, reports

    @staticmethod
    def get_report_by_id(
        db: Session,
        current_user: User,
        report_id: UUID,
    ) -> WeeklyReport:
        report = ReportService._get_report_or_raise(db, report_id)
        ReportService._ensure_owner(report, current_user)

        return report

    @staticmethod
    def delete_draft_report(
        db: Session,
        current_user: User,
        report_id: UUID,
    ) -> None:
        report = ReportService._get_report_or_raise(db, report_id)
        ReportService._ensure_owner(report, current_user)

        if report.status != ReportStatus.DRAFT:
            raise ValueError("Only draft reports can be deleted")

        db.delete(report)
        db.commit()

