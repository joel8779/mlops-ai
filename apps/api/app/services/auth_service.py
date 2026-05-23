import re
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models.domain import Organization, User
from app.repositories.users import OrganizationRepository, UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.organizations = OrganizationRepository(db)

    async def register(self, payload: RegisterRequest) -> TokenPair:
        existing = await self.users.get_by_email(payload.email)
        if existing is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

        slug = self._slugify(payload.organization_name)
        organization = await self.organizations.get_by_slug(slug)
        if organization is None:
            organization = await self.organizations.add(
                Organization(name=payload.organization_name, slug=slug)
            )

        user = await self.users.add(
            User(
                organization_id=organization.id,
                email=payload.email,
                full_name=payload.full_name,
                hashed_password=hash_password(payload.password),
                roles=["admin"],
            )
        )
        await self.db.commit()
        return self._tokens(user)

    async def login(self, payload: LoginRequest) -> TokenPair:
        user = await self.users.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return self._tokens(user)

    async def refresh(self, refresh_token: str) -> TokenPair:
        from app.core.security import decode_token

        try:
            payload = decode_token(refresh_token, expected_type="refresh")
            user = await self.db.get(User, UUID(payload["sub"]))
        except (KeyError, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
        if user is None or not user.is_active:
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
