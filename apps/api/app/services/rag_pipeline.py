from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.ai import AIResponse, CopilotRequest
from app.schemas.auth import AuthContext
from app.advanced_rag.context_compressor import ContextCompressor
from app.advanced_rag.reranking_service import RAGRerankingService
from app.advanced_rag.retrieval_router import RetrievalRouter
from app.services.llm_provider import LLMResult, get_llm_provider
from app.services.prompt_templates import COPILOT_PROMPT, RECRUITER_SYSTEM_PROMPT
from app.security.prompt_injection import sanitize_recruiter_prompt


class RAGPipeline:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.provider = get_llm_provider()

    async def answer(self, auth: AuthContext, payload: CopilotRequest) -> AIResponse:
        safe_query = sanitize_recruiter_prompt(payload.query)
        plan = RetrievalRouter().plan(safe_query, payload.top_k)
        retrieved = RetrievalRouter().retrieve(auth.organization_id, plan)
        reranked = RAGRerankingService().rerank(safe_query, retrieved)
        context = ContextCompressor().compress(reranked)
        result = await self.provider.complete(
            "recruiter_copilot",
            RECRUITER_SYSTEM_PROMPT,
            COPILOT_PROMPT.format(query=safe_query, context=context),
        )
        citations = [{"candidate_id": str(item.candidate_id), "score": item.score} for item in reranked]
        return AIResponse(answer=result.text, citations=citations, usage=result.__dict__)
