# Page Rendering Forensics

## Symptom

Sidebar navigation updated active state, but the visible main content area appeared empty.

## Root Cause

The application shell rendered the desktop sidebar as `lg:static` while the sidebar also had `h-full`. In normal document flow this made the sidebar consume the first viewport-height block before `<main>`.

The page components were still mounting, but on desktop the main content started below the sidebar block, outside the first viewport. This presented as a blank route body even though navigation state changed.

## Fix

`apps/web/components/app-shell.tsx` now keeps the sidebar fixed at desktop sizes and moves main content beside it:

- Sidebar: `fixed left-0 top-0 h-full w-72 ... lg:translate-x-0`
- Main: `relative min-h-screen lg:ml-72`
- Content wrapper: `relative z-10 p-4 sm:p-6 xl:p-8`

This restores visible child rendering for all authenticated routes.

## Route Validation

The Next production build generated the route table successfully and included:

- `/dashboard`
- `/documents`
- `/candidates`
- `/jobs`
- `/search`
- `/analytics`
- `/settings`

The deleted `/copilot` route is no longer generated.

## Rendering Contract

Every authenticated page must render at least:

- A visible page title.
- A backend-connected loading, error, data, or empty state.
- A useful empty-state action when the database has no data.

Blank panels are considered a regression.
