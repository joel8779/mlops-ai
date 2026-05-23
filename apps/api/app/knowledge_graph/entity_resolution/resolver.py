"""Entity resolution for skill, company, and role names."""

from difflib import SequenceMatcher


class EntityResolver:
    def resolve(self, value: str, known_entities: list[str], threshold: float = 0.86) -> tuple[str, float]:
        normalized = self.normalize(value)
        best = (normalized, 0.0)
        for entity in known_entities:
            score = SequenceMatcher(None, normalized, self.normalize(entity)).ratio()
            if score > best[1]:
                best = (entity, score)
        return best if best[1] >= threshold else (normalized, best[1])

    @staticmethod
    def normalize(value: str) -> str:
        return " ".join(value.strip().lower().replace("_", " ").replace("-", " ").split())
