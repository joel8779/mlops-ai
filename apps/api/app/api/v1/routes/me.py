from fastapi import APIRouter, Depends

from app.core.auth import get_current_auth
from app.schemas.auth import AuthContext

router = APIRouter()


@router.get("", response_model=AuthContext)
async def read_me(auth: AuthContext = Depends(get_current_auth)) -> AuthContext:
    return auth
