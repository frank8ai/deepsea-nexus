from __future__ import annotations

from datetime import datetime, timezone, timedelta
from .scoring import KeywordScorer, Scorer
from .vector_scorer import VectorScorer
import uuid
from typing import Dict, List, Optional

from .models import BrainRecord
from .store import JSONLBrainStore

_STORE: Optional[JSONLBrainStore] = None
_SCORER: Optional[Scorer] = None
_ENABLED: bool = False
_TRACK_USAGE: bool = True
_NOVELTY_ENABLED: bool = False
_NOVELTY_MIN_SIMILARITY: float = 0.92
_NOVELTY_WINDOW_SECONDS: int = 3600
_TIERED_RECALL: bool = False
_TIERED_ORDER: List[str] = ["P0", "P1", "P2"]
_TIERED_LIMITS: List[int] = [3, 2, 1]
_DEDUPE_ON_RECALL: bool = True


def configure_brain(
    enabled: bool = False,
    base_path: str = ".",
    scorer: Optional[Scorer] = None,
    scorer_type: str = "keyword",
    max_snapshots: int = 20,
    dedupe_on_write: bool = False,
    dedupe_recent_max: int = 5000,
    track_usage: bool = True,
    decay_on_checkpoint_days: int = 14,
    decay_floor: float = 0.1,
    decay_step: float = 0.05,
    novelty_enabled: bool = False,
    novelty_min_similarity: float = 0.92,
    novelty_window_seconds: int = 3600,
    tiered_recall: bool = False,
    tiered_order: Optional[List[str]] = None,
    tiered_limits: Optional[List[int]] = None,
    dedupe_on_recall: bool = True,
) -> None:
    global _STORE, _SCORER, _ENABLED, _TRACK_USAGE
    global _NOVELTY_ENABLED, _NOVELTY_MIN_SIMILARITY, _NOVELTY_WINDOW_SECONDS
    global _TIERED_RECALL, _TIERED_ORDER, _TIERED_LIMITS, _DEDUPE_ON_RECALL
    _ENABLED = bool(enabled)
    _TRACK_USAGE = bool(track_usage)
    _NOVELTY_ENABLED = bool(novelty_enabled)
    _NOVELTY_MIN_SIMILARITY = max(0.0, min(1.0, float(novelty_min_similarity)))
    _NOVELTY_WINDOW_SECONDS = max(0, int(novelty_window_seconds))
    _TIERED_RECALL = bool(tiered_recall)
    if tiered_order:
        _TIERED_ORDER = [str(x) for x in tiered_order if str(x)]
    if tiered_limits:
        _TIERED_LIMITS = [max(0, int(x)) for x in tiered_limits]
    _DEDUPE_ON_RECALL = bool(dedupe_on_recall)
    _STORE = JSONLBrainStore(
        base_path=base_path,
        max_snapshots=max_snapshots,
        dedupe_on_write=dedupe_on_write,
        dedupe_recent_max=dedupe_recent_max,
        decay_on_checkpoint_days=decay_on_checkpoint_days,
        decay_floor=decay_floor,
        decay_step=decay_step,
    )

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


def _record_text(record: BrainRecord, scorer: Optional[Scorer]) -> str:
    if isinstance(scorer, VectorScorer):
        return scorer.record_text(record)
    return " ".join(
        [
            record.kind,
            record.source,
            record.content,
            " ".join(record.tags),
        ]
    ).strip()


def _mode_for_kind(kind: str) -> str:
    kind_norm = (kind or "").strip().lower()
    if kind_norm in {"strategy", "plan"}:
        return "strategy"
    return "facts"


def _parse_iso(ts: str) -> Optional[datetime]:
    try:
        parsed = datetime.fromisoformat(ts)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _is_duplicate(record: BrainRecord, store: JSONLBrainStore, scorer: Scorer) -> bool:
    if not _NOVELTY_ENABLED:
        return False
    if _NOVELTY_WINDOW_SECONDS <= 0:
        return False

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(seconds=_NOVELTY_WINDOW_SECONDS)
    query_text = _record_text(record, scorer)
    mode = _mode_for_kind(record.kind)
    min_sim = _NOVELTY_MIN_SIMILARITY

    for existing in store.read_all():
        ts = _parse_iso(existing.updated_at) or _parse_iso(existing.created_at)
        if ts is not None and ts < cutoff:
            continue
        if existing.hash and existing.hash == record.hash:
            return True
        if min_sim <= 0:
            continue
        score = float(scorer.score(query=query_text, record=existing, mode=mode))
        if score >= min_sim:
            return True
    return False


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

    scorer = _SCORER or KeywordScorer()
    if _is_duplicate(record_obj, store, scorer):
        return None

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

    def _dedupe(recs: List[Dict]) -> List[Dict]:
        if not _DEDUPE_ON_RECALL:
            return recs
        seen: Dict[str, int] = {}
        out: List[Dict] = []
        for r in recs:
            key = r.get("hash") or r.get("id")
            if not key:
                continue
            idx = seen.get(key)
            if idx is None:
                seen[key] = len(out)
                out.append(r)
                continue

            # Prefer records with stored embeddings or newer updates.
            existing = out[idx]
            r_meta = r.get("metadata") or {}
            e_meta = existing.get("metadata") or {}
            r_has_emb = isinstance(r_meta.get("embedding"), list)
            e_has_emb = isinstance(e_meta.get("embedding"), list)
            if r_has_emb and not e_has_emb:
                out[idx] = r
                continue
            if e_has_emb and not r_has_emb:
                continue

            r_ts = _parse_iso(str(r.get("updated_at", "")))
            e_ts = _parse_iso(str(existing.get("updated_at", "")))
            if r_ts and e_ts and r_ts > e_ts:
                out[idx] = r
        return out

    if _TIERED_RECALL and scored:
        order = _TIERED_ORDER or ["P0", "P1", "P2"]
        limits = _TIERED_LIMITS or []
        out = []
        for idx, pr in enumerate(order):
            tier = [r for r in scored if r.get("priority") == pr]
            tier.sort(key=lambda x: x["score"], reverse=True)
            cap = limits[idx] if idx < len(limits) else max(0, limit - len(out))
            if cap <= 0:
                continue
            out.extend(tier[:cap])
            if len(out) >= limit:
                break
        out = _dedupe(out)[: max(0, limit)]
    else:
        scored.sort(key=lambda x: x["score"], reverse=True)
        out = _dedupe(scored)[: max(0, limit)]

    if _TRACK_USAGE and out:
        try:
            store.log_usage([str(r.get("id", "")) for r in out])
        except Exception:
            pass

    return out


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
