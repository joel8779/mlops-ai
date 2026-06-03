from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.schemas.auth import (
    AuthContext,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RefreshRequest,
    RegisterResponse,
    RegisterRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    SendOTPRequest,
    SendOTPResponse,
    TokenPair,
    UpdateOrganizationPinRequest,
    UpdateOrganizationPinResponse,
    VerifyOTPRequest,
    VerifyOTPResponse,
    VerifyResetOTPRequest,
    VerifyResetOTPResponse,
    VerifyOrganizationPinRequest,
    VerifyOrganizationPinResponse,
)
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService
from app.services.password_reset_service import PasswordResetService
from app.core.rate_limit import rate_limiter, get_client_ip

router = APIRouter()


@router.post("/register", response_model=RegisterResponse)
async def register(request: Request, payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> RegisterResponse:
    ip = get_client_ip(request)
    await rate_limiter.check_rate_limit(f"rate:register:{ip}", 3, 3600)
    return await AuthService(db).register(payload)


@router.post("/login", response_model=TokenPair)
async def login(request: Request, payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    ip = get_client_ip(request)
    await rate_limiter.check_rate_limit(f"rate:login:{ip}", 5, 60)
    return await AuthService(db).login(payload)


@router.post("/refresh", response_model=TokenPair)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)) -> TokenPair:
    return await AuthService(db).refresh(payload.refresh_token)


@router.get("/me", response_model=AuthContext)
async def me(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
    return auth


@router.post("/logout")
async def logout() -> dict[str, str]:
    return {"success": "true", "message": "Logged out successfully"}


@router.post("/verify-organization-pin", response_model=VerifyOrganizationPinResponse)
async def verify_organization_pin(payload: VerifyOrganizationPinRequest, db: AsyncSession = Depends(get_db)) -> VerifyOrganizationPinResponse:
    return await AuthService(db).verify_organization_pin(payload)


@router.post("/update-organization-pin", response_model=UpdateOrganizationPinResponse)
async def update_organization_pin(
    payload: UpdateOrganizationPinRequest,
    auth: AuthContext = Depends(get_current_auth),
    db: AsyncSession = Depends(get_db),
) -> UpdateOrganizationPinResponse:
    return await AuthService(db).update_organization_pin(auth, payload)


@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: Request, payload: SendOTPRequest, db: AsyncSession = Depends(get_db)) -> SendOTPResponse:
    email = payload.email.strip().lower()
    await rate_limiter.check_rate_limit(f"rate:send-otp:{email}", 3, 600)

    from app.repositories.users import UserRepository

    users = UserRepository(db)
    user = await users.get_by_email(payload.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await OTPService(db).create_otp(user.id)
    return SendOTPResponse(success=True, message="OTP code sent to your email")


@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp(payload: VerifyOTPRequest, db: AsyncSession = Depends(get_db)) -> VerifyOTPResponse:
    from app.repositories.users import UserRepository

    users = UserRepository(db)
    user = await users.get_by_email(payload.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await OTPService(db).verify_otp(user.id, payload.otp_code)
    return VerifyOTPResponse(success=True, message="OTP verified successfully")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: Request,
    payload: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    email = payload.email.strip().lower()
    await rate_limiter.check_rate_limit(f"rate:forgot-password:{email}", 3, 3600)
    return await PasswordResetService(db).request_reset(payload)


@router.post("/verify-reset-otp", response_model=VerifyResetOTPResponse)
async def verify_reset_otp(
    payload: VerifyResetOTPRequest,
    db: AsyncSession = Depends(get_db),
) -> VerifyResetOTPResponse:
    return await PasswordResetService(db).verify_reset_otp(payload)


@router.post("/reset-password", response_model=ResetPasswordResponse)
async def reset_password(
    payload: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ResetPasswordResponse:
    return await PasswordResetService(db).reset_password(payload)
