"""Pytest fixtures: an isolated PostgreSQL test database with per-test rollback.

Each test runs inside a transaction that is rolled back on teardown, so tests
never pollute data and never collide with seeded rows. The `client` fixture
shares the same session with the app via a `get_db` dependency override.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.database import Base
from app.db.session import get_db
from app.main import app  # noqa: F401 — importing populates Base.metadata with every model


def _split_url(url: str) -> tuple[str, str]:
    base, _, name = url.rpartition("/")
    return base, name.split("?")[0]


_BASE, _NAME = _split_url(settings.DATABASE_URL)
TEST_DB_NAME = f"{_NAME}_test"
TEST_DATABASE_URL = f"{_BASE}/{TEST_DB_NAME}"


def _ensure_test_database() -> None:
    """Create the test database once, if it doesn't already exist."""
    admin = create_engine(f"{_BASE}/postgres", isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": TEST_DB_NAME},
        ).scalar()
        if not exists:
            conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    admin.dispose()


_ensure_test_database()
test_engine = create_engine(TEST_DATABASE_URL)
Base.metadata.create_all(bind=test_engine)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db():
    connection = test_engine.connect()
    transaction = connection.begin()
    # create_savepoint => the app's commits become savepoints inside our outer
    # transaction, so the final rollback still undoes everything.
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
