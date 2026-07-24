"""Pydantic schemas for Auth."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):

    identifier: str = Field(
        min_length=3,
        max_length=255,
        description="username or phone or email address",
    )
    password: str = Field(min_length=1, max_length=128)


class TokenPair(BaseModel):

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field()


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str | None = None
    all_devices: bool = False
