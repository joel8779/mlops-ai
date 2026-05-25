# Current Runtime State - Phase 23 Baseline

**Captured**: 2026-05-25  
**Purpose**: Immutable baseline before Phase 23 recovery changes.

## Runtime

- Repository: `C:\Users\Lenovo\Desktop\mlops-ai`
- Existing virtual environment: `C:\Users\Lenovo\Desktop\mlops-ai\.venv`
- Existing venv Python: `Python 3.11.9`
- Existing venv pip: `pip 26.1.1` from `.venv\Lib\site-packages\pip`
- Project Python constraint: `>=3.11,<3.13` in `apps/api/pyproject.toml`
- Unactivated shell `python` resolution includes non-project interpreters:
  - `C:\Users\Lenovo\AppData\Local\Python\pythoncore-3.14-64\python.exe`
  - `C:\Users\Lenovo\AppData\Local\Microsoft\WindowsApps\python.exe`
  - `C:\Users\Lenovo\AppData\Local\Python\bin\python.exe`
- Unactivated shell `pip` resolution includes non-project launchers:
  - `C:\Users\Lenovo\AppData\Local\Microsoft\WindowsApps\pip.exe`
  - `C:\Users\Lenovo\AppData\Local\Python\bin\pip.exe`
- Wheel artifacts found inside the existing venv:
  - `.venv\Lib\site-packages\numpy-2.2.3-cp311-cp311-win_amd64.whl`
  - `.venv\Lib\site-packages\scipy-1.17.1-cp311-cp311-win_amd64.whl`

## Requirement Files Present

- `apps/api/requirements-core.txt`
- `apps/api/requirements-observability.txt`
- `apps/api/requirements-ai.txt`
- `apps/api/requirements-ml.txt`
- `apps/api/requirements-dev.txt`
- `apps/api/requirements.txt`
- `apps/api/constraints.txt`
- `apps/api/pyproject.toml`

## Current Startup Command

Run from `apps/api` with the existing venv explicitly selected:

```powershell
..\..\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --reload
```

## First Startup Error Before Changes

The server reloader starts, then the application import fails while constructing `Settings`:

```text
pydantic_core._pydantic_core.ValidationError: 1 validation error for Settings
debug
  Input should be a valid boolean, unable to interpret input
  input_value='release'
```

The first failing import path ends at `apps/api/app/core/config.py:175` (`settings = get_settings()`).
This is a settings-input mismatch (`DEBUG=release` for a boolean setting), not an ML, telemetry, or middleware cascade.

## Installed Packages In Existing Venv

Captured with `.\.venv\Scripts\python.exe -m pip list --format=freeze` before cleanup:

```text
aiosqlite==0.22.1
alembic==1.14.0
amqp==5.3.1
annotated-types==0.7.0
anyio==4.13.0
apprise==1.10.0
asgi-lifespan==2.1.0
asgiref==3.11.1
asyncpg==0.30.0
attrs==26.1.0
bcrypt==4.2.1
billiard==4.2.4
blinker==1.9.0
boto3==1.35.90
botocore==1.35.90
cachetools==5.5.2
celery==5.4.0
certifi==2026.5.20
cffi==2.0.0
charset-normalizer==3.4.7
click==8.1.8
click-didyoumean==0.3.1
click-plugins==1.1.1.2
click-repl==0.3.0
cloudpickle==3.1.2
colorama==0.4.6
contourpy==1.3.3
coolname==2.2.0
croniter==6.2.2
cryptography==44.0.0
cycler==0.12.1
databricks-sdk==0.110.0
dateparser==1.4.0
Deprecated==1.3.1
dnspython==2.8.0
docker==7.1.0
ecdsa==0.19.2
email_validator==2.2.0
exceptiongroup==1.3.1
fastapi==0.115.6
filelock==3.29.0
Flask==3.1.3
fonttools==4.63.0
fsspec==2026.4.0
gitdb==4.0.12
GitPython==3.1.50
google-ai-generativelanguage==0.6.10
google-api-core==2.30.3
google-api-python-client==2.196.0
google-auth==2.53.0
google-auth-httplib2==0.4.0
google-generativeai==0.8.3
googleapis-common-protos==1.75.0
graphene==3.4.3
graphql-core==3.2.8
graphql-relay==3.2.0
graphviz==0.21
greenlet==3.5.1
griffe==1.15.0
grpcio==1.80.0
grpcio-status==1.76.0
grpcio-tools==1.76.0
h11==0.16.0
h2==4.3.0
hpack==4.1.0
httpcore==1.0.9
httplib2==0.31.2
httptools==0.7.1
httpx==0.28.1
huggingface_hub==0.36.2
humanize==4.15.0
hyperframe==6.1.0
idna==3.16
importlib_metadata==8.5.0
itsdangerous==2.2.0
Jinja2==3.1.6
jinja2-humanize-extension==0.4.0
jmespath==1.1.0
joblib==1.4.2
jsonpatch==1.33
jsonpointer==3.1.1
jsonschema==4.26.0
jsonschema-specifications==2025.9.1
kiwisolver==1.5.0
kombu==5.6.2
limits==5.8.0
lxml==6.1.1
Mako==1.3.12
Markdown==3.10.2
markdown-it-py==4.2.0
MarkupSafe==3.0.3
matplotlib==3.10.9
mdurl==0.1.2
mlflow==2.19.0
mlflow-skinny==2.19.0
mpmath==1.3.0
neo4j==5.27.0
networkx==3.4.2
numpy==2.2.3
oauthlib==3.3.1
opentelemetry-api==1.29.0
opentelemetry-exporter-otlp==1.29.0
opentelemetry-exporter-otlp-proto-common==1.29.0
opentelemetry-exporter-otlp-proto-grpc==1.29.0
opentelemetry-exporter-otlp-proto-http==1.29.0
opentelemetry-instrumentation==0.50b0
opentelemetry-instrumentation-asgi==0.50b0
opentelemetry-instrumentation-celery==0.50b0
opentelemetry-instrumentation-fastapi==0.50b0
opentelemetry-instrumentation-httpx==0.50b0
opentelemetry-instrumentation-redis==0.50b0
opentelemetry-instrumentation-sqlalchemy==0.50b0
opentelemetry-proto==1.29.0
opentelemetry-sdk==1.29.0
opentelemetry-semantic-conventions==0.50b0
opentelemetry-util-http==0.50b0
orjson==3.11.9
packaging==24.2
pandas==2.2.3
passlib==1.7.4
pathspec==1.1.1
pdfminer.six==20231228
pdfplumber==0.11.5
pendulum==3.2.0
pillow==11.3.0
pip==26.1.1
portalocker==2.10.1
prefect==3.1.12
prometheus_client==0.21.1
prometheus-fastapi-instrumentator==7.0.0
prompt_toolkit==3.0.52
proto-plus==1.28.0
protobuf==6.33.6
psycopg==3.2.3
psycopg-binary==3.2.3
pyarrow==18.1.0
pyasn1==0.6.3
pyasn1_modules==0.4.2
pycparser==3.0
pydantic==2.10.4
pydantic_core==2.27.2
pydantic-extra-types==2.11.1
pydantic-settings==2.7.1
Pygments==2.20.0
PyMuPDF==1.25.1
pyparsing==3.3.2
pypdfium2==5.8.0
pytesseract==0.3.13
python-dateutil==2.9.0.post0
python-docx==1.1.2
python-dotenv==1.2.2
python-jose==3.3.0
python-multipart==0.0.20
python-slugify==8.0.4
python-socks==2.8.1
pytz==2024.2
pywin32==311
PyYAML==6.0.3
qdrant-client==1.12.1
readchar==4.2.2
redis==5.2.1
referencing==0.37.0
regex==2026.5.9
requests==2.34.2
requests-oauthlib==2.0.0
rfc3339-validator==0.1.4
rich==13.9.4
rpds-py==0.30.0
rsa==4.9.1
ruamel.yaml==0.19.1
s3transfer==0.10.4
safetensors==0.7.0
scikit-learn==1.6.0
scipy==1.17.1
sentence-transformers==3.3.1
setuptools==81.0.0
shellingham==1.5.4
six==1.17.0
slowapi==0.1.9
smmap==5.0.3
sniffio==1.3.1
SQLAlchemy==2.0.36
sqlparse==0.5.5
starlette==0.41.3
stripe==11.4.1
structlog==24.4.0
sympy==1.14.0
tenacity==9.0.0
text-unidecode==1.3
threadpoolctl==3.6.0
tokenizers==0.21.4
toml==0.10.2
torch==2.12.0
tqdm==4.67.3
transformers==4.47.1
typer==0.13.1
typing_extensions==4.15.0
tzdata==2026.2
tzlocal==5.3.1
ujson==5.12.1
uritemplate==4.2.0
urllib3==2.7.0
uvicorn==0.34.0
vine==5.1.0
waitress==3.0.2
watchfiles==1.2.0
wcwidth==0.7.0
websockets==13.1
Werkzeug==3.1.8
wheel==0.47.0
wrapt==1.17.3
xgboost==2.1.3
zipp==4.1.0
```
# Current Runtime State - Phase 42

Date: 2026-05-25

NEURAL OPS is currently a connected FastAPI + Next.js recruiting intelligence platform with PostgreSQL, Redis/Celery, Qdrant, OCR, Gemini provider plumbing, and sentence-transformer embeddings. The product surface is no longer a placeholder dashboard; the remaining failures are integration gaps between ingestion, matching, ATS, workflow state, and frontend hydration.

Important verified state:

- ATS is modeled as a job-scoped relationship through `candidate_id + job_description_id`; global resume scoring is rejected.
- Candidate matching persists `CandidateMatch` per job and now marks job-scoped workflow state as `ranked`.
- Recruiter feedback now updates per-job workflow state for `shortlisted`, `interviewing`, `rejected`, and `hired`.
- Semantic search returns candidate-level aggregate results, not raw vector chunks.
- Candidate identity extraction now blocks the `"Candidate Profile"` false positive and avoids overwriting a real name with fallback identity.
- The current local `.env` has `DEBUG=release`, which blocks API startup because `DEBUG` must be boolean. Override with `DEBUG=false` or fix the environment value.

Validation run:

- `python -m compileall apps/api/app` passed.
- API import passed with `DEBUG=false`.
- `npm.cmd exec tsc -- --noEmit` passed.
- `pytest` is not installed in the local `.venv`.
- `npm run lint` is blocked because ESLint is not installed for the existing `next lint` script.

Open runtime risks:

- Resume and JD ingestion still depend on local OCR/parser binaries, object storage configuration, Redis/Celery availability, and embedding/Qdrant readiness.
- Gemini structured extraction plumbing exists, but JD extraction still has deterministic fallback behavior and should be promoted to Gemini-first extraction once provider/runtime credentials are confirmed.
- Existing databases need Alembic migration `0005_pipeline_stage_contract` to convert old pipeline stage enum values to the product contract.
