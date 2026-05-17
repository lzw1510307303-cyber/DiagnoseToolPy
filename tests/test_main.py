from fastapi.testclient import TestClient

from diagnose_tool.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app": "DiagnoseToolPy"}


def test_index_page() -> None:
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "DiagnoseToolPy" in response.text
    assert "diagnostic assistant" in response.text
