"""ML Capability Detection - PHASE 21.

Provides capability detection for ML dependencies and graceful degradation.
"""
import warnings
import importlib.metadata as metadata
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MLCapability:
    """Represents an ML capability and its availability."""
    name: str
    available: bool
    version: Optional[str] = None
    error: Optional[str] = None


class MLCapabilities:
    """Detects and reports ML capability availability."""
    
    def __init__(self) -> None:
        self._capabilities = self._detect_capabilities()
    
    def _detect_capabilities(self) -> dict[str, MLCapability]:
        """Detect all ML capabilities.
        
        Returns:
            Dictionary of capability name to MLCapability
        """
        capabilities = {}
        
        package_checks = {
            "sentence_transformers": "sentence-transformers",
            "torch": "torch",
            "transformers": "transformers",
            "pandas": "pandas",
            "numpy": "numpy",
            "scikit_learn": "scikit-learn",
        }

        for capability_name, package_name in package_checks.items():
            try:
                capabilities[capability_name] = MLCapability(
                    name=capability_name,
                    available=True,
                    version=metadata.version(package_name),
                )
            except metadata.PackageNotFoundError as exc:
                capabilities[capability_name] = MLCapability(
                    name=capability_name,
                    available=False,
                    error=str(exc),
                )
        
        return capabilities
    
    def is_available(self, capability: str) -> bool:
        """Check if a capability is available.
        
        Args:
            capability: Name of the capability
            
        Returns:
            True if available, False otherwise
        """
        cap = self._capabilities.get(capability)
        return cap.available if cap else False
    
    def get_capability(self, capability: str) -> Optional[MLCapability]:
        """Get a capability by name.
        
        Args:
            capability: Name of the capability
            
        Returns:
            MLCapability if exists, None otherwise
        """
        return self._capabilities.get(capability)
    
    def warn_if_unavailable(self, capability: str, feature_name: str) -> None:
        """Warn if a capability is unavailable.
        
        Args:
            capability: Name of the capability
            feature_name: Name of the feature that requires the capability
        """
        cap = self._capabilities.get(capability)
        if cap and not cap.available:
            warnings.warn(
                f"{feature_name} is unavailable because {capability} is not installed. "
                f"Error: {cap.error}. "
                f"Install with: pip install -r requirements-ml.txt",
                RuntimeWarning,
                stacklevel=2,
            )
    
    def report_unavailable(self) -> list[str]:
        """Report all unavailable capabilities.
        
        Returns:
            List of unavailable capability names
        """
        return [name for name, cap in self._capabilities.items() if not cap.available]
    
    def report_available(self) -> list[str]:
        """Report all available capabilities.
        
        Returns:
            List of available capability names
        """
        return [name for name, cap in self._capabilities.items() if cap.available]


# Global instance
ml_capabilities = MLCapabilities()
