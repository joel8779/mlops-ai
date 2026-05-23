"""Long-term recruiter memory backed by existing conversation tables."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import RecruiterConversation, RecruiterMessage


@dataclass(frozen=True)
class MemoryFact:
    key: str
    value: Any
    confidence: float
    updated_at: datetime


class LongTermRecruiterMemory:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def remember_preference(
        self,
        organization_id: UUID,
        recruiter_id: UUID,
        key: str,
        value: Any,
        confidence: float,
    ) -> None:
        conversation = await self._get_or_create_profile_conversation(organization_id, recruiter_id)
        memory = conversation.memory or {}
        preferences = memory.setdefault("preferences", {})
        preferences[key] = {
            "value": value,
            "confidence": max(0.0, min(1.0, confidence)),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        conversation.memory = memory
        self.db.add(conversation)
        await self.db.commit()

    async def load_preferences(self, organization_id: UUID, recruiter_id: UUID) -> list[MemoryFact]:
        conversation = await self._get_or_create_profile_conversation(organization_id, recruiter_id)
        preferences = (conversation.memory or {}).get("preferences", {})
        facts: list[MemoryFact] = []
        for key, payload in preferences.items():
            facts.append(
                MemoryFact(
                    key=key,
                    value=payload.get("value"),
                    confidence=float(payload.get("confidence", 0.0)),
                    updated_at=datetime.fromisoformat(payload["updated_at"]),
                )
            )
        return sorted(facts, key=lambda item: item.updated_at, reverse=True)

    async def search_messages(self, organization_id: UUID, recruiter_id: UUID, query: str, limit: int = 8) -> list[RecruiterMessage]:
        terms = {term.lower() for term in query.split() if len(term) > 2}
        conversations = await self.db.scalars(
            select(RecruiterConversation.id).where(
                RecruiterConversation.organization_id == organization_id,
                RecruiterConversation.user_id == recruiter_id,
            )
        )
        conversation_ids = list(conversations.all())
        if not conversation_ids:
            return []
        messages = await self.db.scalars(
            select(RecruiterMessage).where(
                RecruiterMessage.organization_id == organization_id,
                RecruiterMessage.conversation_id.in_(conversation_ids),
            )
        )
        scored = []
        for message in messages.all():
            score = sum(1 for term in terms if term in message.content.lower())
            if score:
                scored.append((score, message))
        return [message for _, message in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]

    async def _get_or_create_profile_conversation(self, organization_id: UUID, recruiter_id: UUID) -> RecruiterConversation:
        result = await self.db.scalars(
            select(RecruiterConversation).where(
                RecruiterConversation.organization_id == organization_id,
                RecruiterConversation.user_id == recruiter_id,
                RecruiterConversation.title == "Recruiter Preference Memory",
            )
        )
        conversation = result.first()
        if conversation:
            return conversation
        conversation = RecruiterConversation(
            organization_id=organization_id,
            user_id=recruiter_id,
            title="Recruiter Preference Memory",
            memory={"preferences": {}},
        )
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)
        return conversation
