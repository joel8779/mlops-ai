"""Legacy LLM provider wrapper - migrated to production Gemini infrastructure.

This module provides backward compatibility while using the new Gemini provider system.
New code should import from app.services.llm.providers directly.
"""

from typing import Optional

from app.core.config import settings
from app.services.llm.providers import (
    GeminiProvider,
    ModelRouter,
    ModelType,
)
from app.services.llm.providers.gemini_provider import LLMResult


class DisabledLLMProvider:
    """Fallback provider when no API key is configured."""

    async def complete(self, feature: str, system: str, user: str) -> LLMResult:
        return LLMResult(
            text="AI provider is disabled. Configure GEMINI_API_KEY to enable this feature.",
            provider="disabled",
            model="none",
            prompt_tokens=0,
            completion_tokens=0,
            estimated_cost_usd=0,
        )


# Global model router instance
_model_router: Optional[ModelRouter] = None


def get_model_router() -> ModelRouter:
    """Get or create the global model router."""
    global _model_router
    if _model_router is None:
        _model_router = ModelRouter(api_key=settings.gemini_api_key)
    return _model_router


def get_llm_provider():
    """Get LLM provider - now always uses Gemini.

    Returns:
        GeminiProvider or DisabledLLMProvider
    """
    if not settings.gemini_api_key:
        return DisabledLLMProvider()

    # Use Flash model by default for low latency
    from app.services.llm.providers.gemini_provider import GeminiModel

    return GeminiProvider(
        api_key=settings.gemini_api_key,
        model=GeminiModel.GEMINI_2_5_FLASH,
    )


def get_llm_provider_for_task(task_type: ModelType = ModelType.FAST):
    """Get LLM provider optimized for a specific task type.

    Args:
        task_type: Type of task (fast, reasoning, multimodal, etc.)

    Returns:
        Tuple of (GeminiProvider, ModelSelection)
    """
    if not settings.gemini_api_key:
        return DisabledLLMProvider(), None

    router = get_model_router()
    return router.get_provider_for_task(task_type, api_key=settings.gemini_api_key)
