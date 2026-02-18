from pydantic import BaseModel, Field


class MockLoginRequest(BaseModel):
    """モックログインAPIのリクエストボディを表すスキーマ。"""

    handle: str = Field(min_length=1, max_length=64)


class TokenPairResponse(BaseModel):
    """アクセストークンとリフレッシュトークンの発行結果を表すレスポンススキーマ。"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
