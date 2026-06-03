import secrets
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis_client
from app.core.security import hash_password, verify_password
from app.logging import get_logger
from app.models.domain import AuditLog, User
from app.repositories.users import UserRepository
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    ResetPasswordResponse,
    VerifyResetOTPRequest,
    VerifyResetOTPResponse,
)
from app.services.email_service import EmailService, mask_email

logger = get_logger(__name__)

GENERIC_RESET_MESSAGE = "If an account exists for that email, a reset code has been sent."
INVALID_RESET_CODE_MESSAGE = "Invalid or expired reset code."
INVALID_RESET_TOKEN_MESSAGE = "Invalid or expired password reset token."


class PasswordResetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)

    async def request_reset(self, payload: ForgotPasswordRequest) -> ForgotPasswordResponse:
        email = self._normalize_email(str(payload.email))
        await self._check_request_rate_limit(email)

        user = await self.users.get_by_email(email)
        if user is None or not user.is_active:
            logger.info("password_reset_requested_unknown_email", email=mask_email(email))
            return ForgotPasswordResponse(success=True, message=GENERIC_RESET_MESSAGE)

        otp_code = self._generate_otp()
        redis_client = get_redis_client()
        await redis_client.set(
            self._reset_otp_key(user.id),
            hash_password(otp_code),
            ex=settings.otp_ttl_seconds,
        )
        await self._send_reset_email(user.email, otp_code)
        await self._audit(user, "password_reset.requested")
        await self.db.commit()

        logger.info("password_reset_otp_sent", user_id=str(user.id), email=mask_email(user.email))
        return ForgotPasswordResponse(success=True, message=GENERIC_RESET_MESSAGE)

    async def verify_reset_otp(self, payload: VerifyResetOTPRequest) -> VerifyResetOTPResponse:
        email = self._normalize_email(str(payload.email))
        await self._check_attempt_rate_limit(email)

        user = await self.users.get_by_email(email)
        if user is None or not user.is_active:
            logger.warning("password_reset_verify_unknown_email", email=mask_email(email))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_RESET_CODE_MESSAGE)

        redis_client = get_redis_client()
        stored_hash = await redis_client.get(self._reset_otp_key(user.id))
        if stored_hash is None or not verify_password(payload.otp_code, stored_hash):
            logger.warning("password_reset_invalid_otp", user_id=str(user.id), email=mask_email(user.email))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_RESET_CODE_MESSAGE)

        reset_token = secrets.token_urlsafe(32)
        await redis_client.delete(self._reset_otp_key(user.id))
        await redis_client.set(
            self._reset_grant_key(user.id),
            hash_password(reset_token),
            ex=settings.otp_ttl_seconds,
        )
        await self._audit(user, "password_reset.otp_verified")
        await self.db.commit()

        return VerifyResetOTPResponse(
            success=True,
            message="Reset code verified.",
            reset_token=reset_token,
        )

    async def reset_password(self, payload: ResetPasswordRequest) -> ResetPasswordResponse:
        if payload.new_password != payload.confirm_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Passwords do not match.")

        email = self._normalize_email(str(payload.email))
        user = await self.users.get_by_email(email)
        if user is None or not user.is_active:
            logger.warning("password_reset_unknown_email", email=mask_email(email))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_RESET_TOKEN_MESSAGE)

        redis_client = get_redis_client()
        stored_token_hash = await redis_client.get(self._reset_grant_key(user.id))
        if stored_token_hash is None or not verify_password(payload.reset_token, stored_token_hash):
            logger.warning("password_reset_invalid_token", user_id=str(user.id), email=mask_email(user.email))
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=INVALID_RESET_TOKEN_MESSAGE)

        user.hashed_password = hash_password(payload.new_password)
        await redis_client.delete(self._reset_grant_key(user.id))
        await redis_client.delete(self._reset_otp_key(user.id))
        await self.invalidate_auth_sessions(user)
        await self._audit(user, "password_reset.completed")
        await self.db.commit()

        logger.info("password_reset_completed", user_id=str(user.id), email=mask_email(user.email))
        return ResetPasswordResponse(success=True, message="Password reset successfully.")

    async def invalidate_auth_sessions(self, user: User) -> None:
        redis_client = get_redis_client()
        await redis_client.set(
            self._token_invalid_before_key(user.id),
            str(int(datetime.now(timezone.utc).timestamp())),
            ex=settings.refresh_token_expire_days * 24 * 60 * 60,
        )

    async def _send_reset_email(self, email: str, otp_code: str) -> None:
        email_service = EmailService()
        report = email_service.health_report()
        if not report["configured"]:
            logger.warning("SMTP is NOT configured! Password reset code for %s is %s", email, otp_code)
            return

        body = (
            f"Your password reset code is {otp_code}. "
            f"It expires in {settings.otp_expiry_minutes} minutes. "
            "If you did not request this, you can ignore this email."
        )
        html_body = (
            f"<html><body><p>Your password reset code is <strong>{otp_code}</strong>.</p>"
            f"<p>It expires in {settings.otp_expiry_minutes} minutes.</p>"
            "<p>If you did not request this, you can ignore this email.</p></body></html>"
        )
        await email_service.send_message_async(
            to_email=email,
            subject="Reset your password",
            body=body,
            html_body=html_body,
        )

    async def _check_request_rate_limit(self, email: str) -> None:
        redis_client = get_redis_client()
        cooldown_key = f"password_reset:cooldown:{email}"
        if await redis_client.get(cooldown_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Password reset was requested recently. Please wait before requesting another code.",
            )

        key = f"password_reset:requests:{email}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, settings.otp_ratelimit_window_seconds)
        if count > settings.otp_ratelimit_max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many password reset requests. Please try again later.",
            )
        await redis_client.set(cooldown_key, "1", ex=settings.otp_rate_limit_seconds)

    async def _check_attempt_rate_limit(self, email: str) -> None:
        redis_client = get_redis_client()
        key = f"password_reset:attempts:{email}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, settings.otp_ratelimit_window_seconds)
        if count > settings.otp_ratelimit_max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many reset attempts. Please request a new code later.",
            )

    async def _audit(self, user: User, action: str) -> None:
        self.db.add(
            AuditLog(
                organization_id=user.organization_id,
                user_id=user.id,
                action=action,
                resource_type="user",
                resource_id=str(user.id),
                payload={"email": mask_email(user.email)},
            )
        )
        await self.db.flush()

    @staticmethod
    def _generate_otp() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    @staticmethod
    def _reset_otp_key(user_id) -> str:
        return f"otp:password_reset:{user_id}"

    @staticmethod
    def _reset_grant_key(user_id) -> str:
        return f"password_reset:grant:{user_id}"

    @staticmethod
    def _token_invalid_before_key(user_id) -> str:
        return f"auth:invalid_before:{user_id}"
