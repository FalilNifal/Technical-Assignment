from datetime import date, timedelta


def resolve_dashboard_week(
    week_start: date | None,
    week_end: date | None,
) -> tuple[date, date]:
    """
    If no week is provided, default to the current Monday-Sunday week.
    """

    if week_start and week_end:
        if week_end < week_start:
            raise ValueError("week_end cannot be before week_start")

        return week_start, week_end

    if week_start and not week_end:
        return week_start, week_start + timedelta(days=6)

    today = date.today()
    current_week_start = today - timedelta(days=today.weekday())
    current_week_end = current_week_start + timedelta(days=6)

    return current_week_start, current_week_end
