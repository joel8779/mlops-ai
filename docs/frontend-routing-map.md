# Frontend Routing Map

## Public Routes

| Route | Purpose |
| --- | --- |
| `/` | Landing page |
| `/landing` | Landing page compatibility route |
| `/login` | Email/password login |
| `/signup` | Account registration |
| `/sign-in` | Compatibility route rendering login |
| `/sign-up` | Compatibility route rendering signup |

## Authenticated Routes

| Route | Backend Dependency |
| --- | --- |
| `/dashboard` | Analytics, candidates, resumes |
| `/documents` | Resume upload, resume list, resume status |
| `/candidates` | Candidate list and feedback |
| `/candidates/{id}` | Candidate detail, AI summary, ATS score |
| `/jobs` | Job list and job creation |
| `/search` | Semantic candidate search |
| `/analytics` | Executive analytics |
| `/settings` | Authenticated user context |
| `/resumes` | Redirects to `/documents` |

## Shell Architecture

`apps/web/components/app-shell.tsx` is the authoritative authenticated layout. Individual authenticated pages no longer define their own sidebar, topbar, or logout control.

## Route Guarding

Authentication is enforced by `AppShell` using the persisted access token and current user state. Middleware only redirects authenticated users away from public entry points; it does not create local-storage/cookie race redirects for protected routes.
