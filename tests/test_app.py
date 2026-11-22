"""
Pytest suite for the DevOps starter app.

The test client uses an in-memory SQLite database so no real DB is needed
and the DATABASE_URL environment variable is intentionally left unset.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

# Point to an isolated in-memory DB before importing the app
os.environ.pop("DATABASE_URL", None)

from app.main import Base, app, engine as _default_engine  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    """TestClient backed by an in-memory SQLite database."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Rebind the app's metadata to the test engine
    Base.metadata.create_all(bind=test_engine)

    # Monkey-patch the module-level engine used by the route handlers
    import app.main as main_module
    original_engine = main_module.engine
    main_module.engine = test_engine

    with TestClient(app) as c:
        yield c

    # Restore original engine after the test module is done
    main_module.engine = original_engine


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_item(client):
    response = client.post("/items", json={"title": "Buy milk", "description": "2% fat"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["description"] == "2% fat"
    assert isinstance(data["id"], int)


def test_list_items_contains_created(client):
    client.post("/items", json={"title": "Walk the dog"})
    response = client.get("/items")
    assert response.status_code == 200
    titles = [item["title"] for item in response.json()]
    assert "Walk the dog" in titles


def test_create_item_blank_title_rejected(client):
    response = client.post("/items", json={"title": "   "})
    assert response.status_code == 422
