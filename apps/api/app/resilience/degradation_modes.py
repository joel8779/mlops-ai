from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DegradationMode(StrEnum):
    NORMAL = "normal"
    REDUCED_AI = "reduced_ai"
    RETRIEVAL_ONLY = "retrieval_only"
    READ_ONLY = "read_only"


@dataclass
class DegradationState:
    mode: DegradationMode = DegradationMode.NORMAL
    reason: str | None = None

    @property
    def ai_enabled(self) -> bool:
        return self.mode in {DegradationMode.NORMAL, DegradationMode.REDUCED_AI}

    @property
    def writes_enabled(self) -> bool:
        return self.mode != DegradationMode.READ_ONLY


degradation_state = DegradationState()
