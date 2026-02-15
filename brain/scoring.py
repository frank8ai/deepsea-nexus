from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Protocol

from .models import BrainRecord


class Scorer(Protocol):
    def score(self, *, query: str, record: BrainRecord, mode: str) -> float: ...


@dataclass
class KeywordScorer:
    """Simple, dependency-free scorer for MVP.

    This is intentionally basic (substring token match) and designed to be swapped
    out later with embedding/vector scorers.
    """

    mode_bonus: float = 0.1

    def score(self, *, query: str, record: BrainRecord, mode: str) -> float:
        q_tokens = [t for t in re.split(r"\W+", query.lower()) if t]
        if not q_tokens:
            return 0.0

        text = " ".join([record.kind, record.source, record.content, " ".join(record.tags)]).lower()
        matches = sum(1 for t in q_tokens if t and t in text)
        base = matches / max(1, len(q_tokens))

        bonus = 0.0
        if mode == "facts" and record.kind.lower() in {"fact", "facts"}:
            bonus = self.mode_bonus
        if mode == "strategy" and record.kind.lower() in {"strategy", "plan"}:
            bonus = self.mode_bonus

        priority_weight = {"P0": 1.2, "P1": 1.0, "P2": 0.8}.get(record.priority, 1.0)
        decay_weight = record.decay if record.decay > 0 else 0.1

        return min(1.0, (base + bonus) * priority_weight * math.sqrt(decay_weight))
