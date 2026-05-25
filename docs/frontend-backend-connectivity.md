# Frontend Backend Connectivity

## API Client

All frontend API calls go through `apps/web/lib/api.ts`, using `NEXT_PUBLIC_API_BASE_URL` or `http://localhost:8000/api/v1` by default.

## Connectivity Map

| Feature | Frontend Route | Backend Endpoint |
| --- | --- | --- |
| Login | `/login` | `POST /auth/login` |
| Signup | `/signup` | `POST /auth/register` |
| Current user | Auth provider, settings | `GET /auth/me` |
| Token refresh | API client | `POST /auth/refresh` |
| Dashboard | `/dashboard` | `/analytics/executive`, `/candidates`, `/resumes` |
| Documents | `/documents` | `/resumes`, `/resumes/upload`, `/resumes/{id}` |
| Candidates | `/candidates` | `/candidates`, `/feedback/ranking` |
| Candidate detail | `/candidates/{id}` | `/candidates/{id}`, `/ai/summary`, `/ats/resumes/{id}/score` |
| Jobs | `/jobs` | `/jobs` |
| Search | `/search` | `POST /search/candidates` |
| AI Copilot | `/copilot` | `POST /ai/copilot` |
| Analytics | `/analytics` | `GET /analytics/executive` |

## Empty States

Pages do not render fake metrics or mock cards. When backend data is absent, pages render empty states that direct the user to upload documents or create jobs.

## Backend Change Added

`GET /api/v1/resumes` was added so the Documents page and Dashboard can show real uploaded document data instead of local-only upload state.
