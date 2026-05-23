"""Backend Validation Matrix - PHASE 21.

Validates Python runtime, grpc imports, FastAPI imports, SQLAlchemy imports,
Qdrant imports, Gemini imports, OpenTelemetry imports, embedding imports,
Celery imports, and websocket imports.
"""
import sys
from pathlib import Path


def validate_python_runtime() -> tuple[bool, str]:
    """Validate Python runtime version.
    
    Returns:
        tuple: (is_valid, message)
    """
    version = sys.version_info
    major, minor = version.major, version.minor
    
    if major == 3 and 11 <= minor < 13:
        return True, f"Python {major}.{minor} is compatible"
    return False, f"Python {major}.{minor} is not compatible (requires 3.11 or 3.12)"


def validate_grpc() -> tuple[bool, str]:
    """Validate grpc imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import grpc
        version = grpc.__version__
    except ImportError as e:
        return False, f"grpcio not installed: {e}"
    
    try:
        from grpc._cython import cygrpc
        return True, f"grpcio {version} with cygrpc available"
    except ImportError as e:
        return False, f"grpcio {version} installed but cygrpc import failed: {e}"


def validate_fastapi() -> tuple[bool, str]:
    """Validate FastAPI imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import fastapi
        version = fastapi.__version__
        return True, f"fastapi {version} installed"
    except ImportError as e:
        return False, f"fastapi not installed: {e}"


def validate_sqlalchemy() -> tuple[bool, str]:
    """Validate SQLAlchemy imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import sqlalchemy
        version = sqlalchemy.__version__
        return True, f"SQLAlchemy {version} installed"
    except ImportError as e:
        return False, f"SQLAlchemy not installed: {e}"


def validate_qdrant() -> tuple[bool, str]:
    """Validate Qdrant client imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        from qdrant_client import QdrantClient
        return True, "qdrant-client installed"
    except ImportError as e:
        return False, f"qdrant-client not installed: {e}"


def validate_gemini() -> tuple[bool, str]:
    """Validate Google Generative AI imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import google.generativeai as genai
        version = getattr(genai, "__version__", "unknown")
        return True, f"google-generativeai {version} installed"
    except ImportError as e:
        return False, f"google-generativeai not installed: {e}"


def validate_opentelemetry() -> tuple[bool, str]:
    """Validate OpenTelemetry imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import opentelemetry
        version = opentelemetry.__version__
        return True, f"opentelemetry {version} installed"
    except ImportError as e:
        return False, f"opentelemetry not installed: {e}"


def validate_embedding() -> tuple[bool, str]:
    """Validate embedding imports (sentence-transformers).
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        from sentence_transformers import SentenceTransformer
        import sentence_transformers
        version = getattr(sentence_transformers, "__version__", "unknown")
        return True, f"sentence-transformers {version} installed"
    except ImportError as e:
        return False, f"sentence-transformers not installed: {e}"


def validate_celery() -> tuple[bool, str]:
    """Validate Celery imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import celery
        version = celery.__version__
        return True, f"celery {version} installed"
    except ImportError as e:
        return False, f"celery not installed: {e}"


def validate_websocket() -> tuple[bool, str]:
    """Validate websocket imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import websockets
        version = websockets.__version__
        return True, f"websockets {version} installed"
    except ImportError as e:
        return False, f"websockets not installed: {e}"


def validate_app_imports() -> tuple[bool, str]:
    """Validate core app imports.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        sys.path.insert(0, str(Path("apps/api").absolute()))
        import app.main
        return True, "app.main imports successfully"
    except ImportError as e:
        return False, f"app.main import failed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main() -> int:
    """Run all validation checks and output matrix.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 70)
    print("Backend Validation Matrix - PHASE 21")
    print("=" * 70)
    
    checks = [
        ("Python Runtime", validate_python_runtime),
        ("GRPC", validate_grpc),
        ("FastAPI", validate_fastapi),
        ("SQLAlchemy", validate_sqlalchemy),
        ("Qdrant Client", validate_qdrant),
        ("Gemini", validate_gemini),
        ("OpenTelemetry", validate_opentelemetry),
        ("Embedding (sentence-transformers)", validate_embedding),
        ("Celery", validate_celery),
        ("WebSocket", validate_websocket),
        ("App Imports", validate_app_imports),
    ]
    
    results = []
    all_passed = True
    critical_passed = True
    
    for name, check_fn in checks:
        print(f"\n{name}:")
        try:
            is_valid, message = check_fn()
            results.append((name, is_valid, message))
            if is_valid:
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
                all_passed = False
                # Critical dependencies for core API
                if name in ["Python Runtime", "GRPC", "FastAPI", "SQLAlchemy", "App Imports"]:
                    critical_passed = False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results.append((name, False, str(e)))
            all_passed = False
            critical_passed = False
    
    print("\n" + "=" * 70)
    print("VALIDATION MATRIX")
    print("=" * 70)
    print(f"{'Component':<35} {'Status':<10} {'Details'}")
    print("-" * 70)
    for name, is_valid, message in results:
        status = "PASS" if is_valid else "FAIL"
        print(f"{name:<35} {status:<10} {message[:30]}")
    
    print("\n" + "=" * 70)
    if critical_passed:
        print("✓ CRITICAL DEPENDENCIES: PASSED")
        if not all_passed:
            print("⚠ OPTIONAL DEPENDENCIES: SOME FAILED")
        else:
            print("✓ ALL DEPENDENCIES: PASSED")
    else:
        print("✗ CRITICAL DEPENDENCIES: FAILED")
    print("=" * 70)
    
    if not critical_passed:
        print("\nREMEDIATION:")
        print("1. Run full runtime recovery:")
        print("   .\\scripts\\full_runtime_recovery.ps1  # Windows")
        print("   ./scripts/full_runtime_recovery.sh    # Linux/Mac")
        print("\n2. Install Visual C++ Build Tools (Windows):")
        print("   https://visualstudio.microsoft.com/downloads/")
        print("   Select 'Desktop development with C++'")
        print("\n3. Validate GRPC specifically:")
        print("   python scripts/validate_grpc.py")
        return 1
    elif not all_passed:
        print("\nOPTIONAL DEPENDENCIES MISSING:")
        print("ML features will be unavailable. Core API should work.")
        print("To install ML dependencies:")
        print("  pip install -r apps/api/requirements-ml.txt")
        return 0
    else:
        print("\n✓ All validations passed. Backend should start successfully.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
