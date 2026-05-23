"""Candidate career trajectory and interview success heuristics."""

from typing import Any


class CareerTrajectoryPredictor:
    def predict_next_roles(self, skills: list[str], current_title: str | None = None) -> list[dict[str, float | str]]:
        normalized = {skill.lower() for skill in skills}
        roles = []
        if {"python", "mlops", "kubernetes"} & normalized:
            roles.append({"role": "MLOps Engineer", "confidence": 0.82})
        if {"react", "typescript", "next.js"} & normalized:
            roles.append({"role": "Frontend Platform Engineer", "confidence": 0.78})
        if {"leadership", "architecture", "system design"} & normalized or (current_title and "senior" in current_title.lower()):
            roles.append({"role": "Technical Lead", "confidence": 0.74})
        return roles or [{"role": "Role-adjacent Specialist", "confidence": 0.55}]

    def predict_interview_success(self, context: dict[str, Any]) -> dict[str, Any]:
        matched = len(context.get("matched_skills", []))
        missing = len(context.get("missing_skills", []))
        experience_score = float(context.get("experience_match", 0.65))
        probability = max(0.05, min(0.95, 0.45 + (0.04 * matched) - (0.06 * missing) + (0.2 * experience_score)))
        return {
            "success_probability": round(probability, 3),
            "drivers": ["matched role-critical skills", "experience alignment"][: 1 + int(experience_score > 0.7)],
            "risks": context.get("missing_skills", [])[:5],
        }
