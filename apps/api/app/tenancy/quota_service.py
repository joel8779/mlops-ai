from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import TenantQuota


class QuotaService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def enforce(self, organization_id, metric: str, increment: int = 1) -> None:
        quota = await self.db.get(TenantQuota, organization_id)
        if quota is None:
            return
        limit = {
            "resumes": quota.monthly_resume_limit,
            "llm_tokens": quota.monthly_llm_token_limit,
            "vector_queries": quota.monthly_vector_query_limit,
        }.get(metric)
        if limit is None:
            return
        used = int(quota.usage_counters.get(metric, 0))
        if used + increment > limit:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Tenant quota exceeded")
        quota.usage_counters = {**quota.usage_counters, metric: used + increment}
        self.db.add(quota)
        await self.db.commit()
