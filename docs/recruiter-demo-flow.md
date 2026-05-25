# Recruiter Demo Flow - PHASE 26

Date: 2026-05-25

## Demo Login

- URL: `http://localhost:3000`
- Demo recruiter: `sarah@northstar.demo`
- Password: `demo12345`
- Seed command: `.\.venv\Scripts\python.exe scripts\seed_demo_environment.py`
- Faster seed without Qdrant indexing: `.\.venv\Scripts\python.exe scripts\seed_demo_environment.py --skip-vector-index`

## Storyline

Northstar Talent Labs is hiring for AI platform roles. The recruiter opens the dashboard, reviews live funnel metrics, uploads or reviews resumes, searches semantically, asks the AI copilot for evidence, scores candidates, and records shortlist/interview feedback.

## End-To-End Flow

1. Sign in as Sarah Chen.
2. Open Dashboard and verify candidate, role, action, and funnel metrics load from `/api/v1/analytics/executive`.
3. Open Jobs and create or review active roles from `/api/v1/jobs`.
4. Open Candidates and verify real records from `/api/v1/candidates`.
5. Shortlist or mark a candidate for interview; this records `/api/v1/feedback/ranking`.
6. Open a candidate profile and generate an AI summary through `/api/v1/ai/summary`.
7. Run ATS scoring from the candidate profile through `/api/v1/ats/resumes/{resume_id}/score`.
8. Open Search and query: `python mlops ranking engineer with kubernetes`.
9. Verify semantic results come from Qdrant-backed `/api/v1/search/candidates`.
10. Open Copilot and ask: `Which candidates should I prioritize for the ML engineer role?`
11. Upload a PDF or DOCX resume from Uploads and watch the queued parsing flow.
12. Refresh Candidates or Search after worker processing completes.

## Integration Audit

- Auth/login: wired through `/auth/login`, `/auth/register`, `/auth/refresh`, `/auth/me`.
- JWT refresh: centralized in `apps/web/lib/api.ts`; failed refresh clears tokens and returns to sign-in.
- Protected routes: `AppShell` redirects unauthenticated users and shows skeleton loading.
- Resume upload: uses `FormData` without forcing JSON content type.
- Candidate list/detail: wired to `/candidates` and `/candidates/{id}`.
- Semantic search: wired to `/search/candidates`.
- AI copilot and summaries: wired to `/ai/copilot` and `/ai/summary`.
- ATS scoring: wired to `/ats/resumes/{resume_id}/score`.
- Analytics dashboard: wired to `/analytics/executive`.
- Jobs: wired to `/jobs` create/list APIs.
- Feedback: shortlist/interview actions use `/feedback/ranking`.

## Demo Readiness Notes

- OCR remains optional and startup-safe.
- Tesseract is external; image OCR should be validated separately with `scripts/test_ocr_runtime.py --include-image-ocr`.
- Vector search requires Qdrant and embedding model availability. The seed script reports degraded vector indexing instead of breaking the database seed.
- The platform now has a clean happy path for portfolio demos while preserving graceful failure behavior.
