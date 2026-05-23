"""Recruiter intent understanding for autonomous hiring workflows."""

from dataclasses import dataclass, field
from enum import StrEnum
import re
from typing import Any


class HiringIntent(StrEnum):
    SOURCE = "source"
    RANK = "rank"
    STRATEGY = "strategy"
    RISK = "risk"
    INTERVIEW = "interview"
    OUTREACH = "outreach"
    ANALYTICS = "analytics"
    GENERAL = "general"


@dataclass(frozen=True)
class IntentSignal:
    intent: HiringIntent
    confidence: float
    matched_terms: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class RecruiterIntent:
    primary: HiringIntent
    confidence: float
    signals: list[IntentSignal]
    entities: dict[str, Any]


class RecruiterIntentClassifier:
    PATTERNS: dict[HiringIntent, tuple[str, ...]] = {
        HiringIntent.SOURCE: ("source", "find", "pipeline", "talent pool", "shortlist"),
        HiringIntent.RANK: ("rank", "best", "top", "score", "prioritize", "refine"),
        HiringIntent.STRATEGY: ("strategy", "plan", "market", "hiring strategy", "approach"),
        HiringIntent.RISK: ("risk", "concern", "red flag", "attrition", "flight", "gap"),
        HiringIntent.INTERVIEW: ("interview", "screen", "questions", "success"),
        HiringIntent.OUTREACH: ("outreach", "email", "message", "sequence"),
        HiringIntent.ANALYTICS: ("analytics", "funnel", "conversion", "forecast", "quality"),
    }

    def classify(self, query: str, context: dict[str, Any] | None = None) -> RecruiterIntent:
        context = context or {}
        normalized = query.lower()
        signals: list[IntentSignal] = []
        for intent, terms in self.PATTERNS.items():
            matches = [term for term in terms if re.search(rf"\b{re.escape(term)}\b", normalized)]
            if matches:
                confidence = min(0.95, 0.45 + (0.15 * len(matches)))
                signals.append(IntentSignal(intent=intent, confidence=confidence, matched_terms=matches))

        if not signals:
            signals.append(IntentSignal(intent=HiringIntent.GENERAL, confidence=0.55))

        signals = sorted(signals, key=lambda item: item.confidence, reverse=True)
        entities = {
            "job_id": context.get("job_id") or context.get("job_description_id"),
            "candidate_ids": context.get("candidate_ids", []),
            "seniority": self._extract_seniority(normalized),
            "location": context.get("location"),
        }
        return RecruiterIntent(
            primary=signals[0].intent,
            confidence=signals[0].confidence,
            signals=signals,
            entities={key: value for key, value in entities.items() if value},
        )

    @staticmethod
    def _extract_seniority(query: str) -> str | None:
        for seniority in ("intern", "junior", "mid", "senior", "staff", "principal", "lead"):
            if seniority in query:
                return seniority
        return None
