"""GRPC Ecosystem Validation Script - PHASE 21.

Validates grpcio installation and cygrpc import.
"""
import sys


def validate_grpc() -> tuple[bool, str]:
    """Validate grpcio installation and cygrpc import.
    
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
        return True, f"grpcio {version} with cygrpc installed successfully"
    except ImportError as e:
        return False, f"grpcio {version} installed but cygrpc import failed: {e}"
    except Exception as e:
        return False, f"Unexpected error importing cygrpc: {e}"


def validate_protobuf() -> tuple[bool, str]:
    """Validate protobuf installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        import google.protobuf
        version = google.protobuf.__version__
        return True, f"protobuf {version} installed successfully"
    except ImportError as e:
        return False, f"protobuf not installed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def validate_qdrant_client() -> tuple[bool, str]:
    """Validate qdrant-client installation.
    
    Returns:
        tuple: (is_valid, message)
    """
    try:
        from qdrant_client import QdrantClient
        return True, "qdrant-client installed successfully"
    except ImportError as e:
        return False, f"qdrant-client not installed: {e}"
    except Exception as e:
        return False, f"Unexpected error: {e}"


def main() -> int:
    """Run all grpc validation checks.
    
    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    print("=" * 60)
    print("GRPC Ecosystem Validation - PHASE 21")
    print("=" * 60)
    
    checks = [
        ("grpcio", validate_grpc),
        ("protobuf", validate_protobuf),
        ("qdrant-client", validate_qdrant_client),
    ]
    
    all_passed = True
    
    for name, check_fn in checks:
        print(f"\n{name}:")
        try:
            is_valid, message = check_fn()
            if is_valid:
                print(f"  ✓ {message}")
            else:
                print(f"  ✗ {message}")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Error: {e}")
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ All GRPC validations passed")
        print("=" * 60)
        return 0
    else:
        print("✗ Some GRPC validations failed")
        print("=" * 60)
        print("\nTo fix GRPC issues:")
        print("1. Uninstall GRPC packages:")
        print("   pip uninstall grpcio grpcio-tools grpcio-status protobuf")
        print("2. Purge pip cache:")
        print("   pip cache purge")
        print("3. Reinstall with pinned versions:")
        print("   pip install grpcio==1.60.0 grpcio-tools==1.60.0 grpcio-status==1.60.0 protobuf==4.25.1")
        print("\nIf GRPC still fails on Windows:")
        print("- Install Visual C++ Build Tools from https://visualstudio.microsoft.com/downloads/")
        print("- Select 'Desktop development with C++'")
        print("- Reinstall GRPC packages")
        return 1


if __name__ == "__main__":
    sys.exit(main())
