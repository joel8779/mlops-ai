# Application User Flow

## Public Flow

1. `/` renders the landing page with product overview, Sign In, and Get Started.
2. Sign In opens `/login`.
3. Get Started opens `/signup`.
4. Login and signup both authenticate against `/api/v1/auth/*`.
5. Successful authentication stores tokens, refreshes the current user, and redirects to `/dashboard`.

## Authenticated Flow

All authenticated routes render inside the single frontend `AppShell`:

- `/dashboard`
- `/documents`
- `/candidates`
- `/jobs`
- `/search`
- `/copilot`
- `/analytics`
- `/settings`

The shell provides sidebar navigation, topbar account context, active route highlighting, mobile navigation, and a persistent logout action.

## Primary Workflow

The primary workflow starts at `/documents`:

1. User uploads PDF, DOCX, or DOC resume files.
2. Frontend sends the file to `/api/v1/resumes/upload`.
3. Upload progress is shown from the browser upload event.
4. The page polls `/api/v1/resumes/{id}` for backend processing status.
5. When a candidate is linked, the user can open `/candidates/{id}` or use `/search`.

## Logout Flow

Logout is always available in the sidebar. It clears local storage tokens, clears auth cookies, resets auth state, and redirects to `/`.
