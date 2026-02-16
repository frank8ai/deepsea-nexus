from __future__ import annotations

import os
from typing import Optional, List, Dict

from .graph_store import GraphStore

_GRAPH: Optional[GraphStore] = None
_GRAPH_ENABLED: bool = False


def configure_graph(enabled: bool, base_path: str, db_path: Optional[str] = None) -> None:
    global _GRAPH, _GRAPH_ENABLED
    _GRAPH_ENABLED = bool(enabled)
    if not _GRAPH_ENABLED:
        _GRAPH = None
        return
    if db_path:
        path = db_path
    else:
        path = os.path.join(base_path, "brain", "graph.sqlite3")
    _GRAPH = GraphStore(path)


def graph_add_edge(
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
    if not _GRAPH_ENABLED or _GRAPH is None:
        return None
    return _GRAPH.add_edge(
        subj=subj,
        rel=rel,
        obj=obj,
        weight=weight,
        source=source,
        evidence_text=evidence_text,
        conversation_id=conversation_id,
        round_num=round_num,
        entity_types=entity_types,
    )


def graph_query(
    *,
    subj: Optional[str] = None,
    obj: Optional[str] = None,
    rel: Optional[str] = None,
    limit: int = 20,
) -> List[Dict]:
    if not _GRAPH_ENABLED or _GRAPH is None:
        return []
    return _GRAPH.query_edges(subj=subj, obj=obj, rel=rel, limit=limit)


def graph_related(entity: str, limit: int = 20) -> List[Dict]:
    if not _GRAPH_ENABLED or _GRAPH is None:
        return []
    return _GRAPH.related(entity, limit=limit)
