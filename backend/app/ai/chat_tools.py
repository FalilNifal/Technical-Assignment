"""Tool definitions and executor for the AI chat assistant.

The LLM (Groq, via its OpenAI-compatible function-calling API) decides which of
these tools to call; each one runs server-side against the database, applies the
same privacy rules as the rest of the AI module (SUBMITTED reports only,
sanitized fields), and returns JSON back to the model.
"""
from datetime import date
from typing import Any

from sqlalchemy.orm import Session

from app.ai.safety import sanitize_report_for_ai
from app.models.project import Project
from app.models.role import Role
from app.models.user import User
from app.models.weekly_report import ReportStatus, WeeklyReport


# JSON-schema tool definitions passed to the Anthropic Messages API.
CHAT_TOOLS: list[dict[str, Any]] = [
    {
        "name": "list_projects",
        "description": "List all active projects (name and description). Use this to resolve a project or team the manager mentions (e.g. 'the design team') to a real project name before querying reports.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "list_team_members",
        "description": "List active team members (full name and email). Use this to resolve a person's name before filtering reports by member.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "query_reports",
        "description": "Fetch SUBMITTED weekly reports, optionally filtered by week range, project, and/or member. Returns completed tasks, planned tasks, blockers, hours, and lateness for each report. This is the primary source of truth for answering questions about what the team worked on.",
        "input_schema": {
            "type": "object",
            "properties": {
                "week_start": {"type": "string", "description": "Inclusive start of the week range, ISO date YYYY-MM-DD. Optional."},
                "week_end": {"type": "string", "description": "Inclusive end of the week range, ISO date YYYY-MM-DD. Optional."},
                "project_name": {"type": "string", "description": "Case-insensitive partial project name to filter by. Optional."},
                "member_name": {"type": "string", "description": "Case-insensitive partial member name to filter by. Optional."},
                "only_with_blockers": {"type": "boolean", "description": "If true, return only reports that reported a blocker. Optional."},
            },
        },
    },
    {
        "name": "get_team_summary",
        "description": "Aggregate metrics across SUBMITTED reports for an optional week range: number of reports, distinct members reporting, total hours, late count, and blocker count. Use for high-level 'how is the team doing' questions.",
        "input_schema": {
            "type": "object",
            "properties": {
                "week_start": {"type": "string", "description": "Inclusive start of the week range, ISO date YYYY-MM-DD. Optional."},
                "week_end": {"type": "string", "description": "Inclusive end of the week range, ISO date YYYY-MM-DD. Optional."},
            },
        },
    },
]


def _parse_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _base_report_query(db: Session):
    return (
        db.query(
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
        .filter(WeeklyReport.status == ReportStatus.SUBMITTED)
    )


def _apply_filters(query, tool_input: dict[str, Any]):
    week_start = _parse_date(tool_input.get("week_start"))
    week_end = _parse_date(tool_input.get("week_end"))
    project_name = tool_input.get("project_name")
    member_name = tool_input.get("member_name")

    if week_start:
        query = query.filter(WeeklyReport.week_start >= week_start)
    if week_end:
        query = query.filter(WeeklyReport.week_end <= week_end)
    if project_name:
        query = query.filter(Project.name.ilike(f"%{project_name}%"))
    if member_name:
        query = query.filter(User.full_name.ilike(f"%{member_name}%"))

    return query


def execute_chat_tool(db: Session, name: str, tool_input: dict[str, Any]) -> Any:
    if name == "list_projects":
        rows = (
            db.query(Project.name, Project.description)
            .filter(Project.is_active.is_(True))
            .order_by(Project.name.asc())
            .all()
        )
        return [{"name": r.name, "description": r.description} for r in rows]

    if name == "list_team_members":
        rows = (
            db.query(User.full_name, User.email)
            .join(Role, Role.id == User.role_id)
            .filter(Role.name == "TEAM_MEMBER", User.is_active.is_(True))
            .order_by(User.full_name.asc())
            .all()
        )
        return [{"full_name": r.full_name, "email": r.email} for r in rows]

    if name == "query_reports":
        query = _apply_filters(_base_report_query(db), tool_input)
        if tool_input.get("only_with_blockers"):
            query = query.filter(WeeklyReport.blockers.isnot(None))

        rows = query.order_by(WeeklyReport.week_start.desc()).limit(40).all()

        reports = []
        for r in rows:
            if tool_input.get("only_with_blockers") and not (r.blockers or "").strip():
                continue
            reports.append(
                sanitize_report_for_ai(
                    {
                        "member_name": r.member_name,
                        "project_name": r.project_name,
                        "week_start": str(r.week_start),
                        "week_end": str(r.week_end),
                        "tasks_completed": r.tasks_completed,
                        "tasks_planned": r.tasks_planned,
                        "blockers": r.blockers,
                        "hours_worked": str(r.hours_worked) if r.hours_worked is not None else None,
                        "status": r.status.value if hasattr(r.status, "value") else str(r.status),
                        "is_late": r.is_late,
                    }
                )
            )
        return {"count": len(reports), "reports": reports}

    if name == "get_team_summary":
        rows = _apply_filters(_base_report_query(db), tool_input).all()
        total_hours = sum(float(r.hours_worked) for r in rows if r.hours_worked is not None)
        members = {r.member_name for r in rows}
        late = sum(1 for r in rows if r.is_late)
        blockers = sum(1 for r in rows if (r.blockers or "").strip())
        return {
            "submitted_reports": len(rows),
            "distinct_members_reporting": len(members),
            "total_hours": round(total_hours, 2),
            "late_reports": late,
            "reports_with_blockers": blockers,
        }

    raise ValueError(f"Unknown tool: {name}")
