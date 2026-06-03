import random
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.redis import get_redis_client
from app.core.security import hash_password, verify_password
from app.logging import get_logger
from app.models.domain import User
from app.services.email_service import EmailService, mask_email

logger = get_logger(__name__)


class OTPService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @staticmethod
    def generate_otp() -> str:
        """Generate a 6-digit OTP code."""
        return "".join([str(random.randint(0, 9)) for _ in range(6)])

    async def send_otp_email(self, email: str, otp_code: str) -> None:
        """Send OTP code via email using SMTP."""
        email_service = EmailService()
        smtp_report = email_service.health_report()
        if not smtp_report["configured"]:
            logger.warning("SMTP is NOT configured! OTP code for %s is %s", email, otp_code)
            return

        try:
            body = (
                f"Your verification code is {otp_code}. It expires in {settings.otp_expiry_minutes} minutes."
            )
            html_body = (
                f"<html><body><p>Your verification code is <strong>{otp_code}</strong>.</p>"
                f"<p>It expires in {settings.otp_expiry_minutes} minutes.</p></body></html>"
            )
            await email_service.send_message_async(
                to_email=email,
                subject="Your verification code",
                body=body,
                html_body=html_body,
            )
            logger.info("otp_email_sent", email=mask_email(email), message="OTP code sent successfully")
        except Exception as exc:
            logger.error("otp_email_send_failed", email=mask_email(email), error=str(exc))
            raise

    async def create_otp(self, user_id: UUID) -> str:
        """Create and store OTP for a user."""
        user = await self.db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        await self.check_rate_limit(user.email)

        otp_code = self.generate_otp()
        otp_expiry = datetime.now(timezone.utc) + timedelta(seconds=settings.otp_ttl_seconds)

        redis_client = get_redis_client()
        await redis_client.set(self._otp_key(user.id), hash_password(otp_code), ex=settings.otp_ttl_seconds)

        user.otp_code = None
        user.otp_expiry = otp_expiry
        user.otp_verified = False
        await self.db.commit()

        await self.send_otp_email(user.email, otp_code)

        return otp_code

    async def verify_otp(self, user_id: UUID, otp_code: str) -> bool:
        """Verify OTP code for a user."""
        user = await self.db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        redis_client = get_redis_client()
        stored_hash = await redis_client.get(self._otp_key(user.id))
        if stored_hash is None:
            user.otp_code = None
            user.otp_expiry = None
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP code generated. Please request a new OTP.")

        if user.otp_expiry and user.otp_expiry < datetime.now(timezone.utc):
            await redis_client.delete(self._otp_key(user.id))
            user.otp_code = None
            user.otp_expiry = None
            user.otp_verified = False
            await self.db.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP code has expired. Please request a new OTP.")

        if not verify_password(otp_code, stored_hash):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid OTP code.")

        user.otp_verified = True
        user.otp_code = None
        user.otp_expiry = None
        await redis_client.delete(self._otp_key(user.id))
        await self.db.commit()

        logger.info(
            "otp_verified",
            user_id=str(user_id),
            email=mask_email(user.email),
        )

        return True

    async def check_rate_limit(self, email: str) -> None:
        """Check rate limit for OTP requests using Redis."""
        redis_client = get_redis_client()
        resend_key = f"otp_resend_cooldown:{email}"
        if await redis_client.get(resend_key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="OTP was requested recently. Please wait before requesting another code.",
            )

        key = f"otp_rate_limit:{email}"
        count = await redis_client.incr(key)
        if count == 1:
            await redis_client.expire(key, settings.otp_ratelimit_window_seconds)
        if count > settings.otp_ratelimit_max_requests:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many OTP requests. Please try again later.",
            )
        await redis_client.set(resend_key, "1", ex=settings.otp_rate_limit_seconds)

    @staticmethod
    def _otp_key(user_id: UUID) -> str:
        return f"otp:verification:{user_id}"
