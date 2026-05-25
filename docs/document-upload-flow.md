# Document Upload Flow

## Entry Point

`/documents` is the primary onboarding and operating workflow for resumes.

## Supported Files

The frontend accepts:

- PDF
- DOCX
- DOC

Files are limited to 10MB before upload.

## Upload Sequence

1. User selects or drops a file.
2. Frontend uploads with `XMLHttpRequest` to `/api/v1/resumes/upload`.
3. Browser upload progress is displayed.
4. Backend returns a resume record with an initial processing status.
5. Frontend polls `/api/v1/resumes/{id}` until the status is `parsed`, `embedded`, or `failed`.
6. Uploaded documents are reloaded from `/api/v1/resumes`.

If the backend cannot enqueue the parser/OCR worker task, the API records the resume as `failed` with a processing error instead of crashing the request.

## Post Upload Actions

When the backend links a candidate to the uploaded resume, the UI exposes:

- View candidate profile
- Open semantic search
- Refresh processing status

## Backend Endpoints

| Endpoint | Purpose |
| --- | --- |
| `POST /api/v1/resumes/upload` | Upload and enqueue resume ingestion |
| `GET /api/v1/resumes` | List uploaded resumes for the organization |
| `GET /api/v1/resumes/{id}` | Read processing status and candidate linkage |
