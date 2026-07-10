from datetime import datetime, date, time, timedelta, timezone

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.activity_log import ActivityLog
from app.models.project import Project
from app.models.role import Role
from app.models.user import User
from app.models.weekly_report import ReportStatus, WeeklyReport


def seed_roles(db):
    roles = [
        {
            "name": "TEAM_MEMBER",
            "description": "Can create and manage own weekly reports",
        },
        {
            "name": "MANAGER",
            "description": "Can view and analyze team reports",
        },
        {
            "name": "ADMIN",
            "description": "Can manage users, roles, projects, and settings",
        },
    ]

    for role_data in roles:
        existing_role = db.query(Role).filter(Role.name == role_data["name"]).first()

        if not existing_role:
            db.add(Role(**role_data))


def seed_projects(db):
    projects = [
        {
            "name": "Internal Tooling",
            "description": "Internal systems and automation work",
            "color": "#2563EB",
        },
        {
            "name": "Client A",
            "description": "Client A delivery and support",
            "color": "#7C3AED",
        },
        {
            "name": "R&D",
            "description": "Research and experimentation",
            "color": "#16A34A",
        },
    ]

    for project_data in projects:
        existing_project = db.query(Project).filter(Project.name == project_data["name"]).first()

        if not existing_project:
            db.add(Project(**project_data))


def seed_demo_users(db):
    member_role = db.query(Role).filter(Role.name == "TEAM_MEMBER").first()
    manager_role = db.query(Role).filter(Role.name == "MANAGER").first()
    admin_role = db.query(Role).filter(Role.name == "ADMIN").first()

    demo_users = [
        {
            "full_name": "Nethmi Fernando",
            "email": "nethmi@pulseboard.com",
            "password": "Password123!",
            "role_id": member_role.id,
        },
        {
            "full_name": "Aravinda Perera",
            "email": "manager@pulseboard.com",
            "password": "Password123!",
            "role_id": manager_role.id,
        },
        {
            "full_name": "Admin User",
            "email": "admin@pulseboard.com",
            "password": "Password123!",
            "role_id": admin_role.id,
        },
    ]

    for user_data in demo_users:
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()

        if not existing_user:
            db.add(
                User(
                    full_name=user_data["full_name"],
                    email=user_data["email"],
                    password_hash=hash_password(user_data["password"]),
                    role_id=user_data["role_id"],
                    is_active=True,
                )
            )


def seed_team_members(db):
    """Additional team members so the manager dashboard and analytics look realistic."""
    member_role = db.query(Role).filter(Role.name == "TEAM_MEMBER").first()

    members = [
        {"full_name": "Kasun Silva", "email": "kasun@pulseboard.com"},
        {"full_name": "Dilani Jayawardena", "email": "dilani@pulseboard.com"},
        {"full_name": "Ruwan Bandara", "email": "ruwan@pulseboard.com"},
        {"full_name": "Ishara Gunasekara", "email": "ishara@pulseboard.com"},
    ]

    for member in members:
        existing = db.query(User).filter(User.email == member["email"]).first()
        if not existing:
            db.add(
                User(
                    full_name=member["full_name"],
                    email=member["email"],
                    password_hash=hash_password("Password123!"),
                    role_id=member_role.id,
                    is_active=True,
                )
            )


# member_email, project_name, week_index (0=current), status, is_late, hours,
# tasks_completed, tasks_planned, blockers
REPORT_SEED = [
    # ---- Current week (drives the live Manager dashboard, AI insights, and chat) ----
    ("nethmi@pulseboard.com", "Client A", 0, "SUBMITTED", False, 32,
     "Shipped the Client A onboarding flow and fixed three UAT defects.",
     "Integrate the payment webhooks and add end-to-end tests.",
     "Waiting on Client A to provide sandbox API credentials."),
    ("kasun@pulseboard.com", "Internal Tooling", 0, "SUBMITTED", False, 40,
     "Migrated the CI pipeline to the new runner and cut build time by 35%.",
     "Add a caching layer for dependency installs.",
     None),
    ("dilani@pulseboard.com", "R&D", 0, "SUBMITTED", True, 28,
     "Prototyped the vector-search spike and benchmarked two embedding models.",
     "Write up findings and present a recommendation to the team.",
     "GPU quota is exhausted, so the remaining benchmarks are queued."),
    ("ruwan@pulseboard.com", "Client A", 0, "SUBMITTED", False, 36,
     "Completed the reporting export feature and demoed it to the client.",
     "Harden error handling and add pagination to the export.",
     None),
    ("ruwan@pulseboard.com", "Internal Tooling", 0, "DRAFT", False, 6,
     "Started drafting the internal metrics dashboard.",
     "Flesh out the charts and wire up the data source.",
     None),
    # (ishara submits nothing this week -> shows as PENDING / lowers submission rate)

    # ---- Previous week (history + "what did we do last week" chat answers) ----
    ("nethmi@pulseboard.com", "Client A", 1, "SUBMITTED", False, 38,
     "Delivered the auth module and role-based access for Client A.",
     "Begin the onboarding flow.",
     None),
    ("kasun@pulseboard.com", "Internal Tooling", 1, "SUBMITTED", False, 41,
     "Set up centralized logging and alerting for the platform.",
     "Migrate CI to the new runner.",
     "Blocked on the infra team granting cloud IAM permissions."),
    ("dilani@pulseboard.com", "R&D", 1, "SUBMITTED", False, 35,
     "Surveyed embedding providers and drafted the spike plan.",
     "Run the vector-search benchmark.",
     None),
    ("ruwan@pulseboard.com", "Client A", 1, "SUBMITTED", True, 30,
     "Built the CSV export backend endpoint.",
     "Wire it to the UI and demo to the client.",
     None),
    ("ishara@pulseboard.com", "R&D", 1, "SUBMITTED", False, 33,
     "Reproduced the data-drift issue and added monitoring.",
     "Design a retraining trigger.",
     "Need access to the production feature store."),

    # ---- Two weeks ago (extra depth for trends and history) ----
    ("nethmi@pulseboard.com", "Internal Tooling", 2, "SUBMITTED", False, 40,
     "Refactored the shared component library and raised test coverage to 80%.",
     "Support the Client A auth work.",
     None),
    ("kasun@pulseboard.com", "Client A", 2, "SUBMITTED", False, 37,
     "Implemented Client A single sign-on integration.",
     "Set up centralized logging.",
     None),
    ("dilani@pulseboard.com", "R&D", 2, "SUBMITTED", False, 31,
     "Scoped the research backlog and set up the experiment tracker.",
     "Survey embedding providers.",
     "Awaiting research budget approval."),
]

ACTION_LABELS = {
    "REPORT_CREATED": "created a draft weekly report",
    "REPORT_SUBMITTED": "submitted a weekly report",
}


def _week_bounds(week_index: int) -> tuple[date, date]:
    today = date.today()
    current_start = today - timedelta(days=today.weekday())
    start = current_start - timedelta(days=7 * week_index)
    return start, start + timedelta(days=6)


def _submitted_at(week_index: int, week_end: date, is_late: bool) -> datetime:
    if week_index == 0:
        return datetime.now(timezone.utc)
    if is_late:
        return datetime.combine(week_end + timedelta(days=2), time(10, 0), tzinfo=timezone.utc)
    return datetime.combine(week_end, time(16, 0), tzinfo=timezone.utc)


def seed_weekly_reports(db):
    # Batch-idempotent: only populate reports/activity when there are none yet.
    if db.query(WeeklyReport).count() > 0:
        return

    users = {u.email: u for u in db.query(User).all()}
    projects = {p.name: p for p in db.query(Project).all()}

    for (
        email,
        project_name,
        week_index,
        status,
        is_late,
        hours,
        tasks_completed,
        tasks_planned,
        blockers,
    ) in REPORT_SEED:
        member = users.get(email)
        project = projects.get(project_name)
        if not member or not project:
            continue

        week_start, week_end = _week_bounds(week_index)
        is_submitted = status == "SUBMITTED"
        submitted_at = _submitted_at(week_index, week_end, is_late) if is_submitted else None

        report = WeeklyReport(
            user_id=member.id,
            project_id=project.id,
            week_start=week_start,
            week_end=week_end,
            tasks_completed=tasks_completed,
            tasks_planned=tasks_planned,
            blockers=blockers,
            hours_worked=hours,
            notes=None,
            status=ReportStatus.SUBMITTED if is_submitted else ReportStatus.DRAFT,
            submitted_at=submitted_at,
            is_late=is_late,
        )
        db.add(report)
        db.flush()  # assign report.id for the activity log entity_id

        created_at = (submitted_at or datetime.now(timezone.utc)) - timedelta(hours=6)
        db.add(
            ActivityLog(
                actor_id=member.id,
                action="REPORT_CREATED",
                entity_type="WEEKLY_REPORT",
                entity_id=report.id,
                details=f"{member.full_name} {ACTION_LABELS['REPORT_CREATED']} for {project.name}.",
                created_at=created_at,
            )
        )
        if is_submitted:
            db.add(
                ActivityLog(
                    actor_id=member.id,
                    action="REPORT_SUBMITTED",
                    entity_type="WEEKLY_REPORT",
                    entity_id=report.id,
                    details=f"{member.full_name} {ACTION_LABELS['REPORT_SUBMITTED']} for {project.name}.",
                    created_at=submitted_at,
                )
            )


def seed_database():
    db = SessionLocal()

    try:
        seed_roles(db)
        db.commit()

        seed_projects(db)
        db.commit()

        seed_demo_users(db)
        seed_team_members(db)
        db.commit()

        seed_weekly_reports(db)
        db.commit()

        print("Database seeded successfully")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
