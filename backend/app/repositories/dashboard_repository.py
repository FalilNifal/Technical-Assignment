from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models.weekly_report import WeeklyReport


def reports_for_week(db: Session, week_start: date):
    return db.query(WeeklyReport).filter(WeeklyReport.week_start == week_start).all()


def trend_reports(db: Session, week_start: date):
    return db.query(WeeklyReport).filter(WeeklyReport.week_start >= week_start - timedelta(days=21)).all()
