from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import UserRole, decode_token
from app.db.session import get_db
from app.models.domain import User
from app.schemas.auth import AuthContext


async def get_current_auth(
    authorization: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
) -> AuthContext:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = decode_token(token, expected_type="access")
        user_id = UUID(payload["sub"])
        organization_id = UUID(payload["org"])
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc

    user = await db.get(User, user_id)
    if user is None or not user.is_active or user.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
    if user.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization mismatch")

    return AuthContext(
        user_id=user.id,
        organization_id=user.organization_id,
        email=user.email,
        full_name=user.full_name,
        roles=user.roles,
    )


def require_roles(*allowed_roles: UserRole) -> Callable[[AuthContext], AuthContext]:
    def dependency(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
        if not set(auth.roles).intersection({role.value for role in allowed_roles}):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role")
        return auth

    return dependency
