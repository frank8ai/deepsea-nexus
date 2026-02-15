from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
from typing import Any, Dict, List, Optional

PRIORITIES = {"P0", "P1", "P2"}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_tags(tags: Optional[List[str]]) -> List[str]:
    if not tags:
        return []
    return sorted({t.strip().lower() for t in tags if isinstance(t, str) and t.strip()})


@dataclass
class BrainRecord:
    id: str
    kind: str
    priority: str = "P1"
    source: str = "unknown"
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    tags: List[str] = field(default_factory=list)
    ttl_seconds: Optional[int] = None
    decay: float = 1.0
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""

    def __post_init__(self) -> None:
        if self.priority not in PRIORITIES:
            raise ValueError("priority must be one of P0/P1/P2")
        self.tags = _normalize_tags(self.tags)
        if not self.hash:
            self.hash = self.compute_hash()

    def compute_hash(self) -> str:
        payload = "|".join(
            [
                self.kind.strip().lower(),
                self.priority,
                self.source.strip().lower(),
                " ".join(self.tags),
                (self.content or "").strip(),
            ]
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "kind": self.kind,
            "priority": self.priority,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "tags": list(self.tags),
            "ttl_seconds": self.ttl_seconds,
            "decay": self.decay,
            "content": self.content,
            "metadata": dict(self.metadata),
            "hash": self.hash,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BrainRecord":
        return cls(
            id=str(data.get("id", "")),
            kind=str(data.get("kind", "fact")),
            priority=str(data.get("priority", "P1")),
            source=str(data.get("source", "unknown")),
            created_at=str(data.get("created_at", utc_now_iso())),
            updated_at=str(data.get("updated_at", utc_now_iso())),
            tags=list(data.get("tags", [])),
            ttl_seconds=data.get("ttl_seconds"),
            decay=float(data.get("decay", 1.0)),
            content=str(data.get("content", "")),
            metadata=dict(data.get("metadata", {})),
            hash=str(data.get("hash", "")),
        )
