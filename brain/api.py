from __future__ import annotations

from datetime import datetime, timezone
from .scoring import KeywordScorer, Scorer
from .vector_scorer import VectorScorer
import uuid
from typing import Dict, List, Optional

from .models import BrainRecord
from .store import JSONLBrainStore

_STORE: Optional[JSONLBrainStore] = None
_SCORER: Optional[Scorer] = None
_ENABLED: bool = False


def configure_brain(
    enabled: bool = False,
    base_path: str = ".",
    scorer: Optional[Scorer] = None,
    scorer_type: str = "keyword",
    max_snapshots: int = 20,
) -> None:
    global _STORE, _SCORER, _ENABLED
    _ENABLED = bool(enabled)
    _STORE = JSONLBrainStore(base_path=base_path, max_snapshots=max_snapshots)

    if scorer is not None:
        _SCORER = scorer
        return

    st = (scorer_type or "keyword").strip().lower()
    if st in {"vector", "st", "sentence-transformers"}:
        _SCORER = VectorScorer(use_sentence_transformers=True)
    elif st in {"hashed-vector", "hash", "bow"}:
        _SCORER = VectorScorer(use_sentence_transformers=False)
    else:
        _SCORER = KeywordScorer()


def is_brain_enabled() -> bool:
    return _ENABLED


def _ensure_store() -> JSONLBrainStore:
    global _STORE
    if _STORE is None:
        _STORE = JSONLBrainStore(base_path=".")
    return _STORE


def _maybe_attach_embedding(record: BrainRecord) -> BrainRecord:
    scorer = _SCORER
    if not isinstance(scorer, VectorScorer):
        return record
    if not scorer.use_sentence_transformers or scorer._st_model is None:
        return record

    meta = dict(record.metadata or {})
    if (
        isinstance(meta.get("embedding"), list)
        and meta.get("embedding_model") == scorer.model_name
        and meta.get("embedding_dim") == scorer.dim
        and meta.get("embedding_kind") == "sentence-transformers"
        and meta.get("embedding_hash") == record.hash
    ):
        record.metadata = meta
        return record

    vec = scorer.embed(scorer.record_text(record))
    meta["embedding"] = vec
    meta["embedding_model"] = scorer.model_name
    meta["embedding_dim"] = scorer.dim
    meta["embedding_kind"] = "sentence-transformers"
    meta["embedding_hash"] = record.hash
    record.metadata = meta
    return record


def brain_write(record: BrainRecord | Dict) -> Optional[BrainRecord]:
    if not _ENABLED:
        return None
    store = _ensure_store()

    if isinstance(record, dict):
        payload = dict(record)
        payload.setdefault("id", str(uuid.uuid4()))
        ts = datetime.now(timezone.utc).isoformat()
        payload.setdefault("created_at", ts)
        payload["updated_at"] = ts
        record_obj = BrainRecord.from_dict(payload)
    else:
        record.updated_at = datetime.now(timezone.utc).isoformat()
        record_obj = record

    # Ensure hash reflects latest content before embedding.
    record_obj.hash = record_obj.compute_hash()
    record_obj = _maybe_attach_embedding(record_obj)

    return store.write(record_obj)


def _score(query: str, rec: BrainRecord, mode: str) -> float:
    scorer = _SCORER or KeywordScorer()
    return float(scorer.score(query=query, record=rec, mode=mode))


def brain_retrieve(
    query: str,
    mode: str = "facts",
    limit: int = 5,
    min_score: float = 0.2,
    priority_filter: Optional[List[str]] = None,
) -> List[Dict]:
    if not _ENABLED:
        return []

    store = _ensure_store()
    items = store.read_all()
    if priority_filter:
        allowed = set(priority_filter)
        items = [i for i in items if i.priority in allowed]

    scored = []
    for rec in items:
        score = _score(query=query, rec=rec, mode=mode)
        if score >= min_score:
            d = rec.to_dict()
            d["score"] = round(score, 4)
            scored.append(d)

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[: max(0, limit)]


def checkpoint() -> Dict[str, int]:
    if not _ENABLED:
        return {"version": "", "snapshot_count": 0, "compacted_from": 0}
    store = _ensure_store()
    return store.checkpoint()


def rollback(version: str) -> bool:
    if not _ENABLED:
        return False
    store = _ensure_store()
    return bool(store.rollback(version))


def list_versions() -> List[str]:
    if not _ENABLED:
        return []
    store = _ensure_store()
    return store.list_versions()


def backfill_embeddings(limit: int = 0) -> Dict[str, int]:
    """Backfill embeddings for existing records (best-effort).

    This only runs when a real sentence-transformers model is available.
    It appends updated records with embeddings to the write-ahead log so that
    checkpoint compaction can dedupe later.
    """
    if not _ENABLED:
        return {"scanned": 0, "updated": 0, "skipped": 0}

    scorer = _SCORER
    if not isinstance(scorer, VectorScorer):
        return {"scanned": 0, "updated": 0, "skipped": 0}
    if not scorer.use_sentence_transformers or scorer._st_model is None:
        return {"scanned": 0, "updated": 0, "skipped": 0}

    store = _ensure_store()
    now = datetime.now(timezone.utc).isoformat()

    scanned = 0
    updated = 0
    skipped = 0

    for rec in store.read_all():
        scanned += 1
        meta = rec.metadata or {}
        if (
            isinstance(meta.get("embedding"), list)
            and meta.get("embedding_model") == scorer.model_name
            and meta.get("embedding_dim") == scorer.dim
            and meta.get("embedding_kind") == "sentence-transformers"
            and meta.get("embedding_hash") == rec.hash
        ):
            skipped += 1
        else:
            rec.updated_at = now
            rec = _maybe_attach_embedding(rec)
            store.write(rec)
            updated += 1

        if limit and scanned >= limit:
            break

    return {"scanned": scanned, "updated": updated, "skipped": skipped}
