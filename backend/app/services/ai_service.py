from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.groq_client import GroqJSONClient
from app.ai.formatter import format_reports_for_ai
from app.ai.prompts import TEAM_INSIGHTS_SYSTEM_PROMPT, TEAM_INSIGHTS_USER_PROMPT_TEMPLATE
from app.core.config import settings
from app.models.ai_summary import AISummary
from app.models.project import Project
from app.models.user import User
from app.models.weekly_report import ReportStatus, WeeklyReport
from app.schemas.ai_schema import TeamInsightsContext, TeamInsightsResponse, TeamInsightsResponseBody


class AIService:
    @staticmethod
    def _query_reports(
        db: Session,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
        member_id: UUID | None = None,
    ) -> list[dict]:
        query = (
            db.query(
                WeeklyReport.id,
                WeeklyReport.week_start,
                WeeklyReport.week_end,
                WeeklyReport.tasks_completed,
                WeeklyReport.tasks_planned,
                WeeklyReport.blockers,
                WeeklyReport.hours_worked,
                WeeklyReport.status,
                WeeklyReport.is_late,
                User.full_name.label("member_name"),
                Project.name.label("project_name"),
            )
            .join(User, User.id == WeeklyReport.user_id)
            .join(Project, Project.id == WeeklyReport.project_id)
            .filter(
                WeeklyReport.week_start >= week_start,
                WeeklyReport.week_end <= week_end,
                WeeklyReport.status == ReportStatus.SUBMITTED,
            )
        )

        if project_id:
            query = query.filter(WeeklyReport.project_id == project_id)

        if member_id:
            query = query.filter(WeeklyReport.user_id == member_id)

        rows = query.order_by(Project.name.asc(), User.full_name.asc()).all()

        return [
            {
                "id": str(row.id),
                "week_start": str(row.week_start),
                "week_end": str(row.week_end),
                "member_name": row.member_name,
                "project_name": row.project_name,
                "tasks_completed": row.tasks_completed,
                "tasks_planned": row.tasks_planned,
                "blockers": row.blockers,
                "hours_worked": str(row.hours_worked) if row.hours_worked is not None else None,
                "status": row.status.value if hasattr(row.status, "value") else str(row.status),
                "is_late": row.is_late,
            }
            for row in rows
        ]

    @staticmethod
    def _fallback_insights(
        reports: list[dict],
        week_start: date,
        week_end: date,
        project_id: UUID | None,
        member_id: UUID | None,
    ) -> TeamInsightsResponse:
        reports_used = len(reports)
        achievements: list[str] = []
        blockers: list[str] = []
        risks: list[str] = []
        recommendations: list[str] = []

        projects = sorted({report["project_name"] for report in reports if report.get("project_name")})
        late_count = sum(1 for report in reports if report.get("is_late"))
        blocker_reports = [report for report in reports if report.get("blockers")]

        for report in reports[:5]:
            completed = report.get("tasks_completed")
            project = report.get("project_name")
            if completed:
                achievements.append(f"{project}: {completed[:180]}")

        for report in blocker_reports[:5]:
            blockers.append(
                f"{report.get('member_name')} reported a blocker in {report.get('project_name')}: "
                f"{report.get('blockers')[:180]}"
            )

        if late_count > 0:
            risks.append(f"{late_count} submitted report(s) were marked late.")

        if blocker_reports:
            risks.append("Some projects have unresolved blockers that may affect next week's progress.")

        if not reports:
            summary = "No submitted reports were found for the selected period."
            recommendations.append("Ask team members to submit their weekly reports before generating insights.")
        else:
            summary = (
                f"{reports_used} submitted report(s) were analyzed for {week_start} to {week_end}. "
                f"Work was reported across {len(projects)} project(s): "
                f"{', '.join(projects) if projects else 'No projects'}."
            )
            recommendations.append("Review reported blockers and follow up with the responsible team members.")
            recommendations.append("Use project distribution and late submission data to identify workload or process issues.")

        return TeamInsightsResponse(
            id=None,
            insights=TeamInsightsResponseBody(
                summary=summary,
                achievements=achievements[:6],
                blockers=blockers[:6],
                risks=risks[:6],
                recommendations=recommendations[:6],
            ),
            context=TeamInsightsContext(
                reports_used=reports_used,
                week_start=week_start,
                week_end=week_end,
                project_id=project_id,
                member_id=member_id,
                model_name="fallback-rule-engine",
                generated_by_fallback=True,
            ),
            created_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def generate_team_insights(
        db: Session,
        current_user: User,
        week_start: date,
        week_end: date,
        project_id: UUID | None = None,
        member_id: UUID | None = None,
    ) -> TeamInsightsResponse:
        if week_end < week_start:
            raise ValueError("week_end cannot be before week_start")

        reports = AIService._query_reports(db, week_start, week_end, project_id, member_id)

        if len(reports) == 0 or not settings.GROQ_API_KEY:
            return AIService._fallback_insights(reports, week_start, week_end, project_id, member_id)

        report_context = format_reports_for_ai(reports)
        user_prompt = TEAM_INSIGHTS_USER_PROMPT_TEMPLATE.format(
            week_start=week_start,
            week_end=week_end,
            reports_used_count=len(reports),
            report_context=report_context,
        )
        client = GroqJSONClient()

        try:
            raw_result = client.generate_json(TEAM_INSIGHTS_SYSTEM_PROMPT, user_prompt)
            insights = TeamInsightsResponseBody(
                summary=str(raw_result.get("summary", "")),
                achievements=list(raw_result.get("achievements", [])),
                blockers=list(raw_result.get("blockers", [])),
                risks=list(raw_result.get("risks", [])),
                recommendations=list(raw_result.get("recommendations", [])),
            )
            saved_summary = AISummary(
                generated_by=current_user.id,
                week_start=week_start,
                week_end=week_end,
                project_id=project_id,
                member_id=member_id,
                prompt=user_prompt,
                response=insights.model_dump(),
                model_name=settings.GROQ_MODEL,
                reports_used_count=len(reports),
            )
            db.add(saved_summary)
            db.commit()
            db.refresh(saved_summary)
            return TeamInsightsResponse(
                id=saved_summary.id,
                insights=insights,
                context=TeamInsightsContext(
                    reports_used=len(reports),
                    week_start=week_start,
                    week_end=week_end,
                    project_id=project_id,
                    member_id=member_id,
                    model_name=settings.GROQ_MODEL,
                    generated_by_fallback=False,
                ),
                created_at=saved_summary.created_at,
            )
        except Exception:
            db.rollback()
            return AIService._fallback_insights(reports, week_start, week_end, project_id, member_id)
