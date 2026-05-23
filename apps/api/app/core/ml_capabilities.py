"""ML Capability Detection - PHASE 21.

Provides capability detection for ML dependencies and graceful degradation.
"""
import warnings
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
        
        # sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            import sentence_transformers
            capabilities["sentence_transformers"] = MLCapability(
                name="sentence_transformers",
                available=True,
                version=getattr(sentence_transformers, "__version__", "unknown"),
            )
        except ImportError as e:
            capabilities["sentence_transformers"] = MLCapability(
                name="sentence_transformers",
                available=False,
                error=str(e),
            )
        except Exception as e:
            capabilities["sentence_transformers"] = MLCapability(
                name="sentence_transformers",
                available=False,
                error=f"Unexpected error: {e}",
            )
        
        # torch
        try:
            import torch
            capabilities["torch"] = MLCapability(
                name="torch",
                available=True,
                version=torch.__version__,
            )
        except ImportError as e:
            capabilities["torch"] = MLCapability(
                name="torch",
                available=False,
                error=str(e),
            )
        except Exception as e:
            capabilities["torch"] = MLCapability(
                name="torch",
                available=False,
                error=f"Unexpected error: {e}",
            )
        
        # transformers
        try:
            import transformers
            capabilities["transformers"] = MLCapability(
                name="transformers",
                available=True,
                version=getattr(transformers, "__version__", "unknown"),
            )
        except ImportError as e:
            capabilities["transformers"] = MLCapability(
                name="transformers",
                available=False,
                error=str(e),
            )
        except Exception as e:
            capabilities["transformers"] = MLCapability(
                name="transformers",
                available=False,
                error=f"Unexpected error: {e}",
            )
        
        # pandas
        try:
            import pandas
            capabilities["pandas"] = MLCapability(
                name="pandas",
                available=True,
                version=pandas.__version__,
            )
        except ImportError as e:
            capabilities["pandas"] = MLCapability(
                name="pandas",
                available=False,
                error=str(e),
            )
        except Exception as e:
            capabilities["pandas"] = MLCapability(
                name="pandas",
                available=False,
                error=f"Unexpected error: {e}",
            )
        
        # numpy
        try:
            import numpy
            capabilities["numpy"] = MLCapability(
                name="numpy",
                available=True,
                version=numpy.__version__,
            )
        except ImportError as e:
            capabilities["numpy"] = MLCapability(
                name="numpy",
                available=False,
                error=str(e),
            )
        except Exception as e:
            capabilities["numpy"] = MLCapability(
                name="numpy",
                available=False,
                error=f"Unexpected error: {e}",
            )
        
        # scikit-learn
        try:
            import sklearn
            capabilities["scikit_learn"] = MLCapability(
                name="scikit_learn",
                available=True,
                version=getattr(sklearn, "__version__", "unknown"),
            )
        except ImportError as e:
            capabilities["scikit_learn"] = MLCapability(
                name="scikit_learn",
                available=False,
                error=str(e),
            )
        except Exception as e:
            capabilities["scikit_learn"] = MLCapability(
                name="scikit_learn",
                available=False,
                error=f"Unexpected error: {e}",
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
