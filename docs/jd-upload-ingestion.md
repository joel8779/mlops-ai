# JD Upload Ingestion

JD upload now supports recruiter-first ingestion instead of requiring pasted text.

## Flow

1. Recruiter uploads a PDF or DOCX.
2. Backend extracts text through `ExtractionService`.
3. `JobIntelligenceService.preview_upload` infers the title, role category, skills, experience, education, keywords, and semantic requirements.
4. Frontend auto-populates the job form from the extraction preview.
5. Recruiter may edit fields.
6. Creating the job stores parsed intelligence and queues JD embedding.

## APIs

- `POST /api/v1/jobs/extract`: preview JD extraction without creating a job.
- `POST /api/v1/jobs/upload`: create a job directly from an uploaded JD; title is optional.
- `POST /api/v1/jobs`: create a job from edited text.

## Error Behavior

Extraction failures return structured 422 errors with a reason. Job creation catches common database failures and returns recruiter-facing messages instead of the old generic `Database operation failed` response.
