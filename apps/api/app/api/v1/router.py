from fastapi import APIRouter

from app.api.v1.routes import me, resumes

api_router = APIRouter()
api_router.include_router(me.router, prefix="/me", tags=["identity"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
