# Sidebar Routing Audit

## Active Routes

The authenticated sidebar now exposes the product workflow routes:

- `/dashboard` - workspace activation and operations overview
- `/documents` - resume upload and ingestion status
- `/candidates` - parsed profiles, resume state, and match status
- `/jobs` - job descriptions and candidate match insights
- `/search` - semantic candidate search
- `/analytics` - funnel, skills, processing, and activity metrics
- `/settings` - operator and workspace controls

## Removed Route

`/copilot` was removed from the frontend route map and sidebar.

Removed frontend code:

- `apps/web/app/copilot/page.tsx`
- Copilot sidebar item
- Copilot dashboard CTA
- `aiApi.copilot()` frontend helper

## Route Highlighting

Sidebar active state uses the current pathname:

```ts
pathname === item.href || pathname.startsWith(`${item.href}/`)
```

This supports index routes and nested detail routes such as `/candidates/[id]`.

## Page Content Requirement

Each sidebar route must render visible page content on mount. A route may show loading, error, populated data, or empty state, but it must never render an empty fragment or invisible shell-only screen.
