"""Production-grade Gemini provider with streaming, structured outputs, and enterprise features."""

import asyncio
import json
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Optional

import google.generativeai as genai
from google.generativeai.types import (
    GenerateContentResponse,
    GenerationConfig,
    HarmBlockThreshold,
    HarmCategory,
    ContentType,
)
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

        genai.configure(api_key=self.api_key)
        self.model = model
        self.client = genai.GenerativeModel(model.value)
        self.token_tracker = token_tracker or TokenTracker()
        self.safety_filter = safety_filter or SafetyFilter()

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
    )
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

        start_time = asyncio.get_event_loop().time()
        metric_start = llm_observer.start_timer()

        try:
            with tracer.start_as_current_span("llm.gemini.complete") as span:
                span.set_attribute("llm.provider", "gemini")
                span.set_attribute("llm.model", self.model.value)
                span.set_attribute("llm.feature", feature)

                config = GenerationConfig(
                    temperature=options.temperature,
                    top_p=options.top_p,
                    top_k=options.top_k,
                    max_output_tokens=options.max_output_tokens or self.model.max_tokens,
                )
                safety_settings = self._build_safety_settings(options.safety_level)
                content = self._prepare_content(prompt, system)
                response = await asyncio.to_thread(
                    self.client.generate_content,
                    content,
                    generation_config=config,
                    safety_settings=safety_settings,
                )
        except Exception as exc:
            llm_observer.record_failure("gemini", self.model.value, feature, metric_start, exc)
            raise

        # Calculate latency
        latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000

        # Extract metadata
        prompt_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 0
        completion_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 0
        total_tokens = response.usage_metadata.total_token_count if response.usage_metadata else 0

        # Estimate cost
        cost_usd = self._estimate_cost(prompt_tokens, completion_tokens)

        # Extract safety ratings
        safety_ratings = self._extract_safety_ratings(response)

        # Extract text
        text = response.text if response.parts else ""

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
            finish_reason=response.candidates[0].finish_reason.name if response.candidates else "",
            safety_ratings=safety_ratings,
            structured_data=structured_data,
        )

    @retry(
        retry=retry_if_exception_type((Exception,)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(min=1, max=8),
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
        metric_start = llm_observer.start_timer()

        # Build generation config
        config = GenerationConfig(
            temperature=options.temperature,
            top_p=options.top_p,
            top_k=options.top_k,
            max_output_tokens=options.max_output_tokens or self.model.max_tokens,
        )

        # Build safety settings
        safety_settings = self._build_safety_settings(options.safety_level)

        # Prepare content
        content = self._prepare_content(prompt, system)

        try:
            with tracer.start_as_current_span("llm.gemini.stream") as span:
                span.set_attribute("llm.provider", "gemini")
                span.set_attribute("llm.model", self.model.value)
                span.set_attribute("llm.feature", feature)
                response = await asyncio.to_thread(
                    self.client.generate_content,
                    content,
                    generation_config=config,
                    safety_settings=safety_settings,
                    stream=True,
                )
        except Exception as exc:
            llm_observer.record_failure("gemini", self.model.value, feature, metric_start, exc)
            raise

        full_text = ""
        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                if on_chunk:
                    on_chunk(chunk.text)
                yield chunk.text

        # Track usage after stream completes
        if response.usage_metadata:
            prompt_tokens = response.usage_metadata.prompt_token_count
            completion_tokens = response.usage_metadata.candidates_token_count
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
                start_time=metric_start,
                prompt=prompt,
                response=full_text,
                input_tokens=prompt_tokens,
                output_tokens=completion_tokens,
                cost_usd=cost_usd,
            )

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

    def _prepare_content(self, prompt: str, system: Optional[str]) -> list[ContentType]:
        """Prepare content for generation.

        Args:
            prompt: User prompt
            system: System instruction

        Returns:
            List of content parts
        """
        parts = [{"text": prompt}]

        if system:
            # Set system instruction on the model
            self.client._system_instruction = system

        return parts

    def _build_safety_settings(self, level: SafetyLevel) -> dict[HarmCategory, HarmBlockThreshold]:
        """Build safety settings based on level.

        Args:
            level: Safety level

        Returns:
            Safety settings dictionary
        """
        thresholds = {
            SafetyLevel.BLOCK_NONE: HarmBlockThreshold.BLOCK_NONE,
            SafetyLevel.BLOCK_LOW: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            SafetyLevel.BLOCK_MEDIUM: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            SafetyLevel.BLOCK_HIGH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }

        threshold = thresholds.get(level, HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE)

        return {
            HarmCategory.HARM_CATEGORY_HARASSMENT: threshold,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: threshold,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: threshold,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: threshold,
        }

    def _extract_safety_ratings(self, response: GenerateContentResponse) -> dict[str, str]:
        """Extract safety ratings from response.

        Args:
            response: Gemini response

        Returns:
            Dictionary of safety ratings
        """
        ratings = {}
        if response.candidates and response.candidates[0].safety_ratings:
            for rating in response.candidates[0].safety_ratings:
                ratings[rating.category.name] = rating.probability.name
        return ratings

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
