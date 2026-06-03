# AI Resume Intelligence Platform

## Stack

Frontend:

* Next.js
* TypeScript
* Tailwind

Backend:

* FastAPI
* SQLAlchemy
* Alembic
* Celery
* Redis
* PostgreSQL
* Qdrant
* Gemini

Infrastructure:

* Docker Compose
* MinIO
* MLflow

## Architecture

Organization-based ATS.

Organizations contain:

* Recruiters
* Jobs
* Candidates
* ATS Scores
* Semantic Search

Users belong to organizations.

Same organization:

* shared candidates
* shared jobs
* shared ATS

Different organizations:

* isolated

## Authentication

Users:

* signup
* login
* logout
* OTP verification

Organization:

* create org + PIN
* join existing org with PIN

## Current Features

Working:

* Resume parsing
* ATS scoring
* Semantic search
* Gemini summaries
* Candidate management
* JD parsing
* Docker deployment

Partially working:

* SMTP
* OTP verification
* Forgot password

Known Issues:

* Forgot password flow broken
* Skills extraction inconsistent
* JD title extraction occasionally fails
* Auth session bugs
