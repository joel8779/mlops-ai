"""Seed demo data for AI Resume Intelligence Platform.

Generates realistic organizations, recruiters, job descriptions, candidates,
resumes, and analytics metrics for demo purposes.
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal
from app.models.domain import (
    Candidate,
    CandidateMatch,
    CandidatePipelineStage,
    CandidateSkill,
    JobDescription,
    Organization,
    RankingFeedback,
    RecruiterActivity,
    RecruiterNote,
    Resume,
    User,
)
from app.models.domain import PipelineStage as Stage


# Demo data templates
ORGANIZATIONS = [
    {"name": "TechCorp AI", "slug": "techcorp-ai"},
    {"name": "DataDriven Inc", "slug": "datadriven-inc"},
    {"name": "CloudScale Solutions", "slug": "cloudscale-solutions"},
]

RECRUITERS = [
    {"email": "sarah@techcorp.ai", "full_name": "Sarah Chen", "roles": ["admin"]},
    {"email": "mike@techcorp.ai", "full_name": "Mike Johnson", "roles": ["recruiter"]},
    {"email": "emma@datadriven.inc", "full_name": "Emma Wilson", "roles": ["admin"]},
    {"email": "alex@datadriven.inc", "full_name": "Alex Turner", "roles": ["recruiter"]},
]

JOB_DESCRIPTIONS = [
    {
        "title": "Senior Machine Learning Engineer",
        "description": """We are looking for a Senior Machine Learning Engineer to join our AI team.

The ideal candidate has:
- 5+ years of experience in machine learning
- Strong Python and TensorFlow/PyTorch skills
- Experience with NLP and computer vision
- Knowledge of MLOps and deployment
- PhD or Master's in CS or related field

You will work on cutting-edge AI projects including recommendation systems,
natural language processing, and computer vision applications.""",
        "role_category": "machine_learning",
        "years_experience_min": 5,
        "years_experience_max": 10,
        "required_skills": ["python", "tensorflow", "pytorch", "nlp", "mlops"],
        "optional_skills": ["kubernetes", "docker", "aws", "gcp"],
        "keywords": ["machine learning", "deep learning", "ai", "neural networks"],
    },
    {
        "title": "Full Stack Developer",
        "description": """Join our engineering team as a Full Stack Developer.

Requirements:
- 3+ years of full stack development experience
- Strong React and TypeScript skills
- Experience with Node.js and Python
- Knowledge of PostgreSQL and Redis
- Experience with cloud platforms

You will build and maintain our web applications, working closely with
product and design teams to deliver exceptional user experiences.""",
        "role_category": "full_stack",
        "years_experience_min": 3,
        "years_experience_max": 7,
        "required_skills": ["react", "typescript", "node.js", "python", "postgresql"],
        "optional_skills": ["redis", "docker", "kubernetes", "aws"],
        "keywords": ["full stack", "web development", "frontend", "backend"],
    },
    {
        "title": "DevOps Engineer",
        "description": """We are seeking a DevOps Engineer to manage our infrastructure.

Responsibilities:
- Design and implement CI/CD pipelines
- Manage cloud infrastructure (AWS/GCP)
- Implement monitoring and alerting
- Ensure system reliability and scalability
- Automate deployment processes

Requirements:
- 4+ years of DevOps experience
- Strong Kubernetes and Docker skills
- Experience with Terraform and Ansible
- Knowledge of monitoring tools (Prometheus, Grafana)""",
        "role_category": "devops",
        "years_experience_min": 4,
        "years_experience_max": 8,
        "required_skills": ["kubernetes", "docker", "terraform", "ansible", "aws"],
        "optional_skills": ["gcp", "prometheus", "grafana", "jenkins"],
        "keywords": ["devops", "infrastructure", "cloud", "automation"],
    },
]

CANDIDATE_TEMPLATES = [
    {
        "full_name": "James Rodriguez",
        "email": "james.rodriguez@email.com",
        "headline": "Senior ML Engineer with 7 years experience",
        "location": "San Francisco, CA",
        "summary": "Experienced machine learning engineer specializing in NLP and recommendation systems. Led multiple AI projects from research to production.",
        "skills": ["python", "tensorflow", "pytorch", "nlp", "mlops", "kubernetes", "docker"],
    },
    {
        "full_name": "Emily Zhang",
        "email": "emily.zhang@email.com",
        "headline": "Full Stack Developer | React & Node.js Expert",
        "location": "New York, NY",
        "summary": "Full stack developer with strong frontend and backend skills. Built scalable web applications for fintech and healthcare startups.",
        "skills": ["react", "typescript", "node.js", "python", "postgresql", "redis", "aws"],
    },
    {
        "full_name": "David Kim",
        "email": "david.kim@email.com",
        "headline": "DevOps Engineer | Cloud Infrastructure Specialist",
        "location": "Austin, TX",
        "summary": "DevOps engineer with expertise in Kubernetes, Terraform, and cloud platforms. Implemented CI/CD pipelines for enterprise applications.",
        "skills": ["kubernetes", "docker", "terraform", "ansible", "aws", "gcp", "prometheus"],
    },
    {
        "full_name": "Sophia Martinez",
        "email": "sophia.martinez@email.com",
        "headline": "ML Engineer | Computer Vision & NLP",
        "location": "Seattle, WA",
        "summary": "Machine learning engineer focused on computer vision and NLP. Published research papers and deployed models to production.",
        "skills": ["python", "pytorch", "tensorflow", "computer vision", "nlp", "opencv", "aws"],
    },
    {
        "full_name": "Michael Brown",
        "email": "michael.brown@email.com",
        "headline": "Senior Software Engineer | Full Stack",
        "location": "Boston, MA",
        "summary": "Senior software engineer with full stack expertise. Led teams in building scalable SaaS platforms.",
        "skills": ["react", "typescript", "node.js", "python", "postgresql", "docker", "kubernetes"],
    },
]

RESUME_TEXTS = [
    """James Rodriguez
Senior Machine Learning Engineer
San Francisco, CA | james.rodriguez@email.com

SUMMARY
Experienced machine learning engineer with 7 years of experience in NLP and recommendation systems. Led multiple AI projects from research to production.

EXPERIENCE
Senior ML Engineer | TechCorp AI | 2021-Present
- Led development of recommendation system serving 10M+ users
- Implemented NLP models for document classification
- Built MLOps pipeline with Kubeflow and MLflow
- Reduced model inference latency by 40%

ML Engineer | DataDriven Inc | 2018-2021
- Developed computer vision models for product recognition
- Built real-time fraud detection system
- Implemented A/B testing framework for ML models

EDUCATION
PhD in Computer Science | Stanford University | 2018
MS in Computer Science | UC Berkeley | 2015

SKILLS
Python, TensorFlow, PyTorch, NLP, MLOps, Kubernetes, Docker, AWS, GCP""",
    """Emily Zhang
Full Stack Developer
New York, NY | emily.zhang@email.com

SUMMARY
Full stack developer with 5 years of experience building scalable web applications.

EXPERIENCE
Senior Full Stack Developer | FinTech Startup | 2020-Present
- Built React dashboard for financial analytics
- Implemented Node.js microservices architecture
- Optimized database queries improving performance by 60%
- Led team of 4 developers

Full Stack Developer | Healthcare Startup | 2018-2020
- Developed patient management system
- Implemented real-time notifications with WebSockets
- Built HIPAA-compliant data handling

EDUCATION
BS in Computer Science | MIT | 2018

SKILLS
React, TypeScript, Node.js, Python, PostgreSQL, Redis, AWS, Docker""",
    """David Kim
DevOps Engineer
Austin, TX | david.kim@email.com

SUMMARY
DevOps engineer with 6 years of experience in cloud infrastructure and automation.

EXPERIENCE
Senior DevOps Engineer | CloudScale Solutions | 2019-Present
- Designed Kubernetes infrastructure for 50+ microservices
- Implemented CI/CD pipelines with Jenkins and GitLab
- Reduced deployment time by 70% through automation
- Managed cloud spend optimization saving $500K annually

DevOps Engineer | Enterprise Company | 2016-2019
- Managed production infrastructure on AWS
- Implemented monitoring with Prometheus and Grafana
- Built disaster recovery procedures

EDUCATION
BS in Computer Engineering | UT Austin | 2016

SKILLS
Kubernetes, Docker, Terraform, Ansible, AWS, GCP, Prometheus, Grafana, Jenkins""",
]


async def seed_demo_data():
    """Seed demo data for the platform."""
    async with AsyncSessionLocal() as db:
        # Create organizations
        orgs = []
        for org_data in ORGANIZATIONS:
            org = Organization(**org_data)
            db.add(org)
            await db.flush()
            orgs.append(org)

        # Create recruiters
        recruiters = []
        for i, recruiter_data in enumerate(RECRUITERS):
            org = orgs[i // 2]  # Distribute recruiters across orgs
            recruiter = User(
                organization_id=org.id,
                email=recruiter_data["email"],
                full_name=recruiter_data["full_name"],
                hashed_password=hash_password("demo123"),
                roles=recruiter_data["roles"],
                is_active=True,
            )
            db.add(recruiter)
            await db.flush()
            recruiters.append(recruiter)

        # Create job descriptions
        jobs = []
        for i, job_data in enumerate(JOB_DESCRIPTIONS):
            org = orgs[i % len(orgs)]
            job = JobDescription(
                organization_id=org.id,
                created_by_user_id=recruiters[i].id,
                title=job_data["title"],
                description=job_data["description"],
                status="active",
                role_category=job_data["role_category"],
                years_experience_min=job_data["years_experience_min"],
                years_experience_max=job_data["years_experience_max"],
                required_skills=job_data["required_skills"],
                optional_skills=job_data["optional_skills"],
                keywords=job_data["keywords"],
            )
            db.add(job)
            await db.flush()
            jobs.append(job)

        # Create candidates and resumes
        candidates = []
        for i, candidate_data in enumerate(CANDIDATE_TEMPLATES):
            org = orgs[i % len(orgs)]
            candidate = Candidate(
                organization_id=org.id,
                full_name=candidate_data["full_name"],
                email=candidate_data["email"],
                headline=candidate_data["headline"],
                location=candidate_data["location"],
                summary=candidate_data["summary"],
                raw_profile=candidate_data,
            )
            db.add(candidate)
            await db.flush()
            candidates.append(candidate)

            # Create resume
            resume = Resume(
                organization_id=org.id,
                candidate_id=candidate.id,
                uploaded_by_user_id=recruiters[i].id,
                original_filename=f"{candidate_data['full_name'].replace(' ', '_')}_resume.pdf",
                content_type="application/pdf",
                storage_key=f"organizations/{org.id}/resumes/{uuid4()}.pdf",
                checksum_sha256="demo_checksum_" + str(uuid4()),
                status="parsed",
                extracted_text=RESUME_TEXTS[i % len(RESUME_TEXTS)],
                metadata_json={"size_bytes": 15000},
            )
            db.add(resume)
            await db.flush()

            # Create skills
            for skill in candidate_data["skills"]:
                candidate_skill = CandidateSkill(
                    organization_id=org.id,
                    candidate_id=candidate.id,
                    normalized_skill=skill,
                    raw_skill=skill,
                    confidence=0.9,
                )
                db.add(candidate_skill)

        # Create candidate matches
        for candidate in candidates:
            for job in jobs:
                match = CandidateMatch(
                    organization_id=candidate.organization_id,
                    candidate_id=candidate.id,
                    job_description_id=job.id,
                    overall_score=random.uniform(60, 95),
                    semantic_score=random.uniform(0.5, 0.9),
                    skill_match=random.uniform(0.6, 0.95),
                    experience_match=random.uniform(0.5, 0.9),
                    education_match=random.uniform(0.7, 0.95),
                    keyword_score=random.uniform(0.6, 0.9),
                    matched_skills=random.sample(["python", "react", "kubernetes", "docker", "aws"], 3),
                    missing_skills=[],
                    explanation=f"Strong match for {job.title} role",
                    scoring_version="hybrid-v1",
                )
                db.add(match)

        # Create pipeline stages
        stages = [Stage.applied, Stage.screening, Stage.interview, Stage.technical_round, Stage.final_round, Stage.hired]
        for candidate in candidates:
            for job in jobs:
                stage = random.choice(stages)
                pipeline_stage = CandidatePipelineStage(
                    organization_id=candidate.organization_id,
                    candidate_id=candidate.id,
                    job_description_id=job.id,
                    stage=stage,
                    position=random.randint(0, 5),
                )
                db.add(pipeline_stage)

        # Create recruiter notes
        note_templates = [
            "Strong technical skills, great cultural fit",
            "Excellent communication, recommended for next round",
            "Impressive project experience",
            "Good potential, need to assess more",
        ]
        for candidate in candidates[:3]:
            note = RecruiterNote(
                organization_id=candidate.organization_id,
                candidate_id=candidate.id,
                user_id=recruiters[0].id,
                body=random.choice(note_templates),
            )
            db.add(note)

        # Create recruiter activities
        activity_types = ["view_candidate", "shortlist", "interview", "note"]
        for recruiter in recruiters:
            for _ in range(5):
                activity = RecruiterActivity(
                    organization_id=recruiter.organization_id,
                    user_id=recruiter.id,
                    candidate_id=random.choice(candidates).id,
                    job_description_id=random.choice(jobs).id,
                    activity_type=random.choice(activity_types),
                    payload={"source": "demo"},
                )
                db.add(activity)

        # Create ranking feedback
        for candidate in candidates:
            feedback = RankingFeedback(
                organization_id=candidate.organization_id,
                user_id=recruiters[0].id,
                candidate_id=candidate.id,
                job_description_id=jobs[0].id,
                action=random.choice(["shortlist", "interview", "hire"]),
                reward=random.uniform(0.5, 1.0),
                rank_position=random.randint(1, 10),
                model_version="hybrid-v1",
                feature_snapshot={"skills": ["python", "react"]},
            )
            db.add(feedback)

        await db.commit()
        print(f"✅ Seeded {len(orgs)} organizations")
        print(f"✅ Seeded {len(recruiters)} recruiters")
        print(f"✅ Seeded {len(jobs)} job descriptions")
        print(f"✅ Seeded {len(candidates)} candidates")
        print(f"✅ Seeded candidate matches, pipeline stages, notes, activities, and feedback")


if __name__ == "__main__":
    asyncio.run(seed_demo_data())
