from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class AuthContext(BaseModel):
    user_id: UUID
    organization_id: UUID
    email: EmailStr
    full_name: str | None = None
    roles: list[str]


class RegisterRequest(BaseModel):
    organization_name: str = Field(min_length=2, max_length=255)
    full_name: str = Field(min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    organization_pin: str | None = Field(None, min_length=6, max_length=6, description="PIN to join or create an organization")


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    success: bool
    message: str
    email: EmailStr
    organization_name: str
    requires_otp: bool = True


class RefreshRequest(BaseModel):
    refresh_token: str


class UserRead(BaseModel):
    id: UUID
    organization_id: UUID
    email: EmailStr
    full_name: str | None
    roles: list[str]

    model_config = {"from_attributes": True}


class VerifyOrganizationPinRequest(BaseModel):
    organization_slug: str = Field(min_length=2, max_length=120)
    organization_pin: str = Field(min_length=6, max_length=6)


class VerifyOrganizationPinResponse(BaseModel):
    valid: bool
    organization_name: str | None = None


class UpdateOrganizationPinRequest(BaseModel):
    organization_pin: str = Field(min_length=6, max_length=6, description="New 6-digit PIN for organization access")


class UpdateOrganizationPinResponse(BaseModel):
    success: bool
    message: str


class SendOTPRequest(BaseModel):
    email: EmailStr


class SendOTPResponse(BaseModel):
    success: bool
    message: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)


class VerifyOTPResponse(BaseModel):
    success: bool
    message: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    success: bool
    message: str


class VerifyResetOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str = Field(min_length=6, max_length=6)


class VerifyResetOTPResponse(BaseModel):
    success: bool
    message: str
    reset_token: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    reset_token: str = Field(min_length=32)
    new_password: str = Field(min_length=8, max_length=128)
    confirm_password: str = Field(min_length=8, max_length=128)


class ResetPasswordResponse(BaseModel):
    success: bool
    message: str
