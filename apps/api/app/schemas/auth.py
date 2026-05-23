from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AuthContext(BaseModel):
    user_id: UUID
    organization_id: UUID
    email: EmailStr
    roles: list[str]


class RegisterRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: UUID
    organization_id: UUID
    email: EmailStr
    full_name: str | None
    roles: list[str]

    model_config = {"from_attributes": True}
