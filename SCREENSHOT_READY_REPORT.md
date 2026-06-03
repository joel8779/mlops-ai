# Screenshot Readiness Report

All services for the AI Resume Intelligence Platform are currently running, healthy, and populated with the exact mock demo data required for taking screenshots and product walkthroughs.

## 1. Running Services Status

All core infrastructure and application components are running locally in Docker. You can verify this status via `docker compose ps`.

| Service | Container Name | Status | External Port | Internal Port |
|---|---|---|---|---|
| **Frontend** | `resume-intelligence-frontend-1` | Running (Ready) | `3000` | `3000` |
| **API Backend** | `resume-intelligence-api-1` | Running (Healthy) | `8000` | `8000` |
| **Worker** | `resume-intelligence-worker-1` | Running (Healthy) | - | `8000` |
| **PostgreSQL** | `resume-intelligence-postgres-1` | Running (Healthy) | `5432` | `5432` |
| **Redis** | `resume-intelligence-redis-1` | Running (Healthy) | `6379` | `6379` |
| **Qdrant** | `resume-intelligence-qdrant-1` | Running (Healthy) | `6333` | `6333` |
| **MinIO** | `resume-intelligence-minio-1` | Running (Healthy) | `9000-9001` | `9000-9001` |
| **MLflow** | `resume-intelligence-mlflow-1` | Running (Healthy) | `5000` | `5000` |

---

## 2. Accessibility URLs

Use the following local URLs to access the application and infrastructure dashboards:

- **Web Application Portal**: [http://localhost:3000](http://localhost:3000)
- **API Health Check**: [http://localhost:8000/live](http://localhost:8000/live)
- **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MinIO Console**: [http://localhost:9001](http://localhost:9001) (Credentials: `minioadmin` / `minioadmin`)
- **MLflow UI**: [http://localhost:5000](http://localhost:5000)

---

## 3. Demo Credentials

The database has been seeded with a single workspace containing the following credentials:

- **Organization**: `TalentFlow`
- **Email**: `recruiter_a@talentflow.com`
- **Password**: `demo123`

*Note: The user account is pre-verified and active, allowing you to bypass the OTP flow for immediate access.*

---

## 4. Seeded Data Overview

The following data has been populated to ensure clean, error-free screens:

### Jobs (2 active)
1. **Senior Machine Learning Engineer**
2. **Full Stack Developer**

### Candidates (3 profiles + parsed resumes)
1. **James Rodriguez**
   - **Headline**: Senior ML Engineer \| Ranking and NLP
   - **Skills**: Python, PyTorch, MLOps, Kubernetes, Docker, Redis
   - **Pipeline Stage**: Interviewing (for Senior ML Engineer) / Ranked (for Full Stack Developer)
2. **Emily Zhang**
   - **Headline**: Full Stack Developer \| React & Node.js Expert
   - **Skills**: React, TypeScript, Next.js, FastAPI, PostgreSQL, Redis, Node.js
   - **Pipeline Stage**: Shortlisted (for Senior ML Engineer) / Ranked (for Full Stack Developer)
3. **David Kim**
   - **Headline**: DevOps Engineer \| Kubernetes and Cloud Specialist
   - **Skills**: Kubernetes, Docker, Terraform, Prometheus, Grafana, AWS, GCP
   - **Pipeline Stage**: Ranked (for Senior ML Engineer) / Ranked (for Full Stack Developer)

### Realistic Match & ATS Scores Matrix
- **James Rodriguez**:
  - Senior ML Engineer: **92.50** (overall), **0.93** (semantic), **0.90** (skill)
  - Full Stack Developer: **53.00** (overall), **0.45** (semantic), **0.40** (skill)
- **Emily Zhang**:
  - Senior ML Engineer: **41.20** (overall), **0.35** (semantic), **0.30** (skill)
  - Full Stack Developer: **94.10** (overall), **0.95** (semantic), **0.92** (skill)
- **David Kim**:
  - Senior ML Engineer: **68.40** (overall), **0.70** (semantic), **0.65** (skill)
  - Full Stack Developer: **79.50** (overall), **0.81** (semantic), **0.78** (skill)

All resumes have been successfully chunked and indexed in Qdrant, enabling realistic semantic searching out-of-the-box.

---

## 5. Screenshot Checklist

You can capture screenshots of these key flows:

1. **Dashboard**: Navigate to `/dashboard` to view overall applicant counts, activity feeds, and recruitment pipelines.
2. **Candidate Profile**: Navigate to `/candidates` and click on *James Rodriguez* or *Emily Zhang* to view detailed resumes, parser outputs, skills lists, and recruiter notes.
3. **ATS Ranking**: Navigate to `/jobs` and select the **Senior Machine Learning Engineer** or **Full Stack Developer** role to see ranked candidate lists sorted by hybrid matching scores.
4. **Resume Upload**: Accessible via the resume uploader component on the dashboard or `/resumes/upload`.
5. **JD Upload**: Accessible via the "Create Job" form at `/jobs/new`.
6. **Semantic Search**: Navigate to `/search` (or search input on `/candidates`) and query (e.g. "production machine learning infrastructure") to view vector-ranked search results.
7. **Shortlist Email**: Open a candidate profile card and trigger the shortlist or email candidate action component.
8. **Organization Workspace**: Open organization settings/workspace page.

---

## 6. Known Issues / Telemetry Alerts

- **Telemetry Traces Exception**: You might notice transient connection errors in backend/worker logs for `http://localhost:4318/v1/traces`. This occurs because OpenTelemetry exporters are active but no local trace collector (such as Jaeger or Tempo) is running in the default dev stack. This is expected and does not impact functionality (spans are safely dropped).
