from enum import StrEnum

from fastapi import HTTPException, status

from app.schemas.auth import AuthContext


class Permission(StrEnum):
    read_candidates = "candidates:read"
    write_candidates = "candidates:write"
    read_jobs = "jobs:read"
    write_jobs = "jobs:write"
    run_ai = "ai:run"
    administer_org = "org:admin"


ROLE_PERMISSIONS = {
    "admin": set(Permission),
    "recruiter": {
        Permission.read_candidates,
        Permission.write_candidates,
        Permission.read_jobs,
        Permission.write_jobs,
        Permission.run_ai,
    },
    "viewer": {Permission.read_candidates, Permission.read_jobs},
}


def assert_permission(auth: AuthContext, permission: Permission) -> None:
    allowed = set().union(*(ROLE_PERMISSIONS.get(role, set()) for role in auth.roles))
    if permission not in allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
