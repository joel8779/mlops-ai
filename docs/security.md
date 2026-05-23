# Security

- JWT authentication and RBAC permissions protect recruiter workflows.
- Every user-visible query is scoped by organization ID.
- API keys are hashed and scoped.
- Audit logs capture sensitive workflow events.
- Uploads are content-type checked, size-limited, and signature-scanned.
- Prompt injection filters block common exfiltration instructions before LLM calls.
- Kubernetes secrets and environment-based configuration keep credentials out of code.
