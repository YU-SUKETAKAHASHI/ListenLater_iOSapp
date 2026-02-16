from pydantic import BaseModel, Field


class MockLoginRequest(BaseModel):
    handle: str = Field(min_length=1, max_length=64)


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
