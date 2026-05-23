import re
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import ATSScore, Resume
from app.schemas.ats import ATSScoreRead


class ATSScoringService:
    sections = ["experience", "education", "skills", "projects"]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def score_resume(self, resume: Resume) -> ATSScoreRead:
        text = resume.extracted_text or ""
        lower = text.lower()
        issues: list[str] = []
        recommendations: list[str] = []

        section_score = sum(1 for section in self.sections if section in lower) / len(self.sections) * 30
        keyword_score = min(25, len(set(re.findall(r"[A-Za-z][A-Za-z0-9\+#\.-]{2,}", text))) / 12)
        readability_score = 20 if 250 <= len(text.split()) <= 2500 else 10
        contact_score = 15 if re.search(r"[\w\.-]+@[\w\.-]+", text) else 5
        formatting_score = 10 if "\t" not in text and len(re.findall(r"[^\x00-\x7F]", text)) < 20 else 6

        for section in self.sections:
            if section not in lower:
                issues.append(f"Missing or unclear {section} section")
                recommendations.append(f"Add a clearly labeled {section.title()} section")
        if contact_score < 15:
            issues.append("No email address detected")
            recommendations.append("Include a professional email address near the top")
        if readability_score < 20:
            issues.append("Resume length may hurt readability")
            recommendations.append("Keep resume content concise and role-focused")

        score = round(section_score + keyword_score + readability_score + contact_score + formatting_score, 2)
        record = ATSScore(
            organization_id=resume.organization_id,
            resume_id=resume.id,
            ats_score=score,
            issues=issues,
            recommendations=recommendations,
        )
        self.db.add(record)
        await self.db.commit()
        return ATSScoreRead(resume_id=resume.id, ats_score=score, issues=issues, recommendations=recommendations)
