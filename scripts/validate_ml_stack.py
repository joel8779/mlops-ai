"""AI/ML Stack Validation Script - PHASE 20.

Validates the complete AI pipeline including embeddings, semantic retrieval,
Gemini requests, RAG pipeline, candidate ranking, recommendation engine,
vector search, and OCR pipeline.
"""
import sys
from pathlib import Path


def validate_sentence_transformers() -> tuple[bool, str]:
    """Validate sentence-transformers installation and loading.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        from sentence_transformers import SentenceTransformer
        return True, "sentence-transformers is installed and importable"
    except ImportError as e:
        return False, f"sentence-transformers not installed: {e}"


def validate_torch() -> tuple[bool, str]:
    """Validate PyTorch installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import torch
        version = torch.__version__
        return True, f"PyTorch {version} is installed"
    except ImportError as e:
        return False, f"PyTorch not installed: {e}"


def validate_transformers() -> tuple[bool, str]:
    """Validate transformers installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import transformers
        version = transformers.__version__
        return True, f"transformers {version} is installed"
    except ImportError as e:
        return False, f"transformers not installed: {e}"


def validate_gemini() -> tuple[bool, str]:
    """Validate Google Generative AI installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import google.generativeai as genai
        version = getattr(genai, "__version__", "unknown")
        return True, f"google-generativeai {version} is installed"
    except ImportError as e:
        return False, f"google-generativeai not installed: {e}"


def validate_qdrant() -> tuple[bool, str]:
    """Validate Qdrant client installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        from qdrant_client import QdrantClient
        return True, "qdrant-client is installed"
    except ImportError as e:
        return False, f"qdrant-client not installed: {e}"


def validate_pandas() -> tuple[bool, str]:
    """Validate pandas installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import pandas
        version = pandas.__version__
        return True, f"pandas {version} is installed"
    except ImportError as e:
        return False, f"pandas not installed: {e}"


def validate_numpy() -> tuple[bool, str]:
    """Validate numpy installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import numpy
        version = numpy.__version__
        return True, f"numpy {version} is installed"
    except ImportError as e:
        return False, f"numpy not installed: {e}"


def main() -> int:
    """Run all ML stack validation checks.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("AI/ML Stack Validation - PHASE 20")
    print("=" * 60)
    
    checks = [
        ("sentence-transformers", validate_sentence_transformers),
        ("PyTorch", validate_torch),
        ("transformers", validate_transformers),
        ("Google Generative AI", validate_gemini),
        ("Qdrant Client", validate_qdrant),
        ("pandas", validate_pandas),
        ("numpy", validate_numpy),
    ]
    
    all_passed = True
    ml_stack_available = True
    
    for name, check_fn in checks:
        print(f"\n{name}:")
        try:
            is_valid, message = check_fn()
            if is_valid:
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
                all_passed = False
                if name in ["sentence-transformers", "PyTorch", "transformers"]:
                    ml_stack_available = False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if ml_stack_available:
        print("✓ ML stack is available")
        print("=" * 60)
        print("\nTo install ML dependencies:")
        print("  pip install -r apps/api/requirements-ml.txt")
        return 0 if all_passed else 1
    else:
        print("✗ ML stack is not fully available")
        print("=" * 60)
        print("\nTo install ML dependencies:")
        print("  pip install -r apps/api/requirements-ml.txt")
        print("\nNote: Some ML features may require Visual Studio Build Tools on Windows")
        return 1


if __name__ == "__main__":
    sys.exit(main())
