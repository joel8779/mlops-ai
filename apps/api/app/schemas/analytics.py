from pydantic import BaseModel


class ExecutiveDashboardResponse(BaseModel):
    hiring_funnel: dict[str, int]
    top_skills: list[dict]
    recruiter_efficiency: dict
    ranking_accuracy: dict
