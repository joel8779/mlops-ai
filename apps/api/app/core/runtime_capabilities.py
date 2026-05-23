"""Runtime capabilities - Check optional dependencies and features."""

import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional


class Capability(str, Enum):
    """System capabilities."""

    LLM_GEMINI = "llm_gemini"
    LLM_OPENAI = "llm_openai"
    OCR = "ocr"
    MULTIMODAL = "multimodal"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    MLFLOW = "mlflow"
    PREFECT = "prefect"
    NEO4J = "neo4j"
    OBSERVABILITY_OTLP = "observability_otlp"
    OBSERVABILITY_PROMETHEUS = "observability_prometheus"


@dataclass
class CapabilityInfo:
    """Information about a capability."""

    name: Capability
    available: bool
    version: Optional[str]
    error: Optional[str]


class RuntimeCapabilities:
    """Check and manage runtime capabilities."""

    _capabilities: dict[Capability, CapabilityInfo] = {}
    _initialized = False

    @classmethod
    def initialize(cls) -> None:
        """Initialize capability checks."""
        if cls._initialized:
            return

        cls._capabilities = {
            Capability.LLM_GEMINI: cls._check_gemini(),
            Capability.LLM_OPENAI: cls._check_openai(),
            Capability.OCR: cls._check_ocr(),
            Capability.MULTIMODAL: cls._check_multimodal(),
            Capability.KNOWLEDGE_GRAPH: cls._check_knowledge_graph(),
            Capability.MLFLOW: cls._check_mlflow(),
            Capability.PREFECT: cls._check_prefect(),
            Capability.NEO4J: cls._check_neo4j(),
            Capability.OBSERVABILITY_OTLP: cls._check_observability_otlp(),
            Capability.OBSERVABILITY_PROMETHEUS: cls._check_observability_prometheus(),
        }

        cls._initialized = True

    @classmethod
    def is_available(cls, capability: Capability) -> bool:
        """Check if a capability is available.

        Args:
            capability: Capability to check

        Returns:
            True if available
        """
        if not cls._initialized:
            cls.initialize()
        info = cls._capabilities.get(capability)
        return info.available if info else False

    @classmethod
    def require(cls, capability: Capability) -> None:
        """Require a capability to be available.

        Args:
            capability: Capability to require

        Raises:
            ImportError: If capability not available
        """
        if not cls.is_available(capability):
            info = cls._capabilities.get(capability)
            raise ImportError(f"Required capability {capability.value} not available: {info.error if info else 'Unknown'}")

    @classmethod
    def optional_import(cls, capability: Capability, import_func: Callable[[], Any], default: Any = None) -> Any:
        """Attempt an optional import based on capability.

        Args:
            capability: Capability to check
            import_func: Import function
            default: Default value if not available

        Returns:
            Imported module or default
        """
        if cls.is_available(capability):
            try:
                return import_func()
            except Exception as exc:
                return default
        return default

    @classmethod
    def get_info(cls, capability: Capability) -> Optional[CapabilityInfo]:
        """Get capability information.

        Args:
            capability: Capability to query

        Returns:
            CapabilityInfo or None
        """
        if not cls._initialized:
            cls.initialize()
        return cls._capabilities.get(capability)

    @classmethod
    def get_all(cls) -> dict[Capability, CapabilityInfo]:
        """Get all capability information.

        Returns:
            Dictionary of capabilities
        """
        if not cls._initialized:
            cls.initialize()
        return cls._capabilities.copy()

    @staticmethod
    def _check_gemini() -> CapabilityInfo:
        """Check Gemini LLM capability.

        Returns:
            CapabilityInfo
        """
        try:
            import google.generativeai as genai
            version = getattr(genai, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.LLM_GEMINI,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.LLM_GEMINI,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_openai() -> CapabilityInfo:
        """Check OpenAI LLM capability.

        Returns:
            CapabilityInfo
        """
        try:
            import openai
            version = getattr(openai, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.LLM_OPENAI,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.LLM_OPENAI,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_ocr() -> CapabilityInfo:
        """Check OCR capability.

        Returns:
            CapabilityInfo
        """
        try:
            import pytesseract
            version = getattr(pytesseract, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.OCR,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.OCR,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_multimodal() -> CapabilityInfo:
        """Check multimodal capability.

        Returns:
            CapabilityInfo
        """
        try:
            import sentence_transformers
            version = getattr(sentence_transformers, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.MULTIMODAL,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.MULTIMODAL,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_knowledge_graph() -> CapabilityInfo:
        """Check knowledge graph capability.

        Returns:
            CapabilityInfo
        """
        try:
            import neo4j
            version = getattr(neo4j, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.KNOWLEDGE_GRAPH,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.KNOWLEDGE_GRAPH,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_mlflow() -> CapabilityInfo:
        """Check MLflow capability.

        Returns:
            CapabilityInfo
        """
        try:
            import mlflow
            version = getattr(mlflow, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.MLFLOW,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.MLFLOW,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_prefect() -> CapabilityInfo:
        """Check Prefect capability.

        Returns:
            CapabilityInfo
        """
        try:
            import prefect
            version = getattr(prefect, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.PREFECT,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.PREFECT,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_neo4j() -> CapabilityInfo:
        """Check Neo4j capability.

        Returns:
            CapabilityInfo
        """
        try:
            import neo4j
            version = getattr(neo4j, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.NEO4J,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.NEO4J,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_observability_otlp() -> CapabilityInfo:
        """Check OTLP observability capability.

        Returns:
            CapabilityInfo
        """
        try:
            import opentelemetry.exporter.otlp
            version = getattr(opentelemetry.exporter.otlp, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.OBSERVABILITY_OTLP,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.OBSERVABILITY_OTLP,
                available=False,
                version=None,
                error=str(exc),
            )

    @staticmethod
    def _check_observability_prometheus() -> CapabilityInfo:
        """Check Prometheus observability capability.

        Returns:
            CapabilityInfo
        """
        try:
            import prometheus_client
            version = getattr(prometheus_client, "__version__", "unknown")
            return CapabilityInfo(
                name=Capability.OBSERVABILITY_PROMETHEUS,
                available=True,
                version=version,
                error=None,
            )
        except ImportError as exc:
            return CapabilityInfo(
                name=Capability.OBSERVABILITY_PROMETHEUS,
                available=False,
                version=None,
                error=str(exc),
            )


def require_capability(capability: Capability):
    """Decorator to require a capability for a function.

    Args:
        capability: Required capability

    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            RuntimeCapabilities.require(capability)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def optional_capability(capability: Capability, default: Any = None):
    """Decorator to make a function optional based on capability.

    Args:
        capability: Optional capability
        default: Default return value if not available

    Returns:
        Decorator function
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if RuntimeCapabilities.is_available(capability):
                return func(*args, **kwargs)
            return default
        return wrapper
    return decorator
