from app.tests.conftest import client


def test_health():
    assert client.get("/health").status_code == 200
