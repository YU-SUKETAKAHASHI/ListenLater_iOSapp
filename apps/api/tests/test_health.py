from fastapi.testclient import TestClient


def test_health_returns_database_up(api_client: TestClient) -> None:
    response = api_client.get("/health")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "up"
    assert payload["service"] == "contextcast-api"
