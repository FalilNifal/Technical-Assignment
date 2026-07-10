from datetime import date
from sqlalchemy.orm import Session
from app.models.weekly_report import WeeklyReport


def get_report(db: Session, report_id: int) -> WeeklyReport | None:
    return db.get(WeeklyReport, report_id)


def list_reports(db: Session, week_start: date | None = None, user_id: int | None = None, project_id: int | None = None):
    query = db.query(WeeklyReport)
    if week_start:
        query = query.filter(WeeklyReport.week_start == week_start)
    if user_id:
        query = query.filter(WeeklyReport.user_id == user_id)
    if project_id:
        query = query.filter(WeeklyReport.project_id == project_id)
    return query.order_by(WeeklyReport.week_start.desc(), WeeklyReport.updated_at.desc()).all()
