from fastapi.testclient import TestClient
from app.main import app
def test_version_endpoint():
    response = TestClient(app).get("/version")
    assert response.status_code == 200
    assert "version" in response.json()
