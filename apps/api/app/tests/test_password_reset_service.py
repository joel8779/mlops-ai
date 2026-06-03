import pytest
from fastapi import HTTPException

from app.core.security import hash_password
from app.models.domain import Organization, User
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    VerifyResetOTPRequest,
)
from app.services.auth_service import AuthService
from app.services.password_reset_service import GENERIC_RESET_MESSAGE, PasswordResetService


class FakeRedis:
    def __init__(self) -> None:
        self.values = {}
        self.counts = {}
        self.expire_calls = []

    async def incr(self, key: str) -> int:
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def expire(self, key: str, ttl: int) -> None:
        self.expire_calls.append((key, ttl))

    async def get(self, key: str):
        return self.values.get(key)

    async def set(self, key: str, value: str, ex: int) -> None:
        self.values[key] = value

    async def delete(self, key: str) -> None:
        self.values.pop(key, None)


async def _create_verified_user(test_db, email: str = "reset@example.com", password: str = "old-password"):
    organization = Organization(name="Reset Org", slug="reset-org")
    user = User(
        organization=organization,
        email=email,
        hashed_password=hash_password(password),
        full_name="Reset User",
        roles=["recruiter"],
        otp_verified=True,
    )
    test_db.add_all([organization, user])
    await test_db.commit()
    return user


@pytest.mark.asyncio
async def test_forgot_password_sends_reset_otp_for_valid_email(test_db, monkeypatch, mock_env_vars):
    user = await _create_verified_user(test_db)
    fake_redis = FakeRedis()
    sent = []

    async def fake_send(self, email: str, otp_code: str) -> None:
        sent.append((email, otp_code))

    monkeypatch.setattr("app.services.password_reset_service.get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(PasswordResetService, "_send_reset_email", fake_send)

    response = await PasswordResetService(test_db).request_reset(ForgotPasswordRequest(email=user.email))

    assert response.message == GENERIC_RESET_MESSAGE
    assert sent and sent[0][0] == user.email
    assert len(sent[0][1]) == 6
    assert fake_redis.values[f"otp:password_reset:{user.id}"]


@pytest.mark.asyncio
async def test_forgot_password_does_not_expose_invalid_email(test_db, monkeypatch, mock_env_vars):
    fake_redis = FakeRedis()
    sent = []

    async def fake_send(self, email: str, otp_code: str) -> None:
        sent.append((email, otp_code))

    monkeypatch.setattr("app.services.password_reset_service.get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(PasswordResetService, "_send_reset_email", fake_send)

    response = await PasswordResetService(test_db).request_reset(
        ForgotPasswordRequest(email="missing@example.com")
    )

    assert response.message == GENERIC_RESET_MESSAGE
    assert sent == []


@pytest.mark.asyncio
async def test_verify_reset_otp_rejects_expired_code(test_db, monkeypatch, mock_env_vars):
    user = await _create_verified_user(test_db, email="expired-reset@example.com")
    fake_redis = FakeRedis()
    monkeypatch.setattr("app.services.password_reset_service.get_redis_client", lambda: fake_redis)

    with pytest.raises(HTTPException) as exc_info:
        await PasswordResetService(test_db).verify_reset_otp(
            VerifyResetOTPRequest(email=user.email, otp_code="123456")
        )

    assert exc_info.value.status_code == 400
    assert "invalid or expired" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_verify_reset_otp_rejects_invalid_code(test_db, monkeypatch, mock_env_vars):
    user = await _create_verified_user(test_db, email="invalid-reset@example.com")
    fake_redis = FakeRedis()
    fake_redis.values[f"otp:password_reset:{user.id}"] = hash_password("123456")
    monkeypatch.setattr("app.services.password_reset_service.get_redis_client", lambda: fake_redis)

    with pytest.raises(HTTPException) as exc_info:
        await PasswordResetService(test_db).verify_reset_otp(
            VerifyResetOTPRequest(email=user.email, otp_code="000000")
        )

    assert exc_info.value.status_code == 400
    assert fake_redis.values[f"otp:password_reset:{user.id}"]


@pytest.mark.asyncio
async def test_forgot_password_resend_is_rate_limited(test_db, monkeypatch, mock_env_vars):
    user = await _create_verified_user(test_db, email="resend-reset@example.com")
    fake_redis = FakeRedis()

    async def fake_send(self, email: str, otp_code: str) -> None:
        return None

    monkeypatch.setattr("app.services.password_reset_service.get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(PasswordResetService, "_send_reset_email", fake_send)

    service = PasswordResetService(test_db)
    await service.request_reset(ForgotPasswordRequest(email=user.email))

    with pytest.raises(HTTPException) as exc_info:
        await service.request_reset(ForgotPasswordRequest(email=user.email))

    assert exc_info.value.status_code == 429


@pytest.mark.asyncio
async def test_successful_password_reset_updates_login_and_reuses_no_otp(test_db, monkeypatch, mock_env_vars):
    user = await _create_verified_user(test_db, email="success-reset@example.com")
    fake_redis = FakeRedis()
    sent = []

    async def fake_send(self, email: str, otp_code: str) -> None:
        sent.append(otp_code)

    monkeypatch.setattr("app.services.password_reset_service.get_redis_client", lambda: fake_redis)
    monkeypatch.setattr("app.core.auth.get_redis_client", lambda: fake_redis)
    monkeypatch.setattr(PasswordResetService, "_send_reset_email", fake_send)

    service = PasswordResetService(test_db)
    await service.request_reset(ForgotPasswordRequest(email=user.email))
    verified = await service.verify_reset_otp(
        VerifyResetOTPRequest(email=user.email, otp_code=sent[0])
    )

    assert f"otp:password_reset:{user.id}" not in fake_redis.values

    await service.reset_password(
        ResetPasswordRequest(
            email=user.email,
            reset_token=verified.reset_token,
            new_password="new-password",
            confirm_password="new-password",
        )
    )

    await test_db.refresh(user)
    with pytest.raises(HTTPException):
        await AuthService(test_db).login(LoginRequest(email=user.email, password="old-password"))

    token_pair = await AuthService(test_db).login(LoginRequest(email=user.email, password="new-password"))
    assert token_pair.access_token

    with pytest.raises(HTTPException) as exc_info:
        await service.verify_reset_otp(VerifyResetOTPRequest(email=user.email, otp_code=sent[0]))
    assert exc_info.value.status_code == 400
