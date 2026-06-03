"""RBAC Manager - Role-Based Access Control for enterprise security."""

from dataclasses import dataclass
from enum import Enum
from typing import Set
from uuid import UUID


class Permission(str, Enum):
    """System permissions."""

    # Candidate permissions
    CANDIDATE_READ = "candidate:read"
    CANDIDATE_CREATE = "candidate:create"
    CANDIDATE_UPDATE = "candidate:update"
    CANDIDATE_DELETE = "candidate:delete"
    CANDIDATE_EXPORT = "candidate:export"

    # Job permissions
    JOB_READ = "job:read"
    JOB_CREATE = "job:create"
    JOB_UPDATE = "job:update"
    JOB_DELETE = "job:delete"

    # Analytics permissions
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"

    # Admin permissions
    USER_MANAGE = "user:manage"
    ROLE_MANAGE = "role:manage"
    ORGANIZATION_MANAGE = "organization:manage"
    AUDIT_VIEW = "audit:view"
    SETTINGS_MANAGE = "settings:manage"


class Role(str, Enum):
    """System roles."""

    ADMIN = "admin"
    RECRUITER = "recruiter"
    HIRING_MANAGER = "hiring_manager"
    INTERVIEWER = "interviewer"
    VIEWER = "viewer"


@dataclass
class RoleDefinition:
    """Role definition with permissions."""

    role: Role
    permissions: Set[Permission]
    description: str


class RBACManager:
    """Role-Based Access Control manager."""

    # Default role definitions
    ROLE_DEFINITIONS = {
        Role.ADMIN: RoleDefinition(
            role=Role.ADMIN,
            permissions=set(Permission),  # All permissions
            description="Full system access",
        ),
        Role.HIRING_MANAGER: RoleDefinition(
            role=Role.HIRING_MANAGER,
            permissions={
                Permission.CANDIDATE_READ,
                Permission.CANDIDATE_CREATE,
                Permission.CANDIDATE_UPDATE,
                Permission.JOB_READ,
                Permission.JOB_CREATE,
                Permission.JOB_UPDATE,
                Permission.ANALYTICS_VIEW,
                Permission.ANALYTICS_EXPORT,
            },
            description="Manage hiring process and view analytics",
        ),
        Role.RECRUITER: RoleDefinition(
            role=Role.RECRUITER,
            permissions={
                Permission.CANDIDATE_READ,
                Permission.CANDIDATE_CREATE,
                Permission.CANDIDATE_UPDATE,
                Permission.JOB_READ,
                Permission.ANALYTICS_VIEW,
            },
            description="Recruit and manage candidates",
        ),
        Role.INTERVIEWER: RoleDefinition(
            role=Role.INTERVIEWER,
            permissions={
                Permission.CANDIDATE_READ,
                Permission.JOB_READ,
            },
            description="View candidates and jobs for interviewing",
        ),
        Role.VIEWER: RoleDefinition(
            role=Role.VIEWER,
            permissions={
                Permission.CANDIDATE_READ,
                Permission.JOB_READ,
            },
            description="Read-only access",
        ),
    }

    def __init__(self) -> None:
        """Initialize RBAC manager."""
        self.user_roles: dict[UUID, Set[Role]] = {}
        self.custom_permissions: dict[UUID, Set[Permission]] = {}

    def assign_role(self, user_id: UUID, role: Role) -> None:
        """Assign a role to a user.

        Args:
            user_id: User ID
            role: Role to assign
        """
        if user_id not in self.user_roles:
            self.user_roles[user_id] = set()
        self.user_roles[user_id].add(role)

    def remove_role(self, user_id: UUID, role: Role) -> None:
        """Remove a role from a user.

        Args:
            user_id: User ID
            role: Role to remove
        """
        if user_id in self.user_roles:
            self.user_roles[user_id].discard(role)

    def get_user_roles(self, user_id: UUID) -> Set[Role]:
        """Get all roles for a user.

        Args:
            user_id: User ID

        Returns:
            Set of Role objects
        """
        return self.user_roles.get(user_id, set())

    def has_permission(self, user_id: UUID, permission: Permission) -> bool:
        """Check if user has a specific permission.

        Args:
            user_id: User ID
            permission: Permission to check

        Returns:
            True if user has permission
        """
        # Check custom permissions first
        if user_id in self.custom_permissions:
            if permission in self.custom_permissions[user_id]:
                return True

        # Check role-based permissions
        roles = self.get_user_roles(user_id)
        for role in roles:
            role_def = self.ROLE_DEFINITIONS.get(role)
            if role_def and permission in role_def.permissions:
                return True

        return False

    def grant_custom_permission(self, user_id: UUID, permission: Permission) -> None:
        """Grant a custom permission to a user.

        Args:
            user_id: User ID
            permission: Permission to grant
        """
        if user_id not in self.custom_permissions:
            self.custom_permissions[user_id] = set()
        self.custom_permissions[user_id].add(permission)

    def revoke_custom_permission(self, user_id: UUID, permission: Permission) -> None:
        """Revoke a custom permission from a user.

        Args:
            user_id: User ID
            permission: Permission to revoke
        """
        if user_id in self.custom_permissions:
            self.custom_permissions[user_id].discard(permission)

    def get_all_permissions(self, user_id: UUID) -> Set[Permission]:
        """Get all permissions for a user (role + custom).

        Args:
            user_id: User ID

        Returns:
            Set of all Permission objects
        """
        permissions = set()

        # Add role-based permissions
        roles = self.get_user_roles(user_id)
        for role in roles:
            role_def = self.ROLE_DEFINITIONS.get(role)
            if role_def:
                permissions.update(role_def.permissions)

        # Add custom permissions
        if user_id in self.custom_permissions:
            permissions.update(self.custom_permissions[user_id])

        return permissions

    def create_custom_role(
        self,
        role_name: str,
        permissions: Set[Permission],
        description: str = "",
    ) -> RoleDefinition:
        """Create a custom role definition.

        Args:
            role_name: Name for the custom role
            permissions: Set of permissions
            description: Role description

        Returns:
            RoleDefinition object
        """
        # Create a new Role enum value
        custom_role = Role(role_name.lower())

        role_def = RoleDefinition(
            role=custom_role,
            permissions=permissions,
            description=description,
        )

        self.ROLE_DEFINITIONS[custom_role] = role_def
        return role_def
