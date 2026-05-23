# Local Observability Stability - PHASE 18

**Date**: 2026-05-23
**Phase**: STEP 6 - LOCAL OBSERVABILITY STABILITY

## Overview

Local development environments should be resilient to missing or misconfigured observability services. This document ensures that telemetry degrades gracefully and the application remains functional even when observability services are unavailable.

## Current Configuration

### OpenTelemetry Configuration

**Environment Variables**:
```env
OTEL_SERVICE_NAME=resume-intelligence-api
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_TRACES_EXPORTER=otlp
```

**Current Behavior**: If OTEL collector is not available, the application may fail to start or experience errors during tracing operations.

### Prometheus Configuration

**Environment Variables**:
```env
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090
```

**Current Behavior**: Prometheus metrics endpoint is always available, but if Prometheus server is not running, metrics won't be scraped.

### MLflow Configuration

**Environment Variables**:
```env
MLFLOW_TRACKING_URI=http://localhost:5000
```

**Current Behavior**: If MLflow is not available, ML experiment tracking will fail.

## Required Changes

### 1. Graceful Telemetry Degradation

**Problem**: OpenTelemetry initialization fails if collector is unavailable.

**Solution**: Wrap OTEL initialization in try-except and disable if unavailable.

```python
# apps/api/app/core/telemetry.py
import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def init_telemetry():
    """Initialize OpenTelemetry with graceful degradation."""
    if not os.getenv("OTEL_ENABLED", "false").lower() == "true":
        logger.info("Telemetry disabled via OTEL_ENABLED")
        return
    
    try:
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
        if not otlp_endpoint:
            logger.warning("OTEL_EXPORTER_OTLP_ENDPOINT not set, disabling telemetry")
            return
        
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider = TracerProvider()
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        logger.info("OpenTelemetry initialized successfully")
    except Exception as e:
        logger.warning(f"Failed to initialize OpenTelemetry: {e}. Continuing without telemetry.")
```

### 2. MLflow Graceful Degradation

**Problem**: MLflow tracking fails if server is unavailable.

**Solution**: Wrap MLflow operations in try-except and disable if unavailable.

```python
# apps/api/app/services/mlflow_service.py
import os
import mlflow

def init_mlflow():
    """Initialize MLflow with graceful degradation."""
    mlflow_uri = os.getenv("MLFLOW_TRACKING_URI")
    if not mlflow_uri:
        logger.warning("MLFLOW_TRACKING_URI not set, MLflow tracking disabled")
        return False
    
    try:
        mlflow.set_tracking_uri(mlflow_uri)
        # Test connection
        mlflow.get_experiment_by_name("default")
        logger.info("MLflow initialized successfully")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialize MLflow: {e}. MLflow tracking disabled.")
        return False

# Global flag for MLflow availability
MLFLOW_AVAILABLE = init_mlflow()

def log_experiment(params, metrics, artifacts):
    """Log experiment to MLflow if available."""
    if not MLFLOW_AVAILABLE:
        logger.debug("MLflow unavailable, skipping experiment logging")
        return
    
    try:
        with mlflow.start_run():
            mlflow.log_params(params)
            mlflow.log_metrics(metrics)
            for artifact in artifacts:
                mlflow.log_artifact(artifact)
    except Exception as e:
        logger.warning(f"Failed to log to MLflow: {e}")
```

### 3. Prometheus Metrics

**Problem**: Metrics endpoint is always available, but missing Prometheus server doesn't affect application.

**Solution**: No changes needed. Prometheus metrics endpoint is independent of Prometheus server.

**Configuration**: Keep as-is. The `/metrics` endpoint will continue to work even if Prometheus server is not running.

### 4. Structured Logging

**Problem**: Logs should remain readable even if JSON formatting fails.

**Solution**: Ensure logging configuration has fallback to plain text.

```python
# apps/api/app/core/logging.py
import os
import structlog

def configure_logging():
    """Configure structured logging with fallback."""
    log_json = os.getenv("LOG_JSON", "true").lower() == "true"
    
    try:
        if log_json:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.UnicodeDecoder(),
                    structlog.processors.JSONRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            logger.info("Structured logging configured (JSON)")
        else:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.dev.ConsoleRenderer()
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            logger.info("Structured logging configured (plain text)")
    except Exception as e:
        logger.warning(f"Failed to configure structured logging: {e}. Using default logging.")
        # Fallback to standard logging
        import logging
        logging.basicConfig(level=logging.INFO)
```

### 5. Startup Validation

**Problem**: Application fails to start if observability services are required.

**Solution**: Make observability services optional for local development.

```python
# apps/api/app/main.py
@app.on_event("startup")
async def startup_event():
    """Application startup with optional observability."""
    logger.info("Starting application...")
    
    # Initialize telemetry (optional)
    try:
        init_telemetry()
    except Exception as e:
        logger.warning(f"Telemetry initialization failed: {e}. Continuing without telemetry.")
    
    # Initialize MLflow (optional)
    try:
        init_mlflow()
    except Exception as e:
        logger.warning(f"MLflow initialization failed: {e}. Continuing without MLflow.")
    
    # Initialize other services
    await initialize_core_services()
```

## Environment Configuration

### Local Development Configuration

Add these environment variables to `.env` for local development:

```env
# Observability - Optional for Local Development
OTEL_ENABLED=false
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_TRACES_EXPORTER=otlp

# Prometheus - Always Available
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# MLflow - Optional for Local Development
MLFLOW_TRACKING_URI=http://localhost:5000

# Logging
LOG_JSON=false  # Use plain text for local development
LOG_LEVEL=INFO
```

### Production Configuration

Keep observability enabled for production:

```env
# Observability - Required for Production
OTEL_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=https://your-otlp-endpoint
OTEL_TRACES_EXPORTER=otlp

# Prometheus - Always Available
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9090

# MLflow - Required for Production
MLFLOW_TRACKING_URI=https://your-mlflow-uri

# Logging
LOG_JSON=true
LOG_LEVEL=INFO
```

## Validation

### Test 1: Start Without OTEL Collector

```bash
# Ensure OTEL collector is not running
docker compose stop otel-collector 2>/dev/null || true

# Start application
cd apps/api
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000

# Expected: Application starts successfully with warning about telemetry
```

### Test 2: Start Without MLflow

```bash
# Ensure MLflow is not running
docker compose stop mlflow

# Start application
cd apps/api
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000

# Expected: Application starts successfully with warning about MLflow
```

### Test 3: Start Without Any Observability

```bash
# Stop all observability services
docker compose stop otel-collector mlflow prometheus grafana loki 2>/dev/null || true

# Start application
cd apps/api
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000

# Expected: Application starts successfully, logs in plain text
```

### Test 4: Verify Logs Remain Readable

```bash
# Start application
cd apps/api
uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8000

# Make a request
curl http://localhost:8000/health

# Expected: Logs are readable (plain text or JSON)
```

## Recommendations

### Immediate Actions

1. ✅ Document observability stability requirements
2. ⚠️ Implement graceful degradation for OTEL
3. ⚠️ Implement graceful degradation for MLflow
4. ⚠️ Add fallback for logging configuration
5. ⚠️ Make observability services optional in startup

### Long-term Improvements

1. Add circuit breakers for external observability services
2. Implement observability health checks
3. Add observability metrics to health endpoint
4. Implement automatic fallback to local logging
5. Add observability configuration validation

## Next Steps

1. ✅ Local observability stability documentation complete
2. ⏭️ STEP 7: Developer experience documentation
3. ⏭️ STEP 8: Final local validation

## Conclusion

Local development environments should be resilient to missing or misconfigured observability services. The key changes needed are:
1. Implement graceful degradation for OTEL
2. Implement graceful degradation for MLflow
3. Add fallback for logging configuration
4. Make observability services optional in startup

These changes will ensure that the application remains functional even when observability services are unavailable, providing a better developer experience.
