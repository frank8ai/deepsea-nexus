from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Iterable, List, Optional, Dict


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class GraphStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE,
                    type TEXT,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS edges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subj TEXT,
                    rel TEXT,
                    obj TEXT,
                    weight REAL,
                    source TEXT,
                    conversation_id TEXT,
                    round_num INTEGER,
                    created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    edge_id INTEGER,
                    text TEXT,
                    source TEXT,
                    created_at TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_edges_subj ON edges(subj);
                CREATE INDEX IF NOT EXISTS idx_edges_obj ON edges(obj);
                CREATE INDEX IF NOT EXISTS idx_edges_rel ON edges(rel);
                """
            )

    def _ensure_entity(self, name: str, entity_type: Optional[str] = None) -> None:
        if not name:
            return
        with self._connect() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO entities(name, type, created_at) VALUES (?, ?, ?)",
                (name, entity_type or "unknown", _utcnow()),
            )

    def add_edge(
        self,
        subj: str,
        rel: str,
        obj: str,
        *,
        weight: float = 1.0,
        source: str = "",
        evidence_text: str = "",
        conversation_id: str = "",
        round_num: int = 0,
        entity_types: Optional[Dict[str, str]] = None,
    ) -> Optional[int]:
        if not (subj and rel and obj):
            return None
        entity_types = entity_types or {}
        self._ensure_entity(subj, entity_types.get("subj"))
        self._ensure_entity(obj, entity_types.get("obj"))

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO edges(subj, rel, obj, weight, source, conversation_id, round_num, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (subj, rel, obj, float(weight), source, conversation_id, int(round_num), _utcnow()),
            )
            edge_id = cur.lastrowid
            if evidence_text:
                conn.execute(
                    "INSERT INTO evidence(edge_id, text, source, created_at) VALUES (?, ?, ?, ?)",
                    (edge_id, evidence_text, source, _utcnow()),
                )
        return edge_id

    def query_edges(
        self,
        *,
        subj: Optional[str] = None,
        obj: Optional[str] = None,
        rel: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict]:
        clauses: List[str] = []
        params: List[object] = []
        if subj:
            clauses.append("subj = ?")
            params.append(subj)
        if obj:
            clauses.append("obj = ?")
            params.append(obj)
        if rel:
            clauses.append("rel = ?")
            params.append(rel)
        where = " AND ".join(clauses) if clauses else "1=1"
        sql = f"SELECT id, subj, rel, obj, weight, source, conversation_id, round_num, created_at FROM edges WHERE {where} ORDER BY id DESC LIMIT ?"
        params.append(int(limit))
        with self._connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        out = []
        for r in rows:
            out.append(
                {
                    "id": r[0],
                    "subj": r[1],
                    "rel": r[2],
                    "obj": r[3],
                    "weight": r[4],
                    "source": r[5],
                    "conversation_id": r[6],
                    "round_num": r[7],
                    "created_at": r[8],
                }
            )
        return out

    def related(self, entity: str, limit: int = 20) -> List[Dict]:
        if not entity:
            return []
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, subj, rel, obj, weight, source, conversation_id, round_num, created_at
                FROM edges
                WHERE subj = ? OR obj = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (entity, entity, int(limit)),
            ).fetchall()
        out = []
        for r in rows:
            out.append(
                {
                    "id": r[0],
                    "subj": r[1],
                    "rel": r[2],
                    "obj": r[3],
                    "weight": r[4],
                    "source": r[5],
                    "conversation_id": r[6],
                    "round_num": r[7],
                    "created_at": r[8],
                }
            )
        return out
