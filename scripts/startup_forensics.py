#!/usr/bin/env python
"""
Startup Forensics Script - PHASE 22
Traces the complete backend startup sequence to identify exact failure points
"""

import sys
import time
import traceback
from pathlib import Path

# Add apps/api to path
sys.path.insert(0, str(Path(__file__).parent.parent / "apps" / "api"))

def trace_import(module_name):
    """Trace import with timing and error capture"""
    start = time.time()
    try:
        __import__(module_name)
        duration = time.time() - start
        print(f"✓ {module_name:50s} {duration:.4f}s")
        return True, None
    except Exception as e:
        duration = time.time() - start
        print(f"✗ {module_name:50s} {duration:.4f}s - FAILED")
        print(f"  Error: {e}")
        return False, str(e)

print("=" * 80)
print("STARTUP FORENSICS - PHASE 22")
print("=" * 80)
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"Working Directory: {Path.cwd()}")
print("=" * 80)

# Test critical imports in order
print("\n1. CORE DEPENDENCIES")
print("-" * 80)
core_deps = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "sqlalchemy",
    "asyncpg",
    "redis",
    "celery",
    "grpcio",
    "qdrant_client",
]

for dep in core_deps:
    trace_import(dep)

print("\n2. OBSERVABILITY DEPENDENCIES")
print("-" * 80)
obs_deps = [
    "structlog",
    "prometheus_client",
    "opentelemetry_api",
    "opentelemetry_sdk",
    "opentelemetry_exporter_otlp",
]

for dep in obs_deps:
    trace_import(dep)

print("\n3. ML DEPENDENCIES")
print("-" * 80)
ml_deps = [
    "torch",
    "transformers",
    "sentence_transformers",
    "numpy",
    "pandas",
]

for dep in ml_deps:
    trace_import(dep)

print("\n4. AI SDK DEPENDENCIES")
print("-" * 80)
ai_deps = [
    "google.generativeai",
]

for dep in ai_deps:
    trace_import(dep)

print("\n5. APP MODULE IMPORTS")
print("-" * 80)
app_modules = [
    "app.core.config",
    "app.core.exceptions",
    "app.logging",
    "app.db.database",
    "app.middleware.request_context",
    "app.middleware.security",
    "app.middleware.tenant",
    "app.observability.tracing",
    "app.api.v1.router",
]

for module in app_modules:
    trace_import(module)

print("\n6. MAIN APP IMPORT")
print("-" * 80)
success, error = trace_import("app.main")

if success:
    print("\n7. APP FACTORY TEST")
    print("-" * 80)
    try:
        from app.main import create_app
        app = create_app()
        print("✓ create_app() succeeded")
        print(f"  App title: {app.title}")
        print(f"  App version: {app.version}")
    except Exception as e:
        print(f"✗ create_app() FAILED: {e}")
        traceback.print_exc()

print("\n" + "=" * 80)
print("FORENSICS COMPLETE")
print("=" * 80)
