from fastapi import APIRouter

from app.api.v1.routes import ai, analytics, ats, auth, billing, feedback, jobs, matching, realtime, recommendations, resumes, search, workflow

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["job descriptions"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(search.router, prefix="/search", tags=["semantic search"])
api_router.include_router(ai.router, prefix="/ai", tags=["recruiter ai"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(billing.router, prefix="/billing", tags=["billing"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(ats.router, prefix="/ats", tags=["ats"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(realtime.router, tags=["realtime"])
