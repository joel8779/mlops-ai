from pydantic import BaseModel


class ExecutiveDashboardResponse(BaseModel):
    hiring_funnel: dict[str, int]
    top_skills: list[dict]
    recruiter_efficiency: dict
    ranking_accuracy: dict
    candidates_per_job: list[dict] = []
    ats_score_distribution: dict[str, int] = {}
    shortlist_counts: dict[str, int] = {}
    resume_processing_counts: dict[str, int] = {}
    semantic_match_averages: list[dict] = []
    pipeline_stage_counts: dict[str, int] = {}
    total_candidates: int = 0
    total_jobs: int = 0
    total_actions: int = 0
    total_resumes: int = 0
