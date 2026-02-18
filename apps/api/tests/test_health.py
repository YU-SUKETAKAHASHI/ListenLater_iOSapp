from fastapi.testclient import TestClient


def test_health_returns_database_up(api_client: TestClient) -> None:
    """
    処理内容:
        `/health` エンドポイントが正常応答し、DB状態が `up` で返ることを検証します。

    Parameters:
        api_client (TestClient): API疎通確認に利用するテストクライアント。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    response = api_client.get("/health")
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["database"] == "up"
    assert payload["service"] == "contextcast-api"
