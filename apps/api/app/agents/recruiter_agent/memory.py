"""Agent Memory System - Persistent memory for AI recruiter agent."""

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis import get_redis_client


@dataclass
class MemoryEntry:
    """Single memory entry."""

    role: str  # "user", "assistant", "system", "tool"
    content: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    session_id: Optional[UUID] = None


class AgentMemory:
    """Persistent memory system for agent conversations and context."""

    def __init__(
        self,
        organization_id: UUID,
        user_id: UUID,
        session_id: Optional[UUID] = None,
        max_entries: int = 100,
    ) -> None:
        """Initialize agent memory.

        Args:
            organization_id: Organization ID
            user_id: User ID
            session_id: Optional session ID
            max_entries: Maximum number of entries to keep in memory
        """
        self.organization_id = organization_id
        self.user_id = user_id
        self.session_id = session_id
        self.max_entries = max_entries
        self._entries: list[MemoryEntry] = []
        self._redis_key = f"agent_memory:{organization_id}:{user_id}"

    async def add_message(
        self,
        role: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:
        """Add a message to memory.

        Args:
            role: Message role (user, assistant, system, tool)
            content: Message content
            metadata: Optional metadata
        """
        entry = MemoryEntry(
            role=role,
            content=content,
            metadata=metadata or {},
            session_id=self.session_id,
        )
        self._entries.append(entry)

        # Trim if exceeding max
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

        # Persist to Redis
        await self._persist_to_redis()

    async def get_recent_entries(self, limit: int = 10) -> list[MemoryEntry]:
        """Get recent memory entries.

        Args:
            limit: Number of entries to return

        Returns:
            List of recent MemoryEntry objects
        """
        return self._entries[-limit:]

    async def get_entries_by_role(self, role: str, limit: int = 10) -> list[MemoryEntry]:
        """Get entries by role.

        Args:
            role: Role to filter by
            limit: Maximum number of entries

        Returns:
            List of MemoryEntry objects with matching role
        """
        filtered = [e for e in self._entries if e.role == role]
        return filtered[-limit:]

    async def get_context_window(self, token_limit: int = 4000) -> str:
        """Get context window as formatted string.

        Args:
            token_limit: Approximate token limit

        Returns:
            Formatted context string
        """
        # Simple approximation: 1 token ≈ 4 characters
        char_limit = token_limit * 4

        context_parts = []
        total_chars = 0

        # Add entries from oldest to newest until limit
        for entry in reversed(self._entries):
            entry_text = f"{entry.role}: {entry.content}\n"
            if total_chars + len(entry_text) > char_limit:
                break
            context_parts.insert(0, entry_text)
            total_chars += len(entry_text)

        return "\n".join(context_parts)

    async def search_memory(self, query: str, limit: int = 5) -> list[MemoryEntry]:
        """Search memory for relevant entries.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of relevant MemoryEntry objects
        """
        query_lower = query.lower()
        scored = []

        for entry in self._entries:
            score = 0
            content_lower = entry.content.lower()

            # Exact match
            if query_lower in content_lower:
                score += 10

            # Word matches
            query_words = query_lower.split()
            for word in query_words:
                if word in content_lower:
                    score += 2

            # Recent entries get bonus
            time_diff = (datetime.now(timezone.utc) - entry.timestamp).total_seconds()
            if time_diff < 3600:  # Within 1 hour
                score += 1

            if score > 0:
                scored.append((score, entry))

        # Sort by score and return top results
        scored.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in scored[:limit]]

    async def get_summary(self) -> dict[str, Any]:
        """Get memory summary.

        Returns:
            Dictionary with memory statistics
        """
        role_counts = {}
        for entry in self._entries:
            role_counts[entry.role] = role_counts.get(entry.role, 0) + 1

        return {
            "total_entries": len(self._entries),
            "role_counts": role_counts,
            "session_id": str(self.session_id) if self.session_id else None,
            "oldest_entry": self._entries[0].timestamp if self._entries else None,
            "newest_entry": self._entries[-1].timestamp if self._entries else None,
        }

    async def clear(self) -> None:
        """Clear all memory entries."""
        self._entries.clear()
        await self._persist_to_redis()

    async def load_from_redis(self) -> None:
        """Load memory from Redis."""
        try:
            redis = get_redis_client()
            data = await redis.get(self._redis_key)
            if data:
                entries_data = json.loads(data)
                self._entries = [
                    MemoryEntry(
                        role=e["role"],
                        content=e["content"],
                        timestamp=datetime.fromisoformat(e["timestamp"]),
                        metadata=e.get("metadata", {}),
                        session_id=UUID(e["session_id"]) if e.get("session_id") else None,
                    )
                    for e in entries_data
                ]
        except Exception:
            # If Redis is unavailable, start with empty memory
            self._entries = []

    async def _persist_to_redis(self) -> None:
        """Persist memory to Redis."""
        try:
            redis = get_redis_client()
            data = [
                {
                    "role": e.role,
                    "content": e.content,
                    "timestamp": e.timestamp.isoformat(),
                    "metadata": e.metadata,
                    "session_id": str(e.session_id) if e.session_id else None,
                }
                for e in self._entries
            ]
            await redis.set(self._redis_key, json.dumps(data), ex=86400)  # 24 hour TTL
        except Exception:
            # If Redis is unavailable, continue without persistence
            pass
