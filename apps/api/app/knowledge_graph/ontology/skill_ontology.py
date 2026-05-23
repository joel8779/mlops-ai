"""Skill ontology with synonyms, hierarchy, and related-skill expansion."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class SkillConcept:
    canonical: str
    synonyms: set[str] = field(default_factory=set)
    parents: set[str] = field(default_factory=set)
    related: set[str] = field(default_factory=set)


class SkillOntology:
    def __init__(self, concepts: list[SkillConcept] | None = None) -> None:
        defaults = [
            SkillConcept("python", {"py"}, {"programming"}, {"fastapi", "pandas", "mlops"}),
            SkillConcept("typescript", {"ts"}, {"programming"}, {"react", "next.js", "node.js"}),
            SkillConcept("kubernetes", {"k8s"}, {"platform engineering"}, {"docker", "helm", "terraform"}),
            SkillConcept("mlops", {"machine learning operations"}, {"machine learning"}, {"mlflow", "prefect", "kubernetes"}),
            SkillConcept("rag", {"retrieval augmented generation"}, {"generative ai"}, {"vector search", "reranking"}),
        ]
        self._concepts = {concept.canonical: concept for concept in (concepts or defaults)}
        self._alias_index = {
            alias.lower(): concept.canonical
            for concept in self._concepts.values()
            for alias in {concept.canonical, *concept.synonyms}
        }

    def canonicalize(self, skill: str) -> str:
        return self._alias_index.get(skill.strip().lower(), skill.strip().lower())

    def expand(self, skills: list[str], include_related: bool = True) -> list[str]:
        expanded: set[str] = set()
        for skill in skills:
            canonical = self.canonicalize(skill)
            expanded.add(canonical)
            concept = self._concepts.get(canonical)
            if concept:
                expanded.update(concept.parents)
                if include_related:
                    expanded.update(concept.related)
        return sorted(expanded)

    def emerging_skills(self, current_counts: dict[str, int], previous_counts: dict[str, int], min_growth: float = 0.5) -> list[tuple[str, float]]:
        growth = []
        for skill, current in current_counts.items():
            previous = previous_counts.get(skill, 0)
            if previous == 0 and current >= 3:
                growth.append((skill, 1.0))
            elif previous:
                rate = (current - previous) / previous
                if rate >= min_growth:
                    growth.append((skill, round(rate, 3)))
        return sorted(growth, key=lambda item: item[1], reverse=True)
