from app.ai.safety import sanitize_report_for_ai


def format_reports_for_ai(raw_reports: list[dict]) -> str:
    safe_reports = [sanitize_report_for_ai(report) for report in raw_reports]

    sections: list[str] = []

    for index, report in enumerate(safe_reports, start=1):
        section = f"""
Report {index}
Member: {report.get("member_name")}
Project: {report.get("project_name")}
Week: {report.get("week_start")} to {report.get("week_end")}
Status: {report.get("status")}
Late: {report.get("is_late")}
Hours worked: {report.get("hours_worked")}

Tasks completed:
{report.get("tasks_completed") or "None provided"}

Tasks planned:
{report.get("tasks_planned") or "None provided"}

Blockers:
{report.get("blockers") or "None reported"}
""".strip()

        sections.append(section)

    return "\n\n---\n\n".join(sections)
