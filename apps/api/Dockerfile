FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy layered requirements
COPY requirements-core.txt requirements-observability.txt requirements-ai.txt requirements-ml.txt ./
COPY constraints.txt ./

# Install GRPC ecosystem first (for binary compatibility)
RUN python -m pip install --upgrade pip setuptools wheel \
    && python -m pip install --no-cache-dir \
       grpcio==1.60.0 \
       grpcio-tools==1.60.0 \
       grpcio-status==1.60.0 \
       protobuf==4.25.1

# Build wheels for all layers
RUN python -m pip wheel --wheel-dir /wheels -r requirements-core.txt \
    && python -m pip wheel --wheel-dir /wheels -r requirements-observability.txt \
    && python -m pip wheel --wheel-dir /wheels -r requirements-ai.txt \
    && python -m pip wheel --wheel-dir /wheels -r requirements-ml.txt


FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       curl \
       libpq5 \
       tesseract-ocr \
       poppler-utils \
    && useradd --create-home --shell /usr/sbin/nologin appuser \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /wheels /wheels
COPY requirements-core.txt requirements-observability.txt requirements-ai.txt requirements-ml.txt ./
COPY constraints.txt ./
RUN python -m pip install --no-index --find-links=/wheels -r requirements-core.txt \
    && python -m pip install --no-index --find-links=/wheels -r requirements-observability.txt \
    && python -m pip install --no-index --find-links=/wheels -r requirements-ai.txt \
    && python -m pip install --no-index --find-links=/wheels -r requirements-ml.txt \
    && rm -rf /wheels

COPY app app
COPY alembic alembic
COPY alembic.ini alembic.ini

USER appuser
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -fsS http://localhost:8000/ready || exit 1

CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
