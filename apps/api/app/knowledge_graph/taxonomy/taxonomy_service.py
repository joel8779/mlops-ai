"""Dynamic skill and role taxonomy service."""

from app.knowledge_graph.ontology.role_ontology import RoleOntology
from app.knowledge_graph.ontology.skill_ontology import SkillOntology


class TaxonomyService:
    def __init__(self) -> None:
        self.skills = SkillOntology()
        self.roles = RoleOntology()

    def enrich_candidate_skills(self, skills: list[str]) -> dict[str, list[str]]:
        canonical = [self.skills.canonicalize(skill) for skill in skills]
        expanded = self.skills.expand(canonical)
        role_matches = [role for role, score in self.roles.infer_roles(expanded) if score >= 0.25]
        return {"canonical_skills": sorted(set(canonical)), "expanded_skills": expanded, "role_matches": role_matches}
