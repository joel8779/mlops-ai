"""Role ontology and transition mapping."""


class RoleOntology:
    ROLE_SKILLS: dict[str, set[str]] = {
        "backend engineer": {"python", "fastapi", "postgresql", "redis", "system design"},
        "mlops engineer": {"python", "mlflow", "kubernetes", "terraform", "monitoring"},
        "ai engineer": {"python", "rag", "vector search", "prompt engineering", "evaluation"},
        "frontend engineer": {"typescript", "react", "next.js", "accessibility", "design systems"},
    }

    def infer_roles(self, skills: list[str], limit: int = 5) -> list[tuple[str, float]]:
        skill_set = {skill.lower() for skill in skills}
        scored = []
        for role, required in self.ROLE_SKILLS.items():
            score = len(skill_set & required) / len(required)
            if score:
                scored.append((role, round(score, 3)))
        return sorted(scored, key=lambda item: item[1], reverse=True)[:limit]

    def transition_plan(self, from_role: str, to_role: str) -> dict[str, list[str]]:
        current = self.ROLE_SKILLS.get(from_role.lower(), set())
        target = self.ROLE_SKILLS.get(to_role.lower(), set())
        return {
            "transferable_skills": sorted(current & target),
            "skill_gaps": sorted(target - current),
            "deprioritize": sorted(current - target),
        }
