"""Legacy vector store wrapper.

The codebase currently contains two vector store implementations:
- `vector_store/` (legacy v2-style modules expecting a config_path)
- `vector_store.py` (lightweight, direct Chroma PersistentClient wrapper)

For vNext stability, plugins should use this wrapper so we can evolve internals
without breaking the plugin surface.
"""

from __future__ import annotations

import re
import uuid
from typing import Any, Dict, List, Optional

# NOTE: deepsea_nexus has both `vector_store/` (package) and `vector_store.py` (module).
# Import explicitly from the file-module to avoid package name shadowing.
import importlib.util
from pathlib import Path

_mod_path = Path(__file__).with_name("vector_store.py")
_spec = importlib.util.spec_from_file_location("deepsea_nexus._vector_store_file", _mod_path)
assert _spec and _spec.loader
_vector_store_file = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_vector_store_file)  # type: ignore[attr-defined]
VectorStore = _vector_store_file.VectorStore


def _tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"[\w\u4e00-\u9fff]+", (text or "").lower()) if t]


class NullVectorStore:
    """In-memory fallback store used when chromadb is unavailable."""

    is_fallback = True

    def __init__(
        self,
        collection_name: str = "deepsea_nexus",
        persist_path: Optional[str] = None,
        reason: str = "",
    ):
        self.collection_name = collection_name
        self.persist_path = persist_path
        self.reason = reason or "vector backend unavailable"
        self._docs: Dict[str, Dict[str, Any]] = {}

    @property
    def count(self) -> int:
        return len(self._docs)

    def add(
        self,
        documents: List[str],
        embeddings: Optional[List[List[float]]] = None,
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        del embeddings  # Not used in fallback mode.
        ids = ids or [str(uuid.uuid4())[:8] for _ in documents]
        metadatas = metadatas or [{} for _ in documents]
        for idx, content in enumerate(documents):
            doc_id = ids[idx]
            meta = metadatas[idx] if idx < len(metadatas) else {}
            self._docs[doc_id] = {
                "id": doc_id,
                "content": content,
                "metadata": meta or {},
                "tokens": set(_tokenize(content)),
            }
        return ids

    def search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, List[List[Any]]]:
        del where  # Filtering is not implemented in fallback mode.
        q_tokens = set(_tokenize(query))
        scored: List[Dict[str, Any]] = []
        for doc in self._docs.values():
            if not q_tokens:
                score = 0.0
            else:
                overlap = len(q_tokens & doc["tokens"])
                score = overlap / float(max(1, len(q_tokens)))
                if query and query.lower() in (doc["content"] or "").lower():
                    score = min(1.0, score + 0.2)
            if score <= 0:
                continue
            scored.append({"score": score, **doc})
        scored.sort(key=lambda x: x["score"], reverse=True)
        top = scored[: max(0, int(n_results))]
        return {
            "documents": [[d["content"] for d in top]],
            "metadatas": [[d.get("metadata", {}) for d in top]],
            "ids": [[d["id"] for d in top]],
            # Keep chroma-like API shape where smaller distance = better.
            "distances": [[round(1.0 - float(d["score"]), 4) for d in top]],
        }

    def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        limit: int = 100,
    ) -> Dict[str, List[Any]]:
        del where  # Filtering is not implemented in fallback mode.
        docs = list(self._docs.values())
        if ids:
            id_set = set(ids)
            docs = [d for d in docs if d["id"] in id_set]
        docs = docs[: max(0, int(limit))]
        return {
            "documents": [d["content"] for d in docs],
            "metadatas": [d.get("metadata", {}) for d in docs],
            "ids": [d["id"] for d in docs],
        }

    def delete(self, ids: List[str]):
        for doc_id in ids:
            self._docs.pop(doc_id, None)


def create_vector_store(config: Optional[Dict[str, Any]] = None):
    # Accept the full app config dict; `VectorStore` handles defaults.
    persist_path = None
    collection = "deepsea_nexus"

    if isinstance(config, dict):
        nexus_cfg = config.get("nexus", {}) if isinstance(config.get("nexus", {}), dict) else {}
        persist_path = nexus_cfg.get("vector_db_path")
        collection = nexus_cfg.get("collection_name") or collection

    try:
        return VectorStore(collection_name=collection, persist_path=persist_path)
    except Exception as exc:
        return NullVectorStore(
            collection_name=collection,
            persist_path=persist_path,
            reason=str(exc),
        )
