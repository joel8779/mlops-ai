"""Shared types for retrieval services."""

from dataclasses import dataclass
from typing import Any, Optional
from uuid import UUID


@dataclass
class RetrievalResult:
    """Result from hybrid retrieval."""

    candidate_id: UUID
    score: float
    vector_score: Optional[float] = None
    keyword_score: Optional[float] = None
    metadata: dict[str, Any] = None
