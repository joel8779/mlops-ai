# Application Flow Map

## Public Entry

`/` remains public even when auth cookies exist. Users can choose:

- `/login`
- `/signup`

Compatibility routes:

- `/landing`
- `/sign-in`
- `/sign-up`

## Auth Flow

Login and signup call the backend auth API, persist tokens, refresh `/auth/me`, and redirect to `/dashboard`.

The login page does not auto-redirect just because a cookie exists. Public pages remain stable.

## Authenticated Flow

After auth:

1. `/dashboard` opens mission control.
2. `/documents` starts candidate intelligence ingestion.
3. Uploaded resumes are sent to `/resumes/upload`.
4. The UI polls `/resumes/{id}` until processing reaches `parsed`, `embedded`, or `failed`.
5. Parsed candidates appear in `/candidates`.
6. Users can run `/search`, review `/analytics`, and manage `/jobs`.

## Logout

Logout is always visible in the sidebar. It clears local storage, auth cookies, and in-memory user state, then returns the user to `/`.

## Backend Connectivity

Core pages remain connected to real endpoints:

- Auth: `/auth/login`, `/auth/register`, `/auth/me`, `/auth/refresh`
- Uploads: `/resumes`, `/resumes/upload`, `/resumes/{id}`
- Candidates: `/candidates`, `/candidates/{id}`, `/feedback/ranking`
- Jobs: `/jobs`
- Search: `/search/candidates`
- AI: `/ai/summary`, `/ai/interview-questions`, `/ai/compare`
- ATS: `/ats/resumes/{id}/score`
- Analytics: `/analytics/executive`
