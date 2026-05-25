# Authentication Flow

## Login

`/login` posts email and password to `/api/v1/auth/login`. On success, the frontend stores the access and refresh tokens in local storage and cookies, refreshes `/api/v1/auth/me`, and redirects to `/dashboard`.

## Signup

`/signup` posts organization name, full name, email, and password to `/api/v1/auth/register`. The success path is the same as login.

## Auth State

`AuthProvider` initializes from the persisted access token. If a token exists, it loads the authenticated user from `/api/v1/auth/me`. API requests attach the bearer token through `apiFetch`.

## Refresh

When `apiFetch` receives a `401`, it calls `/api/v1/auth/refresh` once, stores the returned token pair, and retries the original request. If refresh fails, tokens are cleared and the browser is sent to `/login`.

## Logout

Logout is available in `AppShell` on every authenticated route. It clears:

- `access_token`
- `refresh_token`
- matching auth cookies
- in-memory user state

The user is redirected to `/`.
