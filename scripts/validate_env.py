"""Validate environment configuration for local development.

This script validates:
- DATABASE_URL
- REDIS_URL
- QDRANT_URL
- S3 endpoint config
- Required environment variables

Usage:
    python scripts/validate_env.py
"""

import os
import sys
from pathlib import Path
import urllib.parse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def validate_database_url():
    """Validate DATABASE_URL configuration."""
    print("Validating DATABASE_URL...")
    
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("✗ DATABASE_URL not set")
        return False
    
    try:
        parsed = urllib.parse.urlparse(database_url)
        
        if parsed.scheme not in ["postgresql+asyncpg", "postgresql"]:
            print(f"✗ Invalid DATABASE_URL scheme: {parsed.scheme}")
            return False
        
        if not parsed.hostname:
            print("✗ DATABASE_URL missing hostname")
            return False
        
        if not parsed.port:
            print("✗ DATABASE_URL missing port")
            return False
        
        if not parsed.path or not parsed.path.lstrip("/"):
            print("✗ DATABASE_URL missing database name")
            return False
        
        print(f"✓ DATABASE_URL valid: {parsed.hostname}:{parsed.port}{parsed.path}")
        return True
    except Exception as e:
        print(f"✗ DATABASE_URL parsing failed: {e}")
        return False


def validate_redis_url():
    """Validate REDIS_URL configuration."""
    print("Validating REDIS_URL...")
    
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        print("✗ REDIS_URL not set")
        return False
    
    try:
        parsed = urllib.parse.urlparse(redis_url)
        
        if parsed.scheme != "redis":
            print(f"✗ Invalid REDIS_URL scheme: {parsed.scheme}")
            return False
        
        if not parsed.hostname:
            print("✗ REDIS_URL missing hostname")
            return False
        
        if not parsed.port:
            print("✗ REDIS_URL missing port")
            return False
        
        print(f"✓ REDIS_URL valid: {parsed.hostname}:{parsed.port}")
        return True
    except Exception as e:
        print(f"✗ REDIS_URL parsing failed: {e}")
        return False


def validate_qdrant_url():
    """Validate QDRANT_URL configuration."""
    print("Validating QDRANT_URL...")
    
    qdrant_url = os.getenv("QDRANT_URL")
    if not qdrant_url:
        print("✗ QDRANT_URL not set")
        return False
    
    try:
        parsed = urllib.parse.urlparse(qdrant_url)
        
        if parsed.scheme not in ["http", "https"]:
            print(f"✗ Invalid QDRANT_URL scheme: {parsed.scheme}")
            return False
        
        if not parsed.hostname:
            print("✗ QDRANT_URL missing hostname")
            return False
        
        if not parsed.port:
            print("✗ QDRANT_URL missing port")
            return False
        
        print(f"✓ QDRANT_URL valid: {parsed.hostname}:{parsed.port}")
        return True
    except Exception as e:
        print(f"✗ QDRANT_URL parsing failed: {e}")
        return False


def validate_s3_config():
    """Validate S3 (MinIO) configuration."""
    print("Validating S3 configuration...")
    
    s3_endpoint = os.getenv("S3_ENDPOINT_URL")
    s3_access_key = os.getenv("S3_ACCESS_KEY_ID")
    s3_secret_key = os.getenv("S3_SECRET_ACCESS_KEY")
    s3_bucket = os.getenv("S3_BUCKET")
    
    if not s3_endpoint:
        print("✗ S3_ENDPOINT_URL not set")
        return False
    
    if not s3_access_key:
        print("✗ S3_ACCESS_KEY_ID not set")
        return False
    
    if not s3_secret_key:
        print("✗ S3_SECRET_ACCESS_KEY not set")
        return False
    
    if not s3_bucket:
        print("✗ S3_BUCKET not set")
        return False
    
    try:
        parsed = urllib.parse.urlparse(s3_endpoint)
        
        if parsed.scheme not in ["http", "https"]:
            print(f"✗ Invalid S3_ENDPOINT_URL scheme: {parsed.scheme}")
            return False
        
        if not parsed.hostname:
            print("✗ S3_ENDPOINT_URL missing hostname")
            return False
        
        if not parsed.port:
            print("✗ S3_ENDPOINT_URL missing port")
            return False
        
        print(f"✓ S3 configuration valid: {parsed.hostname}:{parsed.port}, bucket={s3_bucket}")
        return True
    except Exception as e:
        print(f"✗ S3 configuration parsing failed: {e}")
        return False


def validate_required_env_vars():
    """Validate required environment variables."""
    print("Validating required environment variables...")
    
    required_vars = [
        "APP_NAME",
        "ENVIRONMENT",
        "JWT_SECRET_KEY",
        "GEMINI_API_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"✗ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    print(f"✓ All required environment variables set")
    return True


def validate_jwt_secret():
    """Validate JWT secret key configuration."""
    print("Validating JWT_SECRET_KEY...")
    
    jwt_secret = os.getenv("JWT_SECRET_KEY")
    if not jwt_secret:
        print("✗ JWT_SECRET_KEY not set")
        return False
    
    if jwt_secret == "change-me-use-a-32-byte-random-secret":
        print("⚠ JWT_SECRET_KEY is using default value (not secure for production)")
        return True  # Allow for local development
    
    if len(jwt_secret) < 32:
        print("⚠ JWT_SECRET_KEY is too short (recommended: 32+ characters)")
        return True  # Allow for local development
    
    print("✓ JWT_SECRET_KEY valid")
    return True


def validate_gemini_api_key():
    """Validate Gemini API key configuration."""
    print("Validating GEMINI_API_KEY...")
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("✗ GEMINI_API_KEY not set")
        return False
    
    if gemini_key.startswith("AIzaSyBshjRojHHc4WO8T6-7PK2RNlzO_j-eVO8"):
        print("⚠ GEMINI_API_KEY appears to be a placeholder")
        return True  # Allow for local development
    
    print("✓ GEMINI_API_KEY set")
    return True


def main():
    """Main validation function."""
    print("=" * 60)
    print("Environment Configuration Validation")
    print("=" * 60)
    print()
    
    # Load .env file
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        print(f"Loading environment variables from {env_file}")
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print()
    
    validations = [
        validate_database_url,
        validate_redis_url,
        validate_qdrant_url,
        validate_s3_config,
        validate_required_env_vars,
        validate_jwt_secret,
        validate_gemini_api_key,
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
        return 0
    else:
        print(f"✗ Some validations failed ({passed}/{total} passed)")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
