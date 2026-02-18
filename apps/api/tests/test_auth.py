from fastapi.testclient import TestClient


def test_mock_login_returns_jwt_pair(api_client: TestClient) -> None:
    """
    処理内容:
        モックログインAPIが有効なJWTペアを返すことを検証します。

    Parameters:
        api_client (TestClient): API呼び出しに使用するテストクライアント。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    response = api_client.post("/auth/mock_login", json={"handle": "auth_tester"})
    assert response.status_code == 200, response.text

    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert isinstance(payload["access_token"], str) and payload["access_token"]
    assert isinstance(payload["refresh_token"], str) and payload["refresh_token"]
    assert payload["expires_in"] > 0


def test_mock_login_with_empty_handle_returns_422(api_client: TestClient) -> None:
    """
    処理内容:
        空のhandleでモックログインを呼ぶと422バリデーションエラーになることを検証します。

    Parameters:
        api_client (TestClient): API呼び出しに使用するテストクライアント。

    Returns:
        None: アサーションによる検証のみを行います。
    """
    response = api_client.post("/auth/mock_login", json={"handle": ""})
    assert response.status_code == 422, response.text
