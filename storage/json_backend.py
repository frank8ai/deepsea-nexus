"""JSON session storage backend (minimal implementation).

The SessionManagerPlugin expects `deepsea_nexus.storage.json_backend.JsonSessionStorage`.
This backend persists sessions to a JSON index file under the configured base_path.

Design goals:
- Simple, predictable, low-dependency.
- Async API to match plugin contract.
- Forward-compatible: stores raw dict blobs.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


class JsonSessionStorage:
    def __init__(self, base_path: str, index_file: str = "_sessions_index.json"):
        self.base_path = Path(os.path.expanduser(base_path))
        self.index_path = self.base_path / index_file

    async def initialize(self) -> bool:
        self.base_path.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self.index_path.write_text(json.dumps({"sessions": {}}, ensure_ascii=False, indent=2), encoding="utf-8")
        return True

    def _load(self) -> Dict[str, Any]:
        try:
            return json.loads(self.index_path.read_text(encoding="utf-8"))
        except Exception:
            return {"sessions": {}}

    def _save(self, data: Dict[str, Any]) -> None:
        self.index_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    async def get_all_sessions(self):
        from .base import StorageResult
        data = self._load()
        sessions = data.get("sessions") or {}
        return StorageResult.ok(data=sessions, backend="json")

    async def get_session(self, session_id: str):
        from .base import StorageResult
        data = self._load()
        sess = (data.get("sessions") or {}).get(session_id)
        if sess is None:
            return StorageResult.err("not found", backend="json")
        return StorageResult.ok(data=sess, backend="json")

    async def save_session(self, session: Any):
        from .base import StorageResult
        payload = asdict(session) if hasattr(session, "__dataclass_fields__") else dict(session)
        session_id = payload.get("session_id")
        if not session_id:
            return StorageResult.err("missing session_id", backend="json")

        data = self._load()
        data.setdefault("sessions", {})[session_id] = payload
        self._save(data)
        return StorageResult.ok(backend="json")

    async def delete_session(self, session_id: str):
        from .base import StorageResult
        data = self._load()
        if session_id in (data.get("sessions") or {}):
            del data["sessions"][session_id]
            self._save(data)
            return StorageResult.ok(backend="json")
        return StorageResult.err("not found", backend="json")

    async def close(self) -> bool:
        return True
