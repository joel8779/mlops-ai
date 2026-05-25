# Recruiter Command Center Architecture

## Shell

`apps/web/components/app-shell.tsx` is the single authenticated command frame. It owns:

- Tactical sidebar
- Current route highlight
- Top operational status bar
- Mobile navigation
- Persistent logout
- Client-side auth guard

## Mission Control Dashboard

`/dashboard` combines live backend data from:

- `/analytics/executive`
- `/candidates`
- `/resumes`

The dashboard renders intelligence cards, live pipeline states, semantic search entry, quick actions, ingestion activity, and AI insight feed. Empty states appear when backend data is absent.

## Primary Workflow

The operating workflow starts on `/documents`:

1. Resume upload
2. OCR and parsing state
3. Embedding and indexing state
4. Candidate creation
5. Candidate profile, search, analytics

## Connected Workstations

| Route | Workstation Role |
| --- | --- |
| `/documents` | Candidate intelligence ingestion |
| `/candidates` | Candidate dossier list |
| `/candidates/{id}` | Candidate intelligence profile |
| `/jobs` | Role command deck |
| `/search` | Neural search terminal |
| `/analytics` | Recruiting telemetry |
| `/settings` | Operator settings |
