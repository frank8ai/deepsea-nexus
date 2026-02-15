from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from collections import OrderedDict

from .models import BrainRecord


class BrainStore(ABC):
    @abstractmethod
    def write(self, record: BrainRecord) -> BrainRecord:
        raise NotImplementedError

    @abstractmethod
    def read_all(self) -> List[BrainRecord]:
        raise NotImplementedError

    @abstractmethod
    def checkpoint(self) -> Dict[str, int]:
        raise NotImplementedError

    @abstractmethod
    def rollback(self, version: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_versions(self) -> List[str]:
        raise NotImplementedError


class JSONLBrainStore(BrainStore):
    def __init__(
        self,
        base_path: str = ".",
        max_snapshots: int = 20,
        dedupe_on_write: bool = False,
        dedupe_recent_max: int = 5000,
    ) -> None:
        self.base_path = Path(base_path)
        self.max_snapshots = max(1, int(max_snapshots))
        self.dedupe_on_write = bool(dedupe_on_write)
        self.dedupe_recent_max = max(0, int(dedupe_recent_max))
        self._recent_hashes: "OrderedDict[str, None]" = OrderedDict()
        self.brain_dir = self.base_path / "brain"
        self.snapshots_dir = self.brain_dir / "snapshots"
        self.records_path = self.brain_dir / "records.jsonl"
        self.snapshot_path = self.brain_dir / "snapshot.jsonl"
        self.changelog_path = self.brain_dir / "changelog.jsonl"
        self.usage_path = self.brain_dir / "usage.jsonl"
        self.brain_dir.mkdir(parents=True, exist_ok=True)
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
        self._warm_recent_hashes()

    def _warm_recent_hashes(self) -> None:
        if not self.dedupe_on_write or self.dedupe_recent_max <= 0:
            return
        if not self.records_path.exists():
            return
        try:
            for item in self._iter_jsonl(self.records_path):
                h = item.get("hash")
                if not isinstance(h, str) or not h:
                    continue
                self._recent_hashes[h] = None
                if len(self._recent_hashes) > self.dedupe_recent_max:
                    self._recent_hashes.popitem(last=False)
        except Exception:
            # Best-effort only; never fail init due to dedupe cache.
            self._recent_hashes.clear()

    def write(self, record: BrainRecord) -> BrainRecord:
        if self.dedupe_on_write and record.hash:
            if record.hash in self._recent_hashes:
                return record
        with self.records_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=True) + "\n")
        if self.dedupe_on_write and record.hash:
            self._recent_hashes[record.hash] = None
            if len(self._recent_hashes) > self.dedupe_recent_max:
                self._recent_hashes.popitem(last=False)
        return record

    def log_usage(self, record_ids: List[str], ts_iso: Optional[str] = None) -> None:
        if not record_ids:
            return
        now_iso = ts_iso or datetime.now(timezone.utc).isoformat()
        with self.usage_path.open("a", encoding="utf-8") as f:
            for rid in record_ids:
                if rid:
                    f.write(json.dumps({"id": rid, "ts": now_iso}, ensure_ascii=True) + "\n")

    def _iter_jsonl(self, path: Path) -> Iterable[dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def read_all(self) -> List[BrainRecord]:
        records = [BrainRecord.from_dict(x) for x in self._iter_jsonl(self.snapshot_path)]
        records.extend(BrainRecord.from_dict(x) for x in self._iter_jsonl(self.records_path))
        return records

    def checkpoint(self) -> Dict[str, int]:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()
        version = now.strftime("%Y%m%dT%H%M%SZ")

        deduped: Dict[str, BrainRecord] = {}
        for rec in self.read_all():
            key = rec.hash
            existing = deduped.get(key)
            if existing is None or rec.updated_at >= existing.updated_at:
                deduped[key] = rec

        # Apply usage-based promotion before snapshotting
        usage_stats = self._apply_usage(deduped, now_iso)

        # Write current snapshot
        with self.snapshot_path.open("w", encoding="utf-8") as f:
            for rec in deduped.values():
                f.write(json.dumps(rec.to_dict(), ensure_ascii=True) + "\n")

        # Also write versioned snapshot for rollback/audit
        versioned_path = self.snapshots_dir / f"{version}.jsonl"
        with versioned_path.open("w", encoding="utf-8") as f:
            for rec in deduped.values():
                f.write(json.dumps(rec.to_dict(), ensure_ascii=True) + "\n")

        appended = sum(1 for _ in self._iter_jsonl(self.records_path))
        if self.records_path.exists():
            self.records_path.unlink()
        self.records_path.touch()
        if self.dedupe_on_write:
            self._recent_hashes.clear()

        deleted_snapshots: List[str] = []
        snapshot_paths = sorted(
            [p for p in self.snapshots_dir.glob("*.jsonl") if p.is_file()],
            key=lambda p: p.name,
            reverse=True,
        )
        for old_path in snapshot_paths[self.max_snapshots :]:
            deleted_snapshots.append(old_path.stem)
            old_path.unlink()

        changelog_event = {
            "ts": now_iso,
            "event": "checkpoint",
            "version": version,
            "snapshot_count": len(deduped),
            "compacted_from": appended,
            "usage_updates": usage_stats,
            "snapshot_path": str(versioned_path),
            "retention_max_snapshots": self.max_snapshots,
            "retention_deleted_versions": deleted_snapshots,
        }
        with self.changelog_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(changelog_event, ensure_ascii=True) + "\n")
            if deleted_snapshots:
                cleanup_event = {
                    "ts": now_iso,
                    "event": "retention_cleanup",
                    "trigger_version": version,
                    "deleted_versions": deleted_snapshots,
                }
                f.write(json.dumps(cleanup_event, ensure_ascii=True) + "\n")

        return {
            "version": version,
            "snapshot_count": len(deduped),
            "compacted_from": appended,
        }

    def _iter_usage(self) -> Iterable[dict]:
        if not self.usage_path.exists():
            return []
        with self.usage_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

    def _apply_usage(self, deduped: Dict[str, BrainRecord], now_iso: str) -> Dict[str, int]:
        """Apply usage stats to records (priority/decay promotion)."""
        usage_by_id: Dict[str, int] = {}
        last_used: Dict[str, str] = {}
        for item in self._iter_usage():
            rid = str(item.get("id", ""))
            if not rid:
                continue
            usage_by_id[rid] = usage_by_id.get(rid, 0) + 1
            last_used[rid] = str(item.get("ts", now_iso))

        if not usage_by_id:
            return {"updated": 0, "skipped": 0}

        # Build lookup by id
        id_map: Dict[str, BrainRecord] = {rec.id: rec for rec in deduped.values() if rec.id}
        updated = 0
        skipped = 0

        for rid, count in usage_by_id.items():
            rec = id_map.get(rid)
            if rec is None:
                skipped += 1
                continue

            meta = dict(rec.metadata or {})
            prev_count = int(meta.get("usage_count", 0) or 0)
            new_count = prev_count + count
            meta["usage_count"] = new_count
            meta["last_used"] = last_used.get(rid, now_iso)

            # Promote priority based on usage
            if new_count >= 10:
                rec.priority = "P0"
            elif new_count >= 3:
                if rec.priority == "P2":
                    rec.priority = "P1"
                elif rec.priority == "P1":
                    # keep P1 unless higher threshold hit
                    rec.priority = "P1"

            # Increase decay floor based on usage
            rec.decay = min(1.0, max(rec.decay, 0.2 + 0.05 * min(new_count, 10)))
            rec.metadata = meta
            rec.updated_at = now_iso
            updated += 1

        # Reset usage log after applying
        if self.usage_path.exists():
            self.usage_path.unlink()
            self.usage_path.touch()

        return {"updated": updated, "skipped": skipped}

    def list_versions(self) -> List[str]:
        versions = set()

        if self.snapshots_dir.exists():
            for path in self.snapshots_dir.glob("*.jsonl"):
                if path.is_file() and path.stem:
                    versions.add(path.stem)

        for event in self._iter_jsonl(self.changelog_path):
            version = event.get("version")
            if isinstance(version, str) and version:
                versions.add(version)

        return sorted(versions, reverse=True)

    def rollback(self, version: str) -> bool:
        """Rollback current snapshot to a previous version (local file rollback)."""
        versioned_path = self.snapshots_dir / f"{version}.jsonl"
        if not versioned_path.exists():
            return False

        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        archived_records_path: Optional[Path] = None
        if self.records_path.exists() and self.records_path.stat().st_size > 0:
            archived_records_path = self.snapshots_dir / f"records_before_rollback_{now.strftime('%Y%m%dT%H%M%SZ')}.jsonl"
            self.records_path.replace(archived_records_path)

        self.records_path.touch()

        # Restore snapshot
        self.snapshot_path.write_text(versioned_path.read_text(encoding="utf-8"), encoding="utf-8")

        changelog_event = {
            "ts": now_iso,
            "event": "rollback",
            "version": version,
            "snapshot_path": str(versioned_path),
            "records_archived": bool(archived_records_path),
        }
        if archived_records_path is not None:
            changelog_event["records_archive_path"] = str(archived_records_path)

        with self.changelog_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(changelog_event, ensure_ascii=True) + "\n")
        return True
