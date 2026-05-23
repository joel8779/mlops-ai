"""Validate local infrastructure connectivity.

This script validates:
- PostgreSQL connectivity
- Redis connectivity
- Qdrant connectivity
- MinIO connectivity

Usage:
    python scripts/validate_local_infra.py
"""

import asyncio
import sys
import time
from pathlib import Path
import subprocess
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def check_docker_running():
    """Check if Docker is running."""
    print("Checking Docker daemon...")
    try:
        result = subprocess.run(
            ["docker", "ps"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            print("✓ Docker daemon is running")
            return True
        else:
            print("✗ Docker daemon is not running")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Docker command timed out")
        return False
    except FileNotFoundError:
        print("✗ Docker not found in PATH")
        return False
    except Exception as e:
        print(f"✗ Docker check failed: {e}")
        return False


def check_postgres_container():
    """Check if PostgreSQL container is running."""
    print("Checking PostgreSQL container...")
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "postgres"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "running" in result.stdout or "healthy" in result.stdout:
            print("✓ PostgreSQL container is running")
            return True
        else:
            print("✗ PostgreSQL container is not running")
            print(f"Output: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ PostgreSQL container check timed out")
        return False
    except Exception as e:
        print(f"✗ PostgreSQL container check failed: {e}")
        return False


def check_postgres_connectivity():
    """Check PostgreSQL connectivity with retry logic."""
    print("Checking PostgreSQL connectivity...")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["docker", "exec", "resume-intelligence-postgres-1", "pg_isready", "-U", "resume", "-d", "resume_ai"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "accepting connections" in result.stdout:
                print("✓ PostgreSQL is accepting connections")
                return True
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: PostgreSQL not ready")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt + 1}/{max_retries}: PostgreSQL check timed out")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: PostgreSQL check failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("✗ PostgreSQL connectivity failed after retries")
    return False


def check_redis_container():
    """Check if Redis container is running."""
    print("Checking Redis container...")
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "redis"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "running" in result.stdout or "healthy" in result.stdout:
            print("✓ Redis container is running")
            return True
        else:
            print("✗ Redis container is not running")
            print(f"Output: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Redis container check timed out")
        return False
    except Exception as e:
        print(f"✗ Redis container check failed: {e}")
        return False


def check_redis_connectivity():
    """Check Redis connectivity with retry logic."""
    print("Checking Redis connectivity...")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["docker", "exec", "resume-intelligence-redis-1", "redis-cli", "ping"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if "PONG" in result.stdout:
                print("✓ Redis is responding to ping")
                return True
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: Redis not ready")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt + 1}/{max_retries}: Redis check timed out")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Redis check failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("✗ Redis connectivity failed after retries")
    return False


def check_qdrant_container():
    """Check if Qdrant container is running."""
    print("Checking Qdrant container...")
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "qdrant"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "running" in result.stdout or "healthy" in result.stdout:
            print("✓ Qdrant container is running")
            return True
        else:
            print("✗ Qdrant container is not running")
            print(f"Output: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ Qdrant container check timed out")
        return False
    except Exception as e:
        print(f"✗ Qdrant container check failed: {e}")
        return False


def check_qdrant_connectivity():
    """Check Qdrant connectivity with retry logic."""
    print("Checking Qdrant connectivity...")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["docker", "exec", "resume-intelligence-qdrant-1", "wget", "-qO-", "http://localhost:6333/healthz"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ Qdrant health endpoint is responding")
                return True
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: Qdrant not ready")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt + 1}/{max_retries}: Qdrant check timed out")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Qdrant check failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("✗ Qdrant connectivity failed after retries")
    return False


def check_minio_container():
    """Check if MinIO container is running."""
    print("Checking MinIO container...")
    try:
        result = subprocess.run(
            ["docker", "compose", "ps", "minio"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if "running" in result.stdout or "healthy" in result.stdout:
            print("✓ MinIO container is running")
            return True
        else:
            print("✗ MinIO container is not running")
            print(f"Output: {result.stdout}")
            return False
    except subprocess.TimeoutExpired:
        print("✗ MinIO container check timed out")
        return False
    except Exception as e:
        print(f"✗ MinIO container check failed: {e}")
        return False


def check_minio_connectivity():
    """Check MinIO connectivity with retry logic."""
    print("Checking MinIO connectivity...")
    
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["docker", "exec", "resume-intelligence-minio-1", "mc", "ready", "local"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✓ MinIO is ready")
                return True
            else:
                print(f"Attempt {attempt + 1}/{max_retries}: MinIO not ready")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        except subprocess.TimeoutExpired:
            print(f"Attempt {attempt + 1}/{max_retries}: MinIO check timed out")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
        except Exception as e:
            print(f"Attempt {attempt + 1}/{max_retries}: MinIO check failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
    
    print("✗ MinIO connectivity failed after retries")
    return False


def main():
    """Main validation function."""
    print("=" * 60)
    print("Local Infrastructure Validation")
    print("=" * 60)
    print()
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    validations = [
        check_docker_running,
        check_postgres_container,
        check_postgres_connectivity,
        check_redis_container,
        check_redis_connectivity,
        check_qdrant_container,
        check_qdrant_connectivity,
        check_minio_container,
        check_minio_connectivity,
    ]
    
    results = []
    for validation in validations:
        try:
            result = validation()
            results.append(result)
        except Exception as e:
            print(f"✗ Validation failed with error: {e}")
            results.append(False)
        print()
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if all(results):
        print(f"✓ All validations passed ({passed}/{total})")
        print("=" * 60)
        print()
        print("Infrastructure is ready. You can now start the backend:")
        print("  cd apps/api")
        print("  uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000 --reload")
        return 0
    else:
        print(f"✗ Some validations failed ({passed}/{total} passed)")
        print("=" * 60)
        print()
        print("To fix issues:")
        print("  1. Start Docker Desktop")
        print("  2. Run: docker compose up -d postgres redis qdrant minio mlflow")
        print("  3. Wait for services to be healthy")
        print("  4. Run this validation script again")
        return 1


if __name__ == "__main__":
    sys.exit(main())
