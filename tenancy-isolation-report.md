# Tenancy Isolation Report

Confirmed design:
- Auth context carries `organization_id` and user identity from JWT.
- Backend route dependencies enforce authenticated access.
- Repositories and services consistently include organization filters in recruiting workflows.
- Deleted rows are filtered from analytics and primary workflow counts.

Fix applied:
- Dashboard analytics no longer scope shared workspace metrics to only the current owner. Same-org users now see shared candidate/job counts and dashboard aggregations.

Validation:
- Added and passed a same-org dashboard sharing regression test.
- Existing analytics tests confirm deleted rows remain excluded.

Remaining audit notes:
- Some older modules still use `owner_id` as a secondary boundary. That is safe for private resources but should be reviewed whenever a feature is intended to be same-org shared.

