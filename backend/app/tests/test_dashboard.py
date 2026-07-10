from datetime import date, timedelta

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.project import Project
from app.models.role import Role
from app.models.user import User


def create_user(db: Session, email: str, role_name: str) -> User:
    role = db.query(Role).filter(Role.name == role_name).first()

    if not role:
        role = Role(name=role_name, description=role_name)
        db.add(role)
        db.commit()
        db.refresh(role)

    user = User(
        full_name=email.split("@")[0].title(),
        email=email,
        password_hash=hash_password("Password123!"),
        role_id=role.id,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_project(db: Session) -> Project:
    project = Project(
        name="Internal Tooling",
        description="Internal work",
        color="#2563EB",
        is_active=True,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def login(client: TestClient, email: str) -> str:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": "Password123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_team_member_cannot_access_dashboard(
    client: TestClient,
    db: Session,
):
    member = create_user(db, "member-dashboard-test@example.com", "TEAM_MEMBER")
    token = login(client, member.email)

    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403


def test_manager_can_access_dashboard_summary(
    client: TestClient,
    db: Session,
):
    manager = create_user(db, "manager-dashboard-test@example.com", "MANAGER")
    token = login(client, manager.email)

    response = client.get(
        "/api/v1/dashboard/summary",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert "total_team_members" in body
    assert "total_reports" in body
    assert "submission_percentage" in body
    assert "blocker_count" in body


def test_manager_can_access_project_distribution(
    client: TestClient,
    db: Session,
):
    manager = create_user(db, "manager-project-distribution@example.com", "MANAGER")
    token = login(client, manager.email)

    response = client.get(
        "/api/v1/dashboard/project-distribution",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert isinstance(body["items"], list)


def test_manager_can_access_team_performance(
    client: TestClient,
    db: Session,
):
    manager = create_user(db, "manager-team-performance@example.com", "MANAGER")
    create_user(db, "member-team-performance@example.com", "TEAM_MEMBER")

    token = login(client, manager.email)

    response = client.get(
        "/api/v1/dashboard/team-performance",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert isinstance(body["items"], list)

    if body["items"]:
        first_item = body["items"][0]
        assert "member_id" in first_item
        assert "submission_status" in first_item


def test_manager_can_access_blockers(
    client: TestClient,
    db: Session,
):
    manager = create_user(db, "manager-blockers@example.com", "MANAGER")
    token = login(client, manager.email)

    response = client.get(
        "/api/v1/dashboard/blockers",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    body = response.json()

    assert "items" in body
    assert isinstance(body["items"], list)


def test_invalid_dashboard_date_range_returns_400(
    client: TestClient,
    db: Session,
):
    manager = create_user(db, "manager-invalid-date@example.com", "MANAGER")
    token = login(client, manager.email)

    today = date.today()
    week_start = today
    week_end = today - timedelta(days=7)

    response = client.get(
        f"/api/v1/dashboard/summary?week_start={week_start}&week_end={week_end}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 400
