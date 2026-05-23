"""GRPC Ecosystem Recovery - PHASE 21.2

Removes all GRPC-related packages and reinstalls with wheel-first strategy.
"""
import subprocess
import sys


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr.
    
    Args:
        cmd: Command to run
        
    Returns:
        tuple: (exit_code, stdout, stderr)
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def uninstall_packages(packages: list[str]) -> bool:
    """Uninstall packages.
    
    Args:
        packages: List of packages to uninstall
        
    Returns:
        bool: True if successful
    """
    for package in packages:
        print(f"Uninstalling {package}...")
        exit_code, stdout, stderr = run_command([sys.executable, "-m", "pip", "uninstall", "-y", package])
        if exit_code != 0:
            print(f"  Warning: Failed to uninstall {package}")
        else:
            print(f"  OK {package} uninstalled")
    return True


def purge_cache() -> bool:
    """Purge pip cache.
    
    Returns:
        bool: True if successful
    """
    print("Purging pip cache...")
    exit_code, stdout, stderr = run_command([sys.executable, "-m", "pip", "cache", "purge"])
    if exit_code == 0:
        print("  OK Pip cache purged")
        return True
    else:
        print("  FAIL Failed to purge cache")
        return False


def install_grpc_wheel_first() -> bool:
    """Install GRPC packages using wheel-first strategy.
    
    Returns:
        bool: True if successful
    """
    print("Installing GRPC ecosystem with wheel-first strategy...")
    
    # Try to install from wheels only
    packages = [
        "grpcio==1.76.0",
        "grpcio-tools==1.76.0",
        "protobuf==4.25.1",
    ]
    
    for package in packages:
        print(f"Installing {package}...")
        exit_code, stdout, stderr = run_command([
            sys.executable, "-m", "pip", "install",
            "--only-binary=:all:",
            "--no-cache-dir",
            package,
        ])
        
        if exit_code == 0:
            print(f"  OK {package} installed")
        else:
            print(f"  FAIL Failed to install {package}")
            print(f"  Error: {stderr[:200]}")
            return False
    
    return True


def validate_grpc() -> bool:
    """Validate GRPC installation.
    
    Returns:
        bool: True if successful
    """
    print("Validating GRPC installation...")
    
    try:
        import grpc
        print(f"  OK grpcio {grpc.__version__} installed")
    except ImportError as e:
        print(f"  FAIL grpcio not installed: {e}")
        return False
    
    try:
        from grpc._cython import cygrpc
        print("  OK cygrpc available")
    except ImportError as e:
        print(f"  FAIL cygrpc not available: {e}")
        return False
    
    try:
        import google.protobuf
        print(f"  OK protobuf {google.protobuf.__version__} installed")
    except ImportError as e:
        print(f"  FAIL protobuf not installed: {e}")
        return False
    
    return True


def main() -> int:
    """Run GRPC ecosystem recovery.
    
    Returns:
        int: Exit code
    """
    print("=" * 70)
    print("GRPC Ecosystem Recovery - PHASE 21.2")
    print("=" * 70)
    
    # Step 1: Uninstall GRPC packages
    print("\nStep 1: Uninstalling GRPC packages...")
    packages_to_uninstall = [
        "grpcio",
        "grpcio-tools",
        "grpcio-status",
        "protobuf",
        "googleapis-common-protos",
    ]
    uninstall_packages(packages_to_uninstall)
    
    # Step 2: Purge cache
    print("\nStep 2: Purging pip cache...")
    purge_cache()
    
    # Step 3: Install GRPC with wheel-first strategy
    print("\nStep 3: Installing GRPC ecosystem...")
    if not install_grpc_wheel_first():
        print("\nFAIL GRPC installation failed")
        print("\nTroubleshooting:")
        print("1. Ensure you're using Python 3.11")
        print("2. Try installing from Developer Command Prompt for VS 2022")
        print("3. Or use: pip install grpcio==1.71.2 grpcio-tools==1.71.2 protobuf==4.25.1")
        return 1
    
    # Step 4: Validate GRPC
    print("\nStep 4: Validating GRPC installation...")
    if not validate_grpc():
        print("\nFAIL GRPC validation failed")
        return 1
    
    print("\n" + "=" * 70)
    print("✓ GRPC ecosystem recovery complete")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
