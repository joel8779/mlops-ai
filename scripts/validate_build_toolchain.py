"""Build Toolchain Validation - PHASE 21.2

Validates MSVC compiler, Windows SDK, CMake, and pip wheel support.
"""
import subprocess
import sys
from pathlib import Path


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
            timeout=10,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except FileNotFoundError:
        return -1, "", "Command not found"
    except Exception as e:
        return -1, "", str(e)


def validate_cl_exe() -> dict:
    """Validate MSVC compiler (cl.exe) availability.
    
    Returns:
        dict: Validation result
    """
    # Try to find cl.exe in common locations
    common_paths = [
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\Enterprise\VC\Tools\MSVC",
    ]
    
    cl_found = False
    cl_path = None
    
    for base_path in common_paths:
        if Path(base_path).exists():
            # Search for cl.exe in subdirectories
            for cl in Path(base_path).rglob("cl.exe"):
                cl_found = True
                cl_path = str(cl)
                break
        if cl_found:
            break
    
    # Try running cl.exe if found
    if cl_found:
        exit_code, stdout, stderr = run_command([cl_path])
        if exit_code == 0 or "Microsoft" in stdout or "Microsoft" in stderr:
            return {
                "available": True,
                "path": cl_path,
                "version": stdout[:200] if stdout else stderr[:200],
            }
    
    return {
        "available": False,
        "path": None,
        "version": "cl.exe not found",
    }


def validate_cmake() -> dict:
    """Validate CMake availability.
    
    Returns:
        dict: Validation result
    """
    exit_code, stdout, stderr = run_command(["cmake", "--version"])
    
    if exit_code == 0:
        version_line = stdout.split("\n")[0] if stdout else ""
        return {
            "available": True,
            "version": version_line,
        }
    
    return {
        "available": False,
        "version": "CMake not found",
    }


def validate_pip_wheel() -> dict:
    """Validate pip wheel support.
    
    Returns:
        dict: Validation result
    """
    exit_code, stdout, stderr = run_command([sys.executable, "-m", "pip", "--version"])
    
    if exit_code == 0:
        return {
            "available": True,
            "version": stdout.strip(),
        }
    
    return {
        "available": False,
        "version": "pip not found",
    }


def validate_windows_sdk() -> dict:
    """Validate Windows SDK availability.
    
    Returns:
        dict: Validation result
    """
    # Check for Windows SDK in common locations
    sdk_paths = [
        r"C:\Program Files (x86)\Windows Kits\10",
        r"C:\Program Files\Windows Kits\10",
    ]
    
    sdk_found = False
    sdk_path = None
    
    for path in sdk_paths:
        if Path(path).exists():
            sdk_found = True
            sdk_path = path
            break
    
    return {
        "available": sdk_found,
        "path": sdk_path,
        "version": "Windows SDK 10" if sdk_found else "Windows SDK not found",
    }


def main() -> int:
    """Run all build toolchain validations.
    
    Returns:
        int: Exit code
    """
    print("=" * 70)
    print("Build Toolchain Validation - PHASE 21.2")
    print("=" * 70)
    
    results = {
        "MSVC Compiler (cl.exe)": validate_cl_exe(),
        "CMake": validate_cmake(),
        "pip wheel": validate_pip_wheel(),
        "Windows SDK": validate_windows_sdk(),
    }
    
    print("\nValidation Results:")
    print("-" * 70)
    
    all_available = True
    for name, result in results.items():
        status = "✓ AVAILABLE" if result.get("available") else "✗ NOT AVAILABLE"
        print(f"\n{name}:")
        print(f"  Status: {status}")
        if result.get("path"):
            print(f"  Path: {result['path']}")
        print(f"  Version: {result['version']}")
        
        if not result.get("available"):
            all_available = False
    
    print("\n" + "=" * 70)
    if all_available:
        print("✓ All build tools available")
        print("=" * 70)
        return 0
    else:
        print("✗ Some build tools missing")
        print("=" * 70)
        print("\nTo install missing tools:")
        print("1. Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/")
        print("   Select 'Desktop development with C++'")
        print("2. CMake: https://cmake.org/download/")
        print("3. Windows SDK: Included with Visual Studio Build Tools")
        return 1


if __name__ == "__main__":
    sys.exit(main())
