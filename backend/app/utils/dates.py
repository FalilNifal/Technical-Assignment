from datetime import date, datetime, time, timedelta, timezone


def validate_week_range(week_start: date, week_end: date) -> None:
    if week_end < week_start:
        raise ValueError("Week end must be greater than or equal to week start")

    days = (week_end - week_start).days

    if days > 6:
        raise ValueError("A weekly report range cannot exceed 7 days")


def get_report_deadline(week_end: date) -> datetime:
    """
    Production note:
    For the 48-hour implementation, reports are due on week_end at 23:59 UTC.
    Later, this should become configurable per organization/timezone.
    """
    return datetime.combine(
        week_end,
        time(hour=23, minute=59, second=59),
        tzinfo=timezone.utc,
    )


def is_late_submission(week_end: date, submitted_at: datetime) -> bool:
    deadline = get_report_deadline(week_end)

    if submitted_at.tzinfo is None:
        submitted_at = submitted_at.replace(tzinfo=timezone.utc)

    return submitted_at > deadline


def get_current_week_range() -> tuple[date, date]:
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)

    return week_start, week_end
