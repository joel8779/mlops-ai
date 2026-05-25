from __future__ import annotations

from time import perf_counter
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ResumeProcessingEvent


class PipelineStageError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.details = details or {}


class PipelineTrace:
    def __init__(self, db: AsyncSession, organization_id, resume_id) -> None:
        self.db = db
        self.organization_id = organization_id
        self.resume_id = resume_id

    async def success(self, stage: str, started_at: float, payload: dict[str, Any] | None = None) -> None:
        await self._emit(stage, "success", started_at, payload or {})

    async def failure(self, stage: str, started_at: float, exc: Exception, payload: dict[str, Any] | None = None) -> None:
        safe_error = classify_pipeline_error(stage, exc)
        await self._emit(
            stage,
            "failure",
            started_at,
            {
                **(payload or {}),
                "error": safe_error,
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
            },
        )

    async def _emit(self, stage: str, status: str, started_at: float, payload: dict[str, Any]) -> None:
        self.db.add(
            ResumeProcessingEvent(
                organization_id=self.organization_id,
                resume_id=self.resume_id,
                event_type=f"resume.{stage}.{status}",
                payload={
                    "stage": stage,
                    "status": status,
                    "duration_ms": round((perf_counter() - started_at) * 1000, 2),
                    **payload,
                },
            )
        )
        await self.db.flush()


def classify_pipeline_error(stage: str, exc: Exception) -> dict[str, str]:
    text = str(exc).lower()
    if "tesseract" in text or "ocr" in text:
        code = "ocr_extraction_failed"
        message = "OCR extraction failed. Check OCR runtime and scanned document quality."
    elif "embedding" in text or "sentence-transformers" in text:
        code = "embedding_generation_failed"
        message = "Embedding generation failed. Check sentence-transformer runtime."
    elif "qdrant" in text or "collection" in text or "vector" in text:
        code = "qdrant_indexing_failed"
        message = "Vector indexing failed. Check Qdrant availability and collection configuration."
    elif "gemini" in text or "genai" in text or "api key" in text:
        code = "gemini_extraction_failed"
        message = "Gemini extraction failed. Check Gemini credentials and model runtime."
    elif "sql" in text or "database" in text or "constraint" in text:
        code = "candidate_persistence_failed"
        message = "Candidate persistence failed. Check database relationships and constraints."
    elif "unsupported content type" in text or "parser" in text or "pdf" in text or "docx" in text:
        code = "document_parsing_failed"
        message = "Document parsing failed. Check file type, encryption, and document text quality."
    else:
        code = f"{stage}_failed"
        message = f"{stage.replace('_', ' ').title()} failed."
    return {"code": code, "message": message}
