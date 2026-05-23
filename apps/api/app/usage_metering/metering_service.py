from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID


@dataclass
class UsageMeter:
    organization_id: UUID
    counters: dict[str, int] = field(default_factory=dict)
    period_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class UsageMeteringService:
    def increment(self, meter: UsageMeter, metric: str, amount: int = 1) -> UsageMeter:
        meter.counters = {**meter.counters, metric: meter.counters.get(metric, 0) + amount}
        return meter

    def projected_invoice_units(self, meter: UsageMeter) -> dict[str, int]:
        return {
            "resume_overage_blocks": max(0, meter.counters.get("resumes", 0) - 5_000) // 1_000,
            "llm_million_tokens": meter.counters.get("llm_tokens", 0) // 1_000_000,
            "vector_query_blocks": meter.counters.get("vector_queries", 0) // 10_000,
        }
