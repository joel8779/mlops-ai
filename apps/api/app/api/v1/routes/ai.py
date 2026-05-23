from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_auth
from app.db.session import get_db
from app.schemas.ai import (
    AIResponse,
    AISummaryRequest,
    CandidateComparisonRequest,
    Copilot2Response,
    CopilotRequest,
    InterviewQuestionRequest,
)
from app.schemas.auth import AuthContext
from app.agents.orchestrator.copilot_orchestrator import HiringCopilotOrchestrator
from app.services.llm_recruiter_service import LLMRecruiterService
from app.services.rag_pipeline import RAGPipeline

router = APIRouter()


@router.post("/summary", response_model=AIResponse)
async def candidate_summary(payload: AISummaryRequest, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await LLMRecruiterService(db).summarize_candidate(auth, payload.candidate_id)


@router.post("/interview-questions", response_model=AIResponse)
async def interview_questions(payload: InterviewQuestionRequest, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await LLMRecruiterService(db).interview_questions(auth, payload.candidate_id, payload.job_description_id, payload.count)


@router.post("/compare", response_model=AIResponse)
async def compare_candidates(payload: CandidateComparisonRequest, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await LLMRecruiterService(db).compare_candidates(auth, payload.candidate_ids, payload.job_description_id)


@router.post("/copilot", response_model=AIResponse)
async def copilot(payload: CopilotRequest, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    return await RAGPipeline(db).answer(auth, payload)


@router.post("/copilot-2", response_model=Copilot2Response)
async def copilot_2(payload: CopilotRequest, auth: AuthContext = Depends(get_current_auth), db: AsyncSession = Depends(get_db)):
    result = await HiringCopilotOrchestrator(db).run(
        organization_id=auth.organization_id,
        recruiter_id=auth.user_id,
        query=payload.query,
        context={**payload.context, "limit": payload.top_k},
    )
    return Copilot2Response(answer=result.answer, confidence=result.confidence, artifacts=result.artifacts)
