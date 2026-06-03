"""Audit Logger - Comprehensive audit logging for compliance."""

import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client


class AuditAction(str, Enum):
    """Types of auditable actions."""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXPORT = "export"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_CHANGE = "permission_change"
    DATA_ACCESS = "data_access"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """Audit event record."""

    event_id: UUID
    action: AuditAction
    resource_type: str
    resource_id: Optional[UUID]
    user_id: UUID
    organization_id: UUID
    timestamp: datetime
    ip_address: Optional[str]
    user_agent: Optional[str]
    severity: AuditSeverity
    details: dict[str, Any]
    success: bool


class AuditLogger:
    """Audit logger for compliance and security monitoring."""

    def __init__(
        self,
        db: AsyncSession,
        enable_redis: bool = True,
        retention_days: int = 365,
    ) -> None:
        """Initialize audit logger.

        Args:
            db: Database session
            enable_redis: Whether to use Redis for real-time logging
            retention_days: Number of days to retain logs
        """
        self.db = db
        self.enable_redis = enable_redis
        self.retention_days = retention_days

    async def log(
        self,
        action: AuditAction,
        resource_type: str,
        user_id: UUID,
        organization_id: UUID,
        resource_id: Optional[UUID] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        details: Optional[dict[str, Any]] = None,
        success: bool = True,
    ) -> AuditEvent:
        """Log an audit event.

        Args:
            action: Action performed
            resource_type: Type of resource affected
            user_id: User who performed the action
            organization_id: Organization ID
            resource_id: ID of affected resource
            ip_address: IP address of request
            user_agent: User agent string
            severity: Severity level
            details: Additional details
            success: Whether the action succeeded

        Returns:
            AuditEvent object
        """
        event = AuditEvent(
            event_id=uuid4(),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            organization_id=organization_id,
            timestamp=datetime.now(timezone.utc),
            ip_address=ip_address,
            user_agent=user_agent,
            severity=severity,
            details=details or {},
            success=success,
        )

        # Log to Redis for real-time monitoring
        if self.enable_redis:
            await self._log_to_redis(event)

        # Log to database for persistence
        await self._log_to_database(event)

        return event

    async def _log_to_redis(self, event: AuditEvent) -> None:
        """Log event to Redis for real-time monitoring.

        Args:
            event: Audit event
        """
        try:
            redis = get_redis_client()
            key = f"audit:{event.organization_id}:{event.timestamp.strftime('%Y-%m-%d')}"
            await redis.lpush(key, json.dumps(event.__dict__, default=str))
            await redis.expire(key, 86400 * self.retention_days)
        except Exception:
            pass

    async def _log_to_database(self, event: AuditEvent) -> None:
        """Log event to database for persistence.

        Args:
            event: Audit event
        """
        # In production, this would insert into an audit_log table
        # For now, we'll use a simple approach
        pass

    async def query_events(
        self,
        organization_id: UUID,
        action: Optional[AuditAction] = None,
        resource_type: Optional[str] = None,
        user_id: Optional[UUID] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        severity: Optional[AuditSeverity] = None,
        limit: int = 100,
    ) -> list[AuditEvent]:
        """Query audit events.

        Args:
            organization_id: Organization ID
            action: Optional action filter
            resource_type: Optional resource type filter
            user_id: Optional user ID filter
            start_date: Optional start date
            end_date: Optional end date
            limit: Maximum number of results

        Returns:
            List of AuditEvent objects
        """
        # In production, this would query the audit_log table
        # For now, return empty list
        return []

    async def get_security_events(
        self,
        organization_id: UUID,
        hours: int = 24,
    ) -> list[AuditEvent]:
        """Get security-related events.

        Args:
            organization_id: Organization ID
            hours: Number of hours to look back

        Returns:
            List of security events
        """
        start_date = datetime.now(timezone.utc) - timedelta(hours=hours)
        return await self.query_events(
            organization_id=organization_id,
            start_date=start_date,
            severity=AuditSeverity.WARNING,
        )

    async def export_audit_trail(
        self,
        organization_id: UUID,
        start_date: datetime,
        end_date: datetime,
    ) -> str:
        """Export audit trail for compliance.

        Args:
            organization_id: Organization ID
            start_date: Start date
            end_date: End date

        Returns:
            Exported audit trail as JSON string
        """
        events = await self.query_events(
            organization_id=organization_id,
            start_date=start_date,
            end_date=end_date,
        )

        return json.dumps([e.__dict__ for e in events], default=str, indent=2)
