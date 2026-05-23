PYTHON ?= .venv/bin/python
PIP ?= .venv/bin/pip
COMPOSE ?= docker compose -f docker-compose.dev.yml

ifeq ($(OS),Windows_NT)
PYTHON := .venv/Scripts/python.exe
PIP := .venv/Scripts/pip.exe
endif

.PHONY: bootstrap dev test lint format seed worker mlflow docs verify services down logs

bootstrap:
	python -c "from pathlib import Path; Path('.env').write_text(Path('.env.example').read_text(encoding='utf-8'), encoding='utf-8') if not Path('.env').exists() else None"
	python scripts/verify_env.py
	python -m venv .venv
	$(PYTHON) -m pip install --upgrade pip setuptools wheel
	$(PIP) install -r apps/api/requirements-dev.txt
	cd apps/web && npm install

dev:
	$(COMPOSE) up --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f api worker

verify:
	$(PYTHON) scripts/verify_env.py

services:
	$(PYTHON) scripts/verify_services.py

test:
	cd apps/api && ../../$(PYTHON) -m pytest -q --cov=app --cov-report=term-missing

lint:
	cd apps/api && ../../$(PYTHON) -m ruff check app
	cd apps/api && ../../$(PYTHON) -m mypy app
	cd apps/web && npm run lint

format:
	cd apps/api && ../../$(PYTHON) -m black app
	cd apps/api && ../../$(PYTHON) -m ruff check app --fix

seed:
	cd apps/api && ../../$(PYTHON) scripts/seed_demo.py

worker:
	cd apps/api && ../../$(PYTHON) -m celery -A app.workers.celery_app.celery_app worker --loglevel=INFO --concurrency=2

mlflow:
	$(COMPOSE) up mlflow

docs:
	$(PYTHON) -m http.server 8088 -d docs
