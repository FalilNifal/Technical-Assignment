from typing import Any


SENSITIVE_KEYS = {
    "password",
    "password_hash",
    "token",
    "access_token",
    "refresh_token",
    "jwt",
    "secret",
    "api_key",
}


def remove_sensitive_fields(data: dict[str, Any]) -> dict[str, Any]:
    safe_data: dict[str, Any] = {}

    for key, value in data.items():
        normalized_key = key.lower()

        if normalized_key in SENSITIVE_KEYS:
            continue

        if isinstance(value, dict):
            safe_data[key] = remove_sensitive_fields(value)
        else:
            safe_data[key] = value

    return safe_data


def truncate_text(value: str | None, max_chars: int = 1200) -> str:
    if not value:
        return ""

    value = value.strip()

    if len(value) <= max_chars:
        return value

    return value[:max_chars] + "..."


def sanitize_report_for_ai(report: dict[str, Any]) -> dict[str, Any]:
    report = remove_sensitive_fields(report)

    return {
        "member_name": report.get("member_name"),
        "project_name": report.get("project_name"),
        "week_start": report.get("week_start"),
        "week_end": report.get("week_end"),
        "tasks_completed": truncate_text(report.get("tasks_completed")),
        "tasks_planned": truncate_text(report.get("tasks_planned")),
        "blockers": truncate_text(report.get("blockers")),
        "hours_worked": report.get("hours_worked"),
        "status": report.get("status"),
        "is_late": report.get("is_late"),
    }
