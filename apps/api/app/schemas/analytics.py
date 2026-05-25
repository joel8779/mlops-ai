from pydantic import BaseModel


class ExecutiveDashboardResponse(BaseModel):
    hiring_funnel: dict[str, int]
    top_skills: list[dict]
    recruiter_efficiency: dict
    ranking_accuracy: dict
    total_candidates: int = 0
    total_jobs: int = 0
    total_actions: int = 0
    total_resumes: int = 0
