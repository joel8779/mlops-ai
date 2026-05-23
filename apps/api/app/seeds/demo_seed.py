from uuid import uuid4

INDUSTRIES = ["Fintech", "Healthtech", "SaaS", "Ecommerce", "Cybersecurity"]
SKILLS = ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "NLP", "PyTorch", "Next.js", "TypeScript"]


def build_demo_candidates(count: int = 120) -> list[dict]:
    candidates: list[dict] = []
    for index in range(count):
        skill_slice = [SKILLS[(index + offset) % len(SKILLS)] for offset in range(4)]
        candidates.append(
            {
                "id": str(uuid4()),
                "full_name": f"Demo Candidate {index + 1}",
                "headline": f"{INDUSTRIES[index % len(INDUSTRIES)]} Engineer",
                "location": ["Bengaluru", "Pune", "Remote", "Mumbai", "Hyderabad"][index % 5],
                "years_experience": 2 + index % 12,
                "skills": skill_slice,
                "summary": f"Experienced in {', '.join(skill_slice)} with production delivery ownership.",
            }
        )
    return candidates


def build_demo_jobs() -> list[dict]:
    return [
        {
            "title": "Senior Backend Engineer",
            "description": "Build FastAPI services with PostgreSQL, Redis, Docker, and Kubernetes for fintech workflows.",
        },
        {
            "title": "ML Engineer NLP",
            "description": "Own NLP model training, embedding evaluation, MLflow tracking, and production inference.",
        },
        {
            "title": "Frontend Platform Engineer",
            "description": "Build recruiter-grade Next.js interfaces with TypeScript, Tailwind, and data-heavy UX.",
        },
    ]
