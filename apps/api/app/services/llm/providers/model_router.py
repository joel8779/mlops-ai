"""Model router for intelligent LLM model selection and fallback."""

import random
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from app.services.llm.providers.gemini_provider import GeminiModel, GeminiProvider


class ModelType(str, Enum):
    """Types of LLM tasks."""

    FAST = "fast"  # Low-latency, simple tasks
    REASONING = "reasoning"  # Complex reasoning
    MULTIMODAL = "multimodal"  # Image/text processing
    LONG_CONTEXT = "long_context"  # Large context windows
    CODE = "code"  # Code generation/analysis
    ANALYSIS = "analysis"  # Data analysis


@dataclass
class ModelSelection:
    """Model selection with fallback chain."""

    primary: GeminiModel
    fallbacks: list[GeminiModel]
    reason: str


class ModelRouter:
    """Intelligent model router for optimal model selection."""

    # Default model mappings by task type
    TASK_MODELS = {
        ModelType.FAST: [
            GeminiModel.GEMINI_2_5_FLASH,
            GeminiModel.GEMINI_1_5_FLASH,
        ],
        ModelType.REASONING: [
            GeminiModel.GEMINI_2_5_PRO,
            GeminiModel.GEMINI_1_5_PRO,
        ],
        ModelType.MULTIMODAL: [
            GeminiModel.GEMINI_2_5_PRO,
            GeminiModel.GEMINI_1_5_PRO,
        ],
        ModelType.LONG_CONTEXT: [
            GeminiModel.GEMINI_2_5_PRO,
            GeminiModel.GEMINI_1_5_PRO,
        ],
        ModelType.CODE: [
            GeminiModel.GEMINI_2_5_PRO,
            GeminiModel.GEMINI_1_5_PRO,
        ],
        ModelType.ANALYSIS: [
            GeminiModel.GEMINI_2_5_PRO,
            GeminiModel.GEMINI_1_5_PRO,
        ],
    }

    def __init__(self, api_key: Optional[str] = None) -> None:
        """Initialize model router.

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        self._providers: dict[GeminiModel, GeminiProvider] = {}

    def select_model(
        self,
        task_type: ModelType,
        budget_constrained: bool = False,
        latency_sensitive: bool = False,
    ) -> ModelSelection:
        """Select the best model for a given task.

        Args:
            task_type: Type of task
            budget_constrained: If True, prefer cheaper models
            latency_sensitive: If True, prefer faster models

        Returns:
            ModelSelection with primary and fallback models
        """
        candidates = self.TASK_MODELS.get(task_type, [GeminiModel.GEMINI_2_5_FLASH])

        # Apply constraints
        if budget_constrained or latency_sensitive:
            # Prefer Flash models
            flash_models = [m for m in candidates if m.is_flash]
            if flash_models:
                candidates = flash_models

        primary = candidates[0]
        fallbacks = candidates[1:] if len(candidates) > 1 else []

        reason = f"Selected {primary.value} for {task_type.value} task"
        if budget_constrained:
            reason += " (budget constrained)"
        if latency_sensitive:
            reason += " (latency sensitive)"

        return ModelSelection(
            primary=primary,
            fallbacks=fallbacks,
            reason=reason,
        )

    def get_provider(
        self,
        model: GeminiModel,
        api_key: Optional[str] = None,
    ) -> GeminiProvider:
        """Get or create a provider for the given model.

        Args:
            model: Gemini model
            api_key: Optional API key override

        Returns:
            GeminiProvider instance
        """
        if model not in self._providers:
            self._providers[model] = GeminiProvider(
                api_key=api_key or self.api_key,
                model=model,
            )
        return self._providers[model]

    def get_provider_for_task(
        self,
        task_type: ModelType,
        budget_constrained: bool = False,
        latency_sensitive: bool = False,
        api_key: Optional[str] = None,
    ) -> tuple[GeminiProvider, ModelSelection]:
        """Get provider and selection for a task.

        Args:
            task_type: Type of task
            budget_constrained: If True, prefer cheaper models
            latency_sensitive: If True, prefer faster models
            api_key: Optional API key override

        Returns:
            Tuple of (GeminiProvider, ModelSelection)
        """
        selection = self.select_model(task_type, budget_constrained, latency_sensitive)
        provider = self.get_provider(selection.primary, api_key)
        return provider, selection

    async def complete_with_fallback(
        self,
        prompt: str,
        task_type: ModelType,
        system: Optional[str] = None,
        budget_constrained: bool = False,
        latency_sensitive: bool = False,
        api_key: Optional[str] = None,
    ) -> tuple[any, GeminiModel]:
        """Complete a prompt with automatic fallback.

        Args:
            prompt: User prompt
            task_type: Type of task
            system: Optional system instruction
            budget_constrained: If True, prefer cheaper models
            latency_sensitive: If True, prefer faster models
            api_key: Optional API key override

        Returns:
            Tuple of (result, model_used)
        """
        selection = self.select_model(task_type, budget_constrained, latency_sensitive)

        # Try primary model
        try:
            provider = self.get_provider(selection.primary, api_key)
            result = await provider.complete(prompt, system)
            return result, selection.primary
        except Exception as e:
            # Try fallbacks
            for fallback_model in selection.fallbacks:
                try:
                    provider = self.get_provider(fallback_model, api_key)
                    result = await provider.complete(prompt, system)
                    return result, fallback_model
                except Exception:
                    continue

            # All models failed
            raise Exception(f"All models failed for task {task_type.value}: {e}")

    def clear_cache(self) -> None:
        """Clear provider cache."""
        self._providers.clear()
