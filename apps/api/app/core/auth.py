from datetime import datetime, timezone
from uuid import UUID

import httpx
from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwk, jwt
from jose.utils import base64url_decode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.models.domain import Organization, User
from app.schemas.auth import AuthContext

DEV_ORG_ID = UUID("00000000-0000-4000-8000-000000000001")
DEV_USER_ID = UUID("00000000-0000-4000-8000-000000000002")


async def get_current_auth(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    if settings.auth_dev_bypass:
        await ensure_dev_identity(db)
        return AuthContext(
            user_id=DEV_USER_ID,
            organization_id=DEV_ORG_ID,
            external_user_id="dev-user",
            email="recruiter@example.com",
            roles=["admin"],
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        claims = await verify_jwt(token)
    except JWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    if settings.jwt_issuer and claims.get("iss") != settings.jwt_issuer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token issuer")
    if settings.jwt_audience and settings.jwt_audience not in claims.get("aud", []):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token audience")

    external_user_id = claims.get("sub")
    email = claims.get("email")
    organization_external_id = claims.get("org_id") or claims.get("org")
    if not external_user_id or not email or not organization_external_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incomplete auth claims")

    organization = await upsert_organization(db, organization_external_id)
    user = await upsert_user(db, organization.id, external_user_id, email, claims.get("name"))

    return AuthContext(
        user_id=user.id,
        organization_id=organization.id,
        external_user_id=external_user_id,
        email=email,
        roles=claims.get("roles", []),
    )


async def verify_jwt(token: str) -> dict:
    if not settings.jwt_jwks_url:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="JWKS URL not configured")

    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get(settings.jwt_jwks_url)
        response.raise_for_status()
    key_data = next((key for key in response.json().get("keys", []) if key.get("kid") == kid), None)
    if key_data is None:
        raise JWTError("Signing key not found")

    message, encoded_signature = token.rsplit(".", 1)
    key = jwk.construct(key_data)
    signature = base64url_decode(encoded_signature.encode())
    if not key.verify(message.encode(), signature):
        raise JWTError("Signature verification failed")

    claims = jwt.get_unverified_claims(token)
    expires_at = claims.get("exp")
    if expires_at is not None and datetime.fromtimestamp(expires_at, tz=timezone.utc) < datetime.now(timezone.utc):
        raise JWTError("Token expired")
    return claims


async def ensure_dev_identity(db: AsyncSession) -> None:
    org = await db.get(Organization, DEV_ORG_ID)
    if org is None:
        db.add(Organization(id=DEV_ORG_ID, name="Development Org", external_id="dev-org"))

    user = await db.get(User, DEV_USER_ID)
    if user is None:
        db.add(
            User(
                id=DEV_USER_ID,
                organization_id=DEV_ORG_ID,
                external_id="dev-user",
                email="recruiter@example.com",
                full_name="Development Recruiter",
            )
        )
    await db.commit()


async def upsert_organization(db: AsyncSession, external_id: str) -> Organization:
    result = await db.execute(select(Organization).where(Organization.external_id == external_id))
    organization = result.scalar_one_or_none()
    if organization is not None:
        return organization

    organization = Organization(name=external_id, external_id=external_id)
    db.add(organization)
    await db.commit()
    await db.refresh(organization)
    return organization


async def upsert_user(
    db: AsyncSession, organization_id: UUID, external_id: str, email: str, full_name: str | None
) -> User:
    result = await db.execute(select(User).where(User.external_id == external_id))
    user = result.scalar_one_or_none()
    if user is not None:
        return user

    user = User(
        organization_id=organization_id,
        external_id=external_id,
        email=email,
        full_name=full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
