# Auth Session Audit

Backend:
- JWTs include `sub`, `org`, `roles`, `typ`, `iat`, and `exp`.
- Access-token dependencies reject missing, malformed, expired, inactive, deleted, and org-mismatched users.
- Refresh rejects invalid refresh tokens and inactive users.
- OTP-protected login remains enforced for pending verification.

Frontend hardening:
- `getAccessToken` and `getRefreshToken` now clear expired/malformed JWTs before reuse.
- Logout clears localStorage, auth cookies, org/recruiter auth-scoped storage, and broadcasts `auth:cleared`.
- React Query cache is cleared on auth cleanup to avoid stale workspace restoration.
- Middleware deletes expired cookies and redirects protected routes to `/login`.

Remaining risk:
- Refresh-token revocation is not persisted server-side, so logout is client-side only until token expiry.
- Middleware performs expiry parsing only; backend remains the source of truth for signature validation.

