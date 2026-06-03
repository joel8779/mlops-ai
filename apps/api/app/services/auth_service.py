import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.domain import Organization, User
from app.repositories.users import OrganizationRepository, UserRepository
from app.schemas.auth import (
    AuthContext,
    LoginRequest,
    RegisterRequest,
    RegisterResponse,
    TokenPair,
    UpdateOrganizationPinRequest,
    UpdateOrganizationPinResponse,
    VerifyOrganizationPinRequest,
    VerifyOrganizationPinResponse,
)
from app.services.otp_service import OTPService


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.organizations = OrganizationRepository(db)

    async def register(self, payload: RegisterRequest) -> RegisterResponse:
        existing = await self.users.get_by_email(payload.email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        if not payload.organization_pin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Organization PIN is required")

        slug = self._slugify(payload.organization_name)
        organization = await self.organizations.get_by_slug(slug)

        is_new_org = organization is None
        if organization is None:
            organization = await self.organizations.add(
                Organization(name=payload.organization_name, slug=slug, organization_pin=hash_password(payload.organization_pin))
            )
            from app.models.domain import TenantQuota, SubscriptionTier
            quota = TenantQuota(
                organization_id=organization.id,
                tier=SubscriptionTier.free,
                monthly_resume_limit=500,
                monthly_llm_token_limit=250000,
                monthly_vector_query_limit=10000,
                usage_counters={},
            )
            self.db.add(quota)
        else:
            if not self._verify_pin(payload.organization_pin, organization.organization_pin):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid organization PIN")
            if organization.organization_pin == payload.organization_pin:
                organization.organization_pin = hash_password(payload.organization_pin)

        user = await self.users.add(
            User(
                organization_id=organization.id,
                email=payload.email,
                full_name=payload.full_name,
                hashed_password=hash_password(payload.password),
                roles=["admin"] if is_new_org else ["recruiter"],
                otp_verified=False,
            )
        )
        await self.db.commit()
        await OTPService(self.db).create_otp(user.id)
        return RegisterResponse(
            success=True,
            message="Account created. Check your email for the verification code.",
            email=user.email,
            organization_name=organization.name,
        )

    async def login(self, payload: LoginRequest) -> TokenPair:
        user = await self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        if not user.otp_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email verification required. Please verify your OTP code.")
        return self._tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        from app.core.auth import token_was_invalidated
        from app.core.security import decode_token

        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user = await self.db.get(User, UUID(payload["sub"]))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
        if user is None or not user.is_active or not user.otp_verified:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        if await token_was_invalidated(user.id, int(payload.get("iat", 0))):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return self._tokens(user)

    @staticmethod
    def _tokens(user: User) -> TokenPair:
        return TokenPair(
            access_token=create_access_token(user.id, user.organization_id, user.roles),
            refresh_token=create_refresh_token(user.id, user.organization_id, user.roles),
        )

    @staticmethod
    def _slugify(value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return slug or "organization"

    async def verify_organization_pin(self, payload: VerifyOrganizationPinRequest) -> VerifyOrganizationPinResponse:
        organization = await self.organizations.get_by_slug(payload.organization_slug)
        if organization is None:
            return VerifyOrganizationPinResponse(valid=False, organization_name=None)
        
        valid = self._verify_pin(payload.organization_pin, organization.organization_pin)
        if valid and organization.organization_pin == payload.organization_pin:
            organization.organization_pin = hash_password(payload.organization_pin)
            await self.db.commit()
        return VerifyOrganizationPinResponse(valid=valid, organization_name=organization.name if valid else None)

    async def update_organization_pin(
        self, auth: AuthContext, payload: UpdateOrganizationPinRequest
    ) -> UpdateOrganizationPinResponse:
        from app.schemas.auth import AuthContext as AuthContextSchema
        
        # Only admins can update organization PIN
        if "admin" not in auth.roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can update organization PIN")
        
        organization = await self.db.get(Organization, auth.organization_id)
        if organization is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        
        organization.organization_pin = hash_password(payload.organization_pin)
        await self.db.commit()
        
        return UpdateOrganizationPinResponse(success=True, message="Organization PIN updated successfully")

    @staticmethod
    def _verify_pin(raw_pin: str, stored_pin: str | None) -> bool:
        if not stored_pin:
            return False
        if stored_pin == raw_pin:
            return True
        try:
            return verify_password(raw_pin, stored_pin)
        except Exception:
            return False
