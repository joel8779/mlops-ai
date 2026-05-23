from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import AuditLog
from app.schemas.auth import AuthContext


async def write_audit_log(
    db: AsyncSession,
    request: Request,
    auth: AuthContext | None,
    action: str,
    resource_type: str,
    resource_id: str | None = None,
    payload: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            organization_id=auth.organization_id if auth else None,
            user_id=auth.user_id if auth else None,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            payload=payload or {},
        )
    )
    await db.commit()
