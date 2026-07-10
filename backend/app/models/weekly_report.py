import enum
import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, ForeignKey, Numeric, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ReportStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ARCHIVED = "ARCHIVED"


class WeeklyReport(Base):
    __tablename__ = "weekly_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    week_start = Column(Date, nullable=False, index=True)
    week_end = Column(Date, nullable=False)

    tasks_completed = Column(Text, nullable=False, default="")
    tasks_planned = Column(Text, nullable=False, default="")
    blockers = Column(Text, nullable=True)
    hours_worked = Column(Numeric(5, 2), nullable=True)
    notes = Column(Text, nullable=True)

    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.DRAFT)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    is_late = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User")
    project = relationship("Project", back_populates="reports")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "project_id",
            "week_start",
            name="uq_user_project_week_report",
        ),
    )
