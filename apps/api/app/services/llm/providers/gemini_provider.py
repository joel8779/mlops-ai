"""Production-grade Gemini provider with streaming, structured outputs, and enterprise features."""

import asyncio
import importlib.metadata as metadata
import json
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Optional

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings
from app.observability.ai import LLMObserver
from app.observability.tracing import get_tracer
from app.services.llm.providers.token_tracker import TokenTracker
from app.services.llm.providers.safety_filters import SafetyFilter, SafetyLevel


tracer = get_tracer(__name__)
llm_observer = LLMObserver()


def _load_genai_sdk() -> tuple[Any, Any]:
    """Load the modern Google Gen AI SDK only when Gemini is actually used."""
    try:
        from google import genai
        from google.genai import types
    except ImportError as exc:
        raise ImportError(
            "Gemini requires google-genai. Install apps/api/requirements-ai.txt "
            "with apps/api/constraints.txt after the core runtime is stable."
        ) from exc
    return genai, types


class GeminiModel(str, Enum):
    """Available Gemini models with their capabilities."""

    GEMINI_2_5_FLASH = "gemini-2.5-flash"
    GEMINI_2_5_PRO = "gemini-2.5-pro"
    GEMINI_1_5_FLASH = "gemini-1.5-flash"
    GEMINI_1_5_PRO = "gemini-1.5-pro"

    @property
    def is_flash(self) -> bool:
        return "flash" in self.value

    @property
    def is_pro(self) -> bool:
        return "pro" in self.value

    @property
    def supports_multimodal(self) -> bool:
        return True  # All Gemini models support multimodal

    @property
    def max_tokens(self) -> int:
        if self.is_pro:
            return 8192
        return 8192

    @property
    def context_window(self) -> int:
        if self.is_pro:
            return 1_000_000
        return 1_000_000


@dataclass(frozen=True)
class LLMResult:
    """Standardized LLM response with metadata."""

    text: str
    provider: str = "gemini"
    model: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    latency_ms: float = 0.0
    finish_reason: str = ""
    safety_ratings: dict[str, str] = field(default_factory=dict)
    structured_data: Optional[dict[str, Any]] = None


@dataclass
class GenerationOptions:
    """Configuration for LLM generation."""

    temperature: float = 0.2
    top_p: float = 0.95
    top_k: int = 40
    max_output_tokens: Optional[int] = None
    stream: bool = False
    json_mode: bool = False
    safety_level: SafetyLevel = SafetyLevel.BLOCK_MEDIUM
    system_instruction: Optional[str] = None


class GeminiProvider:
    """Production-grade Gemini provider with enterprise features."""

    # Cost per 1M tokens (approximate, subject to change)
    COST_PER_MILLION = {
        GeminiModel.GEMINI_2_5_FLASH: {"input": 0.075, "output": 0.30},
        GeminiModel.GEMINI_2_5_PRO: {"input": 1.25, "output": 5.00},
        GeminiModel.GEMINI_1_5_FLASH: {"input": 0.075, "output": 0.15},
        GeminiModel.GEMINI_1_5_PRO: {"input": 1.25, "output": 5.00},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: GeminiModel = GeminiModel.GEMINI_2_5_FLASH,
        token_tracker: Optional[TokenTracker] = None,
        safety_filter: Optional[SafetyFilter] = None,
    ) -> None:
        """Initialize Gemini provider.

        Args:
            api_key: Google API key. If None, uses settings.gemini_api_key
            model: Gemini model to use
            token_tracker: Optional token tracker for cost accounting
            safety_filter: Optional safety filter for content moderation
        """
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key is required")

        genai, types = _load_genai_sdk()
        self.model = model
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(api_version="v1beta"),
        )
        self.token_tracker = token_tracker or TokenTracker()
        self.safety_filter = safety_filter or SafetyFilter()

    async def complete(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[GenerationOptions] = None,
        feature: str = "llm_completion",
    ) -> LLMResult:
        """Generate a completion.

        Args:
            prompt: User prompt
            system: Optional system instruction
            options: Generation options

        Returns:
            LLMResult with response and metadata
        """
        options = options or GenerationOptions()
        options.system_instruction = system

        from datetime import datetime, timezone
        from fastapi import HTTPException
        from app.core.redis import get_redis_client

        redis_client = get_redis_client()
        now_dt = datetime.now(timezone.utc)
        month_key = f"gemini:cost:{now_dt.strftime('%Y-%m')}"

        # 1. Budget check
        current_cost_str = await redis_client.get(month_key)
        current_cost = float(current_cost_str) if current_cost_str else 0.0
        if current_cost >= 100.0:
            raise HTTPException(
                status_code=429,
                detail="Gemini API monthly budget exceeded.",
                headers={"Retry-After": "3600"},
            )

        # 2. Concurrency limit (concurrency queue)
        concurrency_key = "gemini:concurrency"
        max_wait = 30.0
        poll_interval = 0.5
        waited = 0.0
        acquired = False
        while waited < max_wait:
            current_val = await redis_client.incr(concurrency_key)
            if current_val <= 5:
                await redis_client.expire(concurrency_key, 60)
                acquired = True
                break
            else:
                await redis_client.decr(concurrency_key)
                await asyncio.sleep(poll_interval)
                waited += poll_interval

        if not acquired:
            raise HTTPException(
                status_code=429,
                detail="Gemini API concurrency limit exceeded. Please try again later.",
                headers={"Retry-After": "5"},
            )

        try:
            result = await self._complete_retried(prompt, system, options, feature)
            # Update monthly cost
            await redis_client.incrbyfloat(month_key, result.estimated_cost_usd)
            return result
        finally:
            if acquired:
                await redis_client.decr(concurrency_key)

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
    )
    async def _complete_retried(
        self,
        prompt: str,
        system: Optional[str],
        options: GenerationOptions,
        feature: str,
    ) -> LLMResult:
        start_time = asyncio.get_event_loop().time()
        metric_start = llm_observer.start_timer()

        try:
            with tracer.start_as_current_span("llm.gemini.complete") as span:
                span.set_attribute("llm.provider", "gemini")
                span.set_attribute("llm.model", self.model.value)
                span.set_attribute("llm.feature", feature)

                config = self._build_generation_config(options)
                safety_settings = self._build_safety_settings(options.safety_level)
                content = self._prepare_content(prompt, system)
                response = await self.client.aio.models.generate_content(
                    model=self.model.value,
                    contents=content,
                    config={**config, "safety_settings": safety_settings},
                )
        except Exception as exc:
            llm_observer.record_failure("gemini", self.model.value, feature, metric_start, exc)
            raise

        # Calculate latency
        latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000

        # Extract metadata
        prompt_tokens = getattr(response.usage_metadata, "prompt_token_count", None) or 0 if response.usage_metadata else 0
        completion_tokens = getattr(response.usage_metadata, "candidates_token_count", None) or 0 if response.usage_metadata else 0
        total_tokens = getattr(response.usage_metadata, "total_token_count", None) or 0 if response.usage_metadata else 0

        # Estimate cost
        cost_usd = self._estimate_cost(prompt_tokens, completion_tokens)

        # Extract safety ratings
        safety_ratings = self._extract_safety_ratings(response)

        # Extract text
        text = getattr(response, "text", "") or ""

        # Parse JSON if in JSON mode
        structured_data = None
        if options.json_mode and text:
            try:
                structured_data = json.loads(text)
            except json.JSONDecodeError:
                pass

        # Track usage
        self.token_tracker.track(
            model=self.model.value,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost_usd,
            feature=feature,
        )
        llm_observer.record_success(
            provider="gemini",
            model=self.model.value,
            feature=feature,
            start_time=metric_start,
            prompt=prompt,
            response=text,
            input_tokens=prompt_tokens,
            output_tokens=completion_tokens,
            cost_usd=cost_usd,
        )

        return LLMResult(
            text=text,
            provider="gemini",
            model=self.model.value,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost_usd,
            latency_ms=latency_ms,
            finish_reason=self._extract_finish_reason(response),
            safety_ratings=safety_ratings,
            structured_data=structured_data,
        )

    async def complete_stream(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[GenerationOptions] = None,
        on_chunk: Optional[Callable[[str], None]] = None,
        feature: str = "llm_stream",
    ) -> AsyncGenerator[str, None]:
        """Generate a streaming completion.

        Args:
            prompt: User prompt
            system: Optional system instruction
            options: Generation options
            on_chunk: Optional callback for each chunk

        Yields:
            Text chunks as they are generated
        """
        options = options or GenerationOptions()
        options.stream = True
        options.system_instruction = system

        from datetime import datetime, timezone
        from fastapi import HTTPException
        from app.core.redis import get_redis_client

        redis_client = get_redis_client()
        now_dt = datetime.now(timezone.utc)
        month_key = f"gemini:cost:{now_dt.strftime('%Y-%m')}"

        # 1. Budget check
        current_cost_str = await redis_client.get(month_key)
        current_cost = float(current_cost_str) if current_cost_str else 0.0
        if current_cost >= 100.0:
            raise HTTPException(
                status_code=429,
                detail="Gemini API monthly budget exceeded.",
                headers={"Retry-After": "3600"},
            )

        # 2. Concurrency limit (concurrency queue)
        concurrency_key = "gemini:concurrency"
        max_wait = 30.0
        poll_interval = 0.5
        waited = 0.0
        acquired = False
        while waited < max_wait:
            current_val = await redis_client.incr(concurrency_key)
            if current_val <= 5:
                await redis_client.expire(concurrency_key, 60)
                acquired = True
                break
            else:
                await redis_client.decr(concurrency_key)
                await asyncio.sleep(poll_interval)
                waited += poll_interval

        if not acquired:
            raise HTTPException(
                status_code=429,
                detail="Gemini API concurrency limit exceeded. Please try again later.",
                headers={"Retry-After": "5"},
            )

        try:
            chunks = await self._complete_stream_retried(prompt, system, options, feature)
        finally:
            if acquired:
                await redis_client.decr(concurrency_key)

        full_text = ""
        for chunk in chunks:
            text = getattr(chunk, "text", "") or ""
            if text:
                full_text += text
                if on_chunk:
                    on_chunk(text)
                yield text

        # Track usage after stream completes
        usage_metadata = getattr(chunks[-1], "usage_metadata", None) if chunks else None
        if usage_metadata:
            prompt_tokens = getattr(usage_metadata, "prompt_token_count", None) or 0
            completion_tokens = getattr(usage_metadata, "candidates_token_count", None) or 0
            cost_usd = self._estimate_cost(prompt_tokens, completion_tokens)

            self.token_tracker.track(
                model=self.model.value,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cost_usd=cost_usd,
                feature=feature,
            )
            llm_observer.record_success(
                provider="gemini",
                model=self.model.value,
                feature=feature,
                start_time=llm_observer.start_timer(),
                prompt=prompt,
                response=full_text,
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                cost_usd=cost_usd,
            )
            # Update monthly cost
            await redis_client.incrbyfloat(month_key, cost_usd)

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
    )
    async def _complete_stream_retried(
        self,
        prompt: str,
        system: Optional[str],
        options: GenerationOptions,
        feature: str,
    ) -> list[Any]:
        config = self._build_generation_config(options)
        safety_settings = self._build_safety_settings(options.safety_level)
        content = self._prepare_content(prompt, system)
        metric_start = llm_observer.start_timer()

        try:
            with tracer.start_as_current_span("llm.gemini.stream") as span:
                span.set_attribute("llm.provider", "gemini")
                span.set_attribute("llm.model", self.model.value)
                span.set_attribute("llm.feature", feature)
                chunks = await asyncio.to_thread(
                    lambda: list(
                        self.client.models.generate_content_stream(
                            model=self.model.value,
                            contents=content,
                            config={**config, "safety_settings": safety_settings},
                        )
                    )
                )
                return chunks
        except Exception as exc:
            llm_observer.record_failure("gemini", self.model.value, feature, metric_start, exc)
            raise

    async def complete_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        system: Optional[str] = None,
        options: Optional[GenerationOptions] = None,
        feature: str = "llm_structured",
    ) -> LLMResult:
        """Generate a completion with structured JSON output.

        Args:
            prompt: User prompt
            schema: JSON schema for output
            system: Optional system instruction
            options: Generation options

        Returns:
            LLMResult with structured data
        """
        options = options or GenerationOptions()
        options.json_mode = True

        # Add schema to system prompt
        schema_instruction = f"\n\nYou must respond with valid JSON that conforms to this schema:\n{json.dumps(schema, indent=2)}"
        enhanced_system = f"{system or ''}{schema_instruction}"

        result = await self.complete(prompt, enhanced_system, options, feature=feature)

        # Parse and validate JSON
        if result.text:
            try:
                result = replace(result, structured_data=json.loads(result.text))
            except json.JSONDecodeError:
                # Try to extract JSON from markdown code blocks
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', result.text, re.DOTALL)
                if json_match:
                    try:
                        result = replace(result, structured_data=json.loads(json_match.group(1)))
                    except json.JSONDecodeError:
                        pass

        return result

    def _build_generation_config(self, options: GenerationOptions) -> dict[str, Any]:
        """Build generation config for the Google Gen AI SDK."""
        config: dict[str, Any] = {
            "temperature": options.temperature,
            "top_p": options.top_p,
            "top_k": options.top_k,
            "max_output_tokens": options.max_output_tokens or self.model.max_tokens,
        }
        if options.system_instruction:
            config["system_instruction"] = options.system_instruction
        if options.json_mode:
            config["response_mime_type"] = "application/json"
        return config

    def _prepare_content(self, prompt: str, system: Optional[str]) -> str:
        """Prepare content for generation.

        Args:
            prompt: User prompt
            system: System instruction

        Returns:
            Prompt content
        """
        return prompt

    def _build_safety_settings(self, level: SafetyLevel) -> list[dict[str, str]]:
        """Build safety settings based on level.

        Args:
            level: Safety level

        Returns:
            Safety settings list
        """
        thresholds = {
            SafetyLevel.BLOCK_NONE: "BLOCK_NONE",
            SafetyLevel.BLOCK_LOW: "BLOCK_LOW_AND_ABOVE",
            SafetyLevel.BLOCK_MEDIUM: "BLOCK_MEDIUM_AND_ABOVE",
            SafetyLevel.BLOCK_HIGH: "BLOCK_ONLY_HIGH",
        }

        threshold = thresholds.get(level, "BLOCK_MEDIUM_AND_ABOVE")

        return [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": threshold},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": threshold},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": threshold},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": threshold},
        ]

    def _extract_safety_ratings(self, response: Any) -> dict[str, str]:
        """Extract safety ratings from response.

        Args:
            response: Gemini response

        Returns:
            Dictionary of safety ratings
        """
        ratings = {}
        candidates = getattr(response, "candidates", None) or []
        if candidates and getattr(candidates[0], "safety_ratings", None):
            for rating in candidates[0].safety_ratings:
                category = getattr(rating, "category", "")
                probability = getattr(rating, "probability", "")
                ratings[getattr(category, "name", category)] = getattr(probability, "name", probability)
        return ratings

    def _extract_finish_reason(self, response: Any) -> str:
        """Extract finish reason from a Gemini response."""
        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            return ""
        finish_reason = getattr(candidates[0], "finish_reason", "")
        return getattr(finish_reason, "name", finish_reason) or ""

    @staticmethod
    def sdk_version() -> str | None:
        """Return installed Google Gen AI SDK version, if present."""
        try:
            return metadata.version("google-genai")
        except metadata.PackageNotFoundError:
            return None

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Estimate cost in USD.

        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens

        Returns:
            Estimated cost in USD
        """
        costs = self.COST_PER_MILLION.get(self.model, {"input": 0.15, "output": 0.60})
        input_cost = (prompt_tokens / 1_000_000) * costs["input"]
        output_cost = (completion_tokens / 1_000_000) * costs["output"]
        return round(input_cost + output_cost, 6)

    def get_token_tracker(self) -> TokenTracker:
        """Get the token tracker instance.

        Returns:
            TokenTracker instance
        """
        return self.token_tracker

    def reset_token_tracker(self) -> None:
        """Reset token tracking."""
        self.token_tracker.reset()
