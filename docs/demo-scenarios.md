# Demo Scenarios - PHASE 16

**Date**: 2026-05-23
**Phase**: STEP 9 - DEMO READINESS

## Demo Overview

This document provides step-by-step demo scenarios for the AI Resume Intelligence Platform. These scenarios showcase the key features and workflows of the platform.

## Prerequisites

### Infrastructure
- PostgreSQL database running
- Redis running
- Qdrant vector database running
- MinIO/S3 object storage running
- Backend API running (http://localhost:8000)
- Frontend running (http://localhost:3000)

### Demo Data
Run the seed script to populate demo data:
```bash
cd apps/api
python scripts/seed_demo_data.py
```

This creates:
- 3 organizations
- 4 recruiters
- 3 job descriptions
- 5 candidates with resumes
- Candidate matches, pipeline stages, notes, activities, and feedback

---

## Scenario 1: Recruiter Onboarding

### Objective
Demonstrate the registration and onboarding flow for a new recruiter.

### Steps

1. **Navigate to Sign In**
   - Open http://localhost:3000/sign-in
   - Click "Create Account"

2. **Register Organization**
   - Enter organization name: "Demo Company"
   - Enter email: "recruiter@demo.com"
   - Enter password: "demo123"
   - Enter full name: "Demo Recruiter"
   - Click "Register"

3. **Dashboard Access**
   - After registration, redirect to dashboard
   - View welcome message
   - See onboarding checklist

4. **Complete Profile**
   - Add recruiter profile photo
   - Set notification preferences
   - Configure team settings

### Expected Outcome
- New organization created
- Recruiter account created with admin role
- Access to dashboard with onboarding guidance

---

## Scenario 2: Resume Upload Demo

### Objective
Demonstrate the resume upload and processing pipeline.

### Steps

1. **Navigate to Resumes**
   - Click "Resumes" in navigation
   - Click "Upload Resume"

2. **Upload Resume**
   - Select a sample PDF resume
   - Click "Upload"
   - See processing status (queued → parsing → embedded → complete)

3. **View Processed Resume**
   - Click on the uploaded resume
   - View extracted text
   - View extracted skills
   - View ATS score

4. **Create Candidate**
   - Click "Create Candidate"
   - Auto-populate from resume data
   - Add additional information
   - Save candidate

### Expected Outcome
- Resume uploaded to object storage
- Text extracted via OCR/parsing
- Skills extracted and normalized
- Embeddings generated and stored in Qdrant
- ATS score calculated
- Candidate created with resume link

---

## Scenario 3: Semantic Search Demo

### Objective
Demonstrate semantic search for candidates using natural language queries.

### Steps

1. **Navigate to Search**
   - Click "Search" in navigation
   - See search input and filters

2. **Natural Language Search**
   - Enter query: "Find senior machine learning engineers with NLP experience"
   - Click "Search"
   - View results ranked by semantic similarity

3. **Apply Filters**
   - Add skill filter: "python"
   - Add location filter: "San Francisco"
   - See filtered results

4. **View Candidate Details**
   - Click on a search result
   - View candidate profile
   - View match score breakdown
   - View resume snippet

### Expected Outcome
- Query converted to embedding
- Semantic search performed in Qdrant
- Results ranked by similarity
- Filters applied correctly
- Reranking boosts keyword matches
- Pagination works correctly

---

## Scenario 4: AI Copilot Demo

### Objective
Demonstrate the AI-powered recruiting copilot for answering questions.

### Steps

1. **Navigate to Copilot**
   - Click "Copilot" in navigation
   - See chat interface

2. **Ask Question**
   - Enter: "What are the top skills for machine learning engineers?"
   - Send message
   - View AI response with citations

3. **Context-Aware Questions**
   - Enter: "How does James Rodriguez compare to other candidates?"
   - View response with candidate comparison
   - See confidence score

4. **View Artifacts**
   - Ask for interview questions
   - View generated questions
   - See structured output

### Expected Outcome
- Question processed with RAG
- Context retrieved from vector database
- Gemini generates response
- Citations displayed
- Confidence score shown
- Artifacts rendered correctly

---

## Scenario 5: Ranking Explanation Demo

### Objective
Demonstrate AI-powered candidate ranking and explanation.

### Steps

1. **Navigate to Jobs**
   - Click "Jobs" in navigation
   - Select "Senior Machine Learning Engineer"

2. **View Rankings**
   - Click "Rank Candidates"
   - View ranked candidate list
   - See match scores

3. **View Explanation**
   - Click on a candidate
   - View ranking explanation
   - See score breakdown:
     - Semantic similarity
     - Skill match
     - Experience match
     - Education match
   - View matched/missing skills

4. **Provide Feedback**
   - Click "Shortlist" or "Reject"
   - Feedback logged for learning
   - Ranking model improves over time

### Expected Outcome
- Candidates ranked by hybrid score
- Explanation shows score components
- Skills matched/missing displayed
- Feedback recorded
- Model learns from feedback

---

## Scenario 6: Analytics Dashboard Demo

### Objective
Demonstrate the executive analytics dashboard.

### Steps

1. **Navigate to Analytics**
   - Click "Analytics" in navigation
   - View executive dashboard

2. **View Hiring Funnel**
   - See funnel visualization
   - View candidates by stage
   - View conversion rates

3. **View Top Skills**
   - See skill demand chart
   - View skill trends
   - View skill growth

4. **View Recruiter Efficiency**
   - See actions logged
   - See automation rate
   - See time-to-hire metrics

5. **View Ranking Accuracy**
   - See positive feedback rate
   - See precision/recall metrics
   - See model performance

### Expected Outcome
- Dashboard displays key metrics
- Funnel visualization shows pipeline health
- Skills analytics show demand trends
- Efficiency metrics show recruiter productivity
- Accuracy metrics show AI performance

---

## Demo Script Summary

### Quick Demo (5 minutes)
1. Show root endpoint with service info
2. Show Swagger docs at /docs
3. Show semantic search with natural language query
4. Show AI copilot answering a question
5. Show analytics dashboard

### Full Demo (15 minutes)
1. Recruiter onboarding (2 min)
2. Resume upload and processing (3 min)
3. Semantic search with filters (2 min)
4. AI copilot with context (3 min)
5. Ranking and explanation (3 min)
6. Analytics dashboard (2 min)

### Technical Demo (20 minutes)
1. Show API endpoints in Swagger
2. Show database schema
3. Show vector database operations
4. Show Celery task queue
5. Show monitoring metrics
6. Show logging and tracing

## Demo Tips

### Preparation
- Ensure all infrastructure is running
- Seed demo data before demo
- Have sample resumes ready
- Test all scenarios beforehand
- Prepare fallback responses

### During Demo
- Start with high-level overview
- Focus on user value, not technical details
- Use realistic scenarios
- Highlight AI features
- Show data-driven insights
- Keep it interactive

### Common Questions
- **How does it work?** → Explain RAG + embeddings
- **Is it accurate?** → Show ranking explanation
- **How fast is it?** → Show response times
- **Can it scale?** → Show architecture
- **Is it secure?** → Show auth and RBAC

## Demo Environment

### Local Development
```bash
# Start infrastructure
docker-compose up -d postgres redis qdrant minio

# Start backend
cd apps/api
uvicorn app.main:create_app --reload --host 0.0.0.0 --port 8000

# Start frontend
cd apps/web
npm run dev

# Seed data
cd apps/api
python scripts/seed_demo_data.py
```

### Production Demo
- Use staging environment
- Use production-like data
- Ensure all services are healthy
- Monitor for errors during demo
- Have rollback plan ready

## Success Criteria

A successful demo should:
- Show all key features working
- Demonstrate real user value
- Be smooth and error-free
- Answer audience questions
- Leave audience impressed
- Generate follow-up interest

## Next Steps

After completing demo scenarios:
1. Record demo video
2. Create demo GIFs for README
3. Add demo screenshots to docs
4. Update landing page
5. Prepare demo script for sales
