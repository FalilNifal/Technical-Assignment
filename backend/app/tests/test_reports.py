from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.project import Project
from app.models.role import Role
from app.models.user import User
from app.models.weekly_report import WeeklyReport


@pytest.fixture
def team_member(db: Session):
    role = db.query(Role).filter(Role.name == "TEAM_MEMBER").first()

    if not role:
        role = Role(name="TEAM_MEMBER", description="Team member")
        db.add(role)
        db.commit()
        db.refresh(role)

    user = User(
        full_name="Test Member",
        email="testmember@example.com",
        password_hash=hash_password("Password123!"),
        role_id=role.id,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def second_member(db: Session):
    role = db.query(Role).filter(Role.name == "TEAM_MEMBER").first()

    user = User(
        full_name="Second Member",
        email="secondmember@example.com",
        password_hash=hash_password("Password123!"),
        role_id=role.id,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def project(db: Session):
    project = Project(
        name="Internal Tooling",
        description="Internal tooling work",
        color="#2563EB",
        is_active=True,
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


def login_and_get_token(client: TestClient, email: str, password: str):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def test_create_report_success(client: TestClient, team_member: User, project: Project):
    token = login_and_get_token(client, team_member.email, "Password123!")

    week_start = date.today()
    week_end = week_start + timedelta(days=6)

    response = client.post(
        "/api/v1/reports",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "project_id": str(project.id),
            "week_start": str(week_start),
            "week_end": str(week_end),
            "tasks_completed": "Completed auth module.",
            "tasks_planned": "Build report module.",
            "blockers": "None",
            "hours_worked": 30,
            "notes": "Good progress.",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["tasks_completed"] == "Completed auth module."
    assert body["status"] == "DRAFT"
    assert body["project"]["id"] == str(project.id)


def test_reports_checklist_placeholder():
    assert WeeklyReport is not None
