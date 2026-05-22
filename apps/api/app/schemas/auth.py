from uuid import UUID

from pydantic import BaseModel, EmailStr


class AuthContext(BaseModel):
    user_id: UUID
    organization_id: UUID
    external_user_id: str
    email: EmailStr
    roles: list[str] = []
