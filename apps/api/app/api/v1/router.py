from fastapi import APIRouter

from app.api.v1.routes import analytics, ats, auth, billing, candidates, diagnostics, feedback, health, jobs, matching, realtime, resumes, workspace

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(candidates.router, prefix="/candidates", tags=["candidates"])
api_router.include_router(resumes.router, prefix="/resumes", tags=["resumes"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["job descriptions"])
api_router.include_router(matching.router, prefix="/matching", tags=["matching"])
api_router.include_router(workspace.router, prefix="/workspace", tags=["workspace"])
api_router.include_router(diagnostics.router, prefix="/diagnostics", tags=["diagnostics"])

# Optional routes - may fail if dependencies missing
try:
    from app.api.v1.routes import search
    api_router.include_router(search.router, prefix="/search", tags=["semantic search"])
except ImportError:
    pass  # Search route unavailable if dependencies missing

try:
    from app.api.v1.routes import ai
    api_router.include_router(ai.router, prefix="/ai", tags=["recruiter ai"])
except ImportError:
    pass  # AI route unavailable if dependencies missing

try:
    from app.api.v1.routes import recommendations
    api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
except ImportError:
    pass  # Recommendations route unavailable if dependencies missing

api_router.include_router(billing.router, prefix="/billing", tags=["billing"])

try:
    from app.api.v1.routes import workflow
    api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
except ImportError:
    pass  # Workflow route unavailable if dependencies missing

api_router.include_router(ats.router, prefix="/ats", tags=["ats"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["feedback"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(realtime.router, tags=["realtime"])
