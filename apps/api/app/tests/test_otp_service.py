from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.domain import Organization, User
from app.schemas.auth import LoginRequest
from app.services.auth_service import AuthService
from app.services.otp_service import OTPService


class FakeRedis:
    def __init__(self, count: int) -> None:
        self.count = count
        self.expire_calls = []
        self.values = {}

    async def incr(self, key: str) -> int:
        self.count += 1
        return self.count

    async def expire(self, key: str, ttl: int) -> None:
        self.expire_calls.append((key, ttl))

    async def get(self, key: str):
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)


@pytest.mark.asyncio
async def test_create_otp_sends_email_and_tracks_pending_verification(test_db, monkeypatch, mock_env_vars):
    organization = Organization(name="Test Org", slug="test-org")
    user = User(
        organization=organization,
        email="otp@example.com",
        hashed_password=hash_password("password"),
        full_name="OTP User",
        roles=["recruiter"],
    )
    test_db.add_all([organization, user])
    await test_db.commit()

    sent = []

    async def fake_send(self, email: str, otp_code: str) -> None:
        sent.append((email, otp_code))

    monkeypatch.setattr(OTPService, "send_otp_email", fake_send)
    monkeypatch.setattr("app.services.otp_service.get_redis_client", lambda: FakeRedis(0))

    otp = await OTPService(test_db).create_otp(user.id)

    await test_db.refresh(user)

    assert len(otp) == 6
    assert user.otp_code is None
    assert user.otp_verified is False
    assert user.otp_expiry is not None
    assert sent == [(user.email, otp)]


@pytest.mark.asyncio
async def test_check_rate_limit_blocks_excess_requests(monkeypatch, mock_env_vars):
    fake_redis = FakeRedis(5)
    monkeypatch.setattr("app.services.otp_service.get_redis_client", lambda: fake_redis)

    service = OTPService(None)
    with pytest.raises(HTTPException) as exc_info:
        await service.check_rate_limit("rate@example.com")

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_login_requires_pending_otp_verification(test_db, mock_env_vars):
    organization = Organization(name="Verification Org", slug="verification-org")
    user = User(
        organization=organization,
        email="verify@example.com",
        hashed_password=hash_password("password"),
        full_name="Verify User",
        roles=["recruiter"],
        otp_code="123456",
        otp_expiry=datetime.now(timezone.utc) + timedelta(minutes=5),
        otp_verified=False,
    )
    test_db.add_all([organization, user])
    await test_db.commit()

    service = AuthService(test_db)

    with pytest.raises(HTTPException) as exc_info:
        await service.login(LoginRequest(email=user.email, password="password"))

    assert exc_info.value.status_code == 403
    assert "email verification required" in exc_info.value.detail.lower()
    assert "otp code" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_otp_rejects_expired_code(test_db, monkeypatch, mock_env_vars):
    organization = Organization(name="Expired Org", slug="expired-org")
    user = User(
        organization=organization,
        email="expired@example.com",
        hashed_password=hash_password("password"),
        full_name="Expired User",
        roles=["recruiter"],
        otp_code="999999",
        otp_expiry=datetime.now(timezone.utc) - timedelta(minutes=1),
        otp_verified=False,
    )
    test_db.add_all([organization, user])
    await test_db.commit()

    service = OTPService(test_db)
    fake_redis = FakeRedis(0)
    fake_redis.values[f"otp:verification:{user.id}"] = hash_password("999999")
    monkeypatch.setattr("app.services.otp_service.get_redis_client", lambda: fake_redis)

    with pytest.raises(HTTPException) as exc_info:
        await service.verify_otp(user.id, "999999")

    assert exc_info.value.status_code == 400
    await test_db.refresh(user)
    assert user.otp_code is None
    assert user.otp_expiry is None
    assert user.otp_verified is False
