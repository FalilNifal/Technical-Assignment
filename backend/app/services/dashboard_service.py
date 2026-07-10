from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import and_, case, desc, distinct, func
from sqlalchemy.orm import Session

from app.models.activity_log import ActivityLog
from app.models.project import Project
from app.models.role import Role
from app.models.user import User
from app.models.weekly_report import ReportStatus, WeeklyReport
from app.schemas.dashboard_schema import (
    ActivityTimelineItem,
    ActivityTimelineResponse,
    BlockerItem,
    BlockerListResponse,
    DashboardSummaryResponse,
    ProjectDistributionItem,
    ProjectDistributionResponse,
    TeamMemberItem,
    TeamMemberListResponse,
    TeamPerformanceItem,
    TeamPerformanceResponse,
    TeamReportItem,
    TeamReportListResponse,
)


class DashboardService:
    @staticmethod
    def get_summary(
        db: Session,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
        member_id: UUID | None = None,
    ) -> DashboardSummaryResponse:
        active_members_query = (
            db.query(func.count(User.id))
            .join(Role, Role.id == User.role_id)
            .filter(
                Role.name == "TEAM_MEMBER",
                User.is_active.is_(True),
            )
        )

        if member_id:
            active_members_query = active_members_query.filter(User.id == member_id)

        total_team_members = active_members_query.scalar() or 0

        report_query = db.query(
            func.count(WeeklyReport.id).label("total_reports"),
            func.count(
                case(
                    (WeeklyReport.status == ReportStatus.SUBMITTED, 1),
                    else_=None,
                )
            ).label("submitted_reports"),
            func.count(
                case(
                    (WeeklyReport.status == ReportStatus.DRAFT, 1),
                    else_=None,
                )
            ).label("draft_reports"),
            func.count(
                case(
                    (WeeklyReport.is_late.is_(True), 1),
                    else_=None,
                )
            ).label("late_reports"),
            func.count(
                case(
                    (
                        func.length(func.trim(WeeklyReport.blockers)) > 0,
                        1,
                    ),
                    else_=None,
                )
            ).label("blocker_count"),
            func.coalesce(func.sum(WeeklyReport.hours_worked), 0).label(
                "total_hours_reported"
            ),
            func.count(distinct(WeeklyReport.user_id)).label("members_with_reports"),
            func.count(
                distinct(
                    case(
                        (
                            WeeklyReport.status == ReportStatus.SUBMITTED,
                            WeeklyReport.user_id,
                        ),
                        else_=None,
                    )
                )
            ).label("members_submitted"),
        ).filter(
            WeeklyReport.week_start >= week_start,
            WeeklyReport.week_end <= week_end,
        )

        if project_id:
            report_query = report_query.filter(WeeklyReport.project_id == project_id)

        if member_id:
            report_query = report_query.filter(WeeklyReport.user_id == member_id)

        result = report_query.one()

        total_reports = result.total_reports or 0
        submitted_reports = result.submitted_reports or 0
        draft_reports = result.draft_reports or 0
        late_reports = result.late_reports or 0
        blocker_count = result.blocker_count or 0
        total_hours_reported = result.total_hours_reported or Decimal("0")
        members_submitted = result.members_submitted or 0

        pending_members = max(total_team_members - members_submitted, 0)

        submission_percentage = (
            round((members_submitted / total_team_members) * 100, 2)
            if total_team_members > 0
            else 0.0
        )

        return DashboardSummaryResponse(
            week_start=week_start,
            week_end=week_end,
            total_team_members=total_team_members,
            total_reports=total_reports,
            submitted_reports=submitted_reports,
            draft_reports=draft_reports,
            late_reports=late_reports,
            pending_members=pending_members,
            submission_percentage=submission_percentage,
            blocker_count=blocker_count,
            total_hours_reported=total_hours_reported,
        )

    @staticmethod
    def get_project_distribution(
        db: Session,
        week_start: date,
        week_end: date,
        member_id: UUID | None = None,
    ) -> ProjectDistributionResponse:
        query = (
            db.query(
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                Project.color.label("project_color"),
                func.count(WeeklyReport.id).label("report_count"),
                func.count(
                    case(
                        (WeeklyReport.status == ReportStatus.SUBMITTED, 1),
                        else_=None,
                    )
                ).label("submitted_count"),
                func.count(
                    case(
                        (
                            func.length(func.trim(WeeklyReport.blockers)) > 0,
                            1,
                        ),
                        else_=None,
                    )
                ).label("blocker_count"),
                func.coalesce(func.sum(WeeklyReport.hours_worked), 0).label(
                    "total_hours"
                ),
            )
            .join(WeeklyReport, WeeklyReport.project_id == Project.id)
            .filter(
                WeeklyReport.week_start >= week_start,
                WeeklyReport.week_end <= week_end,
            )
        )

        if member_id:
            query = query.filter(WeeklyReport.user_id == member_id)

        rows = (
            query.group_by(Project.id, Project.name, Project.color)
            .order_by(desc("total_hours"), desc("report_count"))
            .all()
        )

        return ProjectDistributionResponse(
            items=[
                ProjectDistributionItem(
                    project_id=row.project_id,
                    project_name=row.project_name,
                    project_color=row.project_color,
                    report_count=row.report_count or 0,
                    submitted_count=row.submitted_count or 0,
                    blocker_count=row.blocker_count or 0,
                    total_hours=row.total_hours or Decimal("0"),
                )
                for row in rows
            ]
        )

    @staticmethod
    def get_team_performance(
        db: Session,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
    ) -> TeamPerformanceResponse:
        report_join_conditions = [
            WeeklyReport.user_id == User.id,
            WeeklyReport.week_start >= week_start,
            WeeklyReport.week_end <= week_end,
        ]

        if project_id:
            report_join_conditions.append(WeeklyReport.project_id == project_id)

        query = (
            db.query(
                User.id.label("member_id"),
                User.full_name.label("member_name"),
                User.email.label("member_email"),
                func.count(WeeklyReport.id).label("report_count"),
                func.count(
                    case(
                        (WeeklyReport.status == ReportStatus.SUBMITTED, 1),
                        else_=None,
                    )
                ).label("submitted_count"),
                func.count(
                    case(
                        (WeeklyReport.status == ReportStatus.DRAFT, 1),
                        else_=None,
                    )
                ).label("draft_count"),
                func.count(
                    case(
                        (WeeklyReport.is_late.is_(True), 1),
                        else_=None,
                    )
                ).label("late_count"),
                func.count(
                    case(
                        (
                            func.length(func.trim(WeeklyReport.blockers)) > 0,
                            1,
                        ),
                        else_=None,
                    )
                ).label("blocker_count"),
                func.coalesce(func.sum(WeeklyReport.hours_worked), 0).label(
                    "total_hours"
                ),
                func.max(WeeklyReport.submitted_at).label("last_submitted_at"),
            )
            .join(Role, Role.id == User.role_id)
            .outerjoin(WeeklyReport, and_(*report_join_conditions))
            .filter(
                Role.name == "TEAM_MEMBER",
                User.is_active.is_(True),
            )
            .group_by(User.id, User.full_name, User.email)
            .order_by(User.full_name.asc())
        )

        rows = query.all()

        items: list[TeamPerformanceItem] = []

        for row in rows:
            report_count = row.report_count or 0
            submitted_count = row.submitted_count or 0
            draft_count = row.draft_count or 0
            late_count = row.late_count or 0

            if submitted_count > 0 and late_count > 0:
                submission_status = "LATE"
            elif submitted_count > 0:
                submission_status = "SUBMITTED"
            elif draft_count > 0:
                submission_status = "DRAFT"
            else:
                submission_status = "PENDING"

            items.append(
                TeamPerformanceItem(
                    member_id=row.member_id,
                    member_name=row.member_name,
                    member_email=row.member_email,
                    report_count=report_count,
                    submitted_count=submitted_count,
                    draft_count=draft_count,
                    late_count=late_count,
                    blocker_count=row.blocker_count or 0,
                    total_hours=row.total_hours or Decimal("0"),
                    submission_status=submission_status,
                    last_submitted_at=row.last_submitted_at,
                )
            )

        return TeamPerformanceResponse(items=items)

    @staticmethod
    def get_blockers(
        db: Session,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
        member_id: UUID | None = None,
    ) -> BlockerListResponse:
        query = (
            db.query(
                WeeklyReport.id.label("report_id"),
                User.id.label("member_id"),
                User.full_name.label("member_name"),
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                WeeklyReport.blockers.label("blockers"),
                WeeklyReport.week_start.label("week_start"),
                WeeklyReport.week_end.label("week_end"),
                WeeklyReport.submitted_at.label("submitted_at"),
            )
            .join(User, User.id == WeeklyReport.user_id)
            .join(Project, Project.id == WeeklyReport.project_id)
            .filter(
                WeeklyReport.week_start >= week_start,
                WeeklyReport.week_end <= week_end,
                WeeklyReport.blockers.isnot(None),
                func.length(func.trim(WeeklyReport.blockers)) > 0,
            )
        )

        if project_id:
            query = query.filter(WeeklyReport.project_id == project_id)

        if member_id:
            query = query.filter(WeeklyReport.user_id == member_id)

        rows = query.order_by(WeeklyReport.updated_at.desc()).all()

        return BlockerListResponse(
            items=[
                BlockerItem(
                    report_id=row.report_id,
                    member_id=row.member_id,
                    member_name=row.member_name,
                    project_id=row.project_id,
                    project_name=row.project_name,
                    blockers=row.blockers,
                    week_start=row.week_start,
                    week_end=row.week_end,
                    submitted_at=row.submitted_at,
                )
                for row in rows
            ]
        )

    @staticmethod
    def get_activity_timeline(
        db: Session,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
        member_id: UUID | None = None,
        limit: int = 20,
    ) -> ActivityTimelineResponse:
        query = (
            db.query(
                ActivityLog.id.label("activity_id"),
                ActivityLog.action.label("action"),
                ActivityLog.details.label("details"),
                ActivityLog.created_at.label("created_at"),
                User.id.label("actor_id"),
                User.full_name.label("actor_name"),
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                WeeklyReport.id.label("report_id"),
            )
            .outerjoin(User, User.id == ActivityLog.actor_id)
            .join(WeeklyReport, WeeklyReport.id == ActivityLog.entity_id)
            .join(Project, Project.id == WeeklyReport.project_id)
            .filter(
                ActivityLog.entity_type == "WEEKLY_REPORT",
                WeeklyReport.week_start >= week_start,
                WeeklyReport.week_end <= week_end,
            )
        )

        if project_id:
            query = query.filter(WeeklyReport.project_id == project_id)

        if member_id:
            query = query.filter(WeeklyReport.user_id == member_id)

        rows = query.order_by(desc(ActivityLog.created_at)).limit(limit).all()
        title_map = {
            "REPORT_CREATED": "Report draft created",
            "REPORT_UPDATED": "Report updated",
            "REPORT_SUBMITTED": "Report submitted",
        }

        items = [
            ActivityTimelineItem(
                id=row.activity_id,
                type=row.action,
                title=title_map.get(row.action, "Report activity"),
                description=row.details or title_map.get(row.action, "Report activity"),
                actor_id=row.actor_id,
                actor_name=row.actor_name,
                project_id=row.project_id,
                project_name=row.project_name,
                report_id=row.report_id,
                created_at=row.created_at,
            )
            for row in rows
        ]

        return ActivityTimelineResponse(items=items)

    @staticmethod
    def list_team_members(db: Session) -> TeamMemberListResponse:
        rows = (
            db.query(User.id, User.full_name, User.email)
            .join(Role, Role.id == User.role_id)
            .filter(Role.name == "TEAM_MEMBER", User.is_active.is_(True))
            .order_by(User.full_name.asc())
            .all()
        )

        return TeamMemberListResponse(
            items=[
                TeamMemberItem(member_id=row.id, member_name=row.full_name, member_email=row.email)
                for row in rows
            ]
        )

    @staticmethod
    def list_team_reports(
        db: Session,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
        member_id: UUID | None = None,
    ) -> TeamReportListResponse:
        query = (
            db.query(
                WeeklyReport.id.label("report_id"),
                User.id.label("member_id"),
                User.full_name.label("member_name"),
                Project.id.label("project_id"),
                Project.name.label("project_name"),
                Project.color.label("project_color"),
                WeeklyReport.week_start,
                WeeklyReport.week_end,
                WeeklyReport.tasks_completed,
                WeeklyReport.tasks_planned,
                WeeklyReport.blockers,
                WeeklyReport.hours_worked,
                WeeklyReport.notes,
                WeeklyReport.status,
                WeeklyReport.is_late,
                WeeklyReport.submitted_at,
            )
            .join(User, User.id == WeeklyReport.user_id)
            .join(Project, Project.id == WeeklyReport.project_id)
            .filter(
                WeeklyReport.week_start >= week_start,
                WeeklyReport.week_end <= week_end,
            )
        )

        if project_id:
            query = query.filter(WeeklyReport.project_id == project_id)

        if member_id:
            query = query.filter(WeeklyReport.user_id == member_id)

        rows = query.order_by(
            WeeklyReport.week_start.desc(), User.full_name.asc()
        ).all()

        items = [
            TeamReportItem(
                report_id=row.report_id,
                member_id=row.member_id,
                member_name=row.member_name,
                project_id=row.project_id,
                project_name=row.project_name,
                project_color=row.project_color,
                week_start=row.week_start,
                week_end=row.week_end,
                tasks_completed=row.tasks_completed,
                tasks_planned=row.tasks_planned,
                blockers=row.blockers,
                hours_worked=row.hours_worked,
                notes=row.notes,
                status=row.status.value if hasattr(row.status, "value") else str(row.status),
                is_late=row.is_late,
                submitted_at=row.submitted_at,
            )
            for row in rows
        ]

        return TeamReportListResponse(items=items, total=len(items))
