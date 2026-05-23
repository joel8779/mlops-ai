from datetime import datetime, timedelta, timezone
from enum import StrEnum
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRole(StrEnum):
    admin = "admin"
    recruiter = "recruiter"
    viewer = "viewer"


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)


def create_access_token(user_id: UUID, organization_id: UUID, roles: list[str]) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return _encode_token(
        subject=user_id,
        organization_id=organization_id,
        roles=roles,
        token_type="access",
        expires_at=expires_at,
    )


def create_refresh_token(user_id: UUID, organization_id: UUID, roles: list[str]) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return _encode_token(
        subject=user_id,
        organization_id=organization_id,
        roles=roles,
        token_type="refresh",
        expires_at=expires_at,
    )


def decode_token(token: str, expected_type: str = "access") -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
    if payload.get("typ") != expected_type:
        raise ValueError("Invalid token type")
    return payload


def _encode_token(
    subject: UUID,
    organization_id: UUID,
    roles: list[str],
    token_type: str,
    expires_at: datetime,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(subject),
        "org": str(organization_id),
        "roles": roles,
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
