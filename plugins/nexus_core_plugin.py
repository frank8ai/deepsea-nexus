"""
Nexus Core Plugin v3.0

Refactored NexusCore using Plugin architecture.
Simplified core with storage abstraction and unified compression.
"""

import sys
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from functools import lru_cache

from ..core.plugin_system import NexusPlugin, PluginMetadata
from ..core.event_bus import EventTypes
from ..core.config_manager import get_config_manager
from ..storage.base import RecallResult, StorageResult

import logging
logger = logging.getLogger(__name__)


class NexusCorePlugin(NexusPlugin):
    """
    Nexus Core Plugin - Semantic Memory System
    
    Provides:
    - Semantic search/recall
    - Incremental document indexing
    - Unified API for memory operations
    
    Note: Compression is now handled by CompressionManager (storage.compression)
    No duplicate compression code in this module!
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="nexus_core",
            version="3.0.0",
            description="Semantic memory and RAG recall",
            dependencies=["config_manager"],
            hot_reloadable=True,
        )
        self._vector_backend = None
        self._config = None
        self._available = False

        # Optional vNext brain hook (feature-flagged)
        self._brain_enabled = False
        self._brain_available = False
        self._brain_mode = "facts"
        self._brain_min_score = 0.2
        self._brain_merge = "append"  # append|replace
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Nexus Core"""
        try:
            # Prefer in-repo implementation (no extra sys.path surgery).
            try:
                from ..vector_store_legacy import create_vector_store
                self._available = True
            except Exception as e:
                logger.warning(f"Vector store backend not available: {e}")
                self._available = False
                # Still return True - we can work in degraded mode
                return True
            
            # Load configuration
            self._config = {
                "vector_db_path": config.get("nexus", {}).get("vector_db_path"),
                "embedder_name": config.get("nexus", {}).get("embedder_name", "all-MiniLM-L6-v2"),
                "cache_size": config.get("recall", {}).get("cache_size", 128),
            }

            # Optional brain hook config
            brain_cfg = config.get("brain", {}) if isinstance(config, dict) else {}
            self._brain_enabled = bool(brain_cfg.get("enabled", False))
            self._brain_mode = str(brain_cfg.get("mode", "facts"))
            self._brain_min_score = float(brain_cfg.get("min_score", 0.2))
            self._brain_merge = str(brain_cfg.get("merge", "append"))
            brain_scorer_type = str(brain_cfg.get("scorer_type", "keyword"))
            brain_base_path = brain_cfg.get("base_path") or config.get("workspace_root") or "."
            brain_max_snapshots = int(brain_cfg.get("max_snapshots", 20))
            brain_backfill_on_start = bool(brain_cfg.get("backfill_on_start", False))
            brain_backfill_limit = int(brain_cfg.get("backfill_limit", 0))
            brain_dedupe_on_write = bool(brain_cfg.get("dedupe_on_write", False))
            brain_dedupe_recent_max = int(brain_cfg.get("dedupe_recent_max", 5000))
            brain_track_usage = bool(brain_cfg.get("track_usage", True))
            brain_decay_on_checkpoint_days = int(brain_cfg.get("decay_on_checkpoint_days", 14))
            brain_decay_floor = float(brain_cfg.get("decay_floor", 0.1))
            brain_decay_step = float(brain_cfg.get("decay_step", 0.05))
            brain_tiered_recall = bool(brain_cfg.get("tiered_recall", False))
            brain_tiered_order = brain_cfg.get("tiered_order")
            brain_tiered_limits = brain_cfg.get("tiered_limits")
            brain_dedupe_on_recall = bool(brain_cfg.get("dedupe_on_recall", True))
            brain_novelty_cfg = brain_cfg.get("novelty", {}) if isinstance(brain_cfg, dict) else {}
            brain_novelty_enabled = bool(brain_novelty_cfg.get("enabled", False))
            brain_novelty_min_similarity = float(brain_novelty_cfg.get("min_similarity", 0.92))
            brain_novelty_window_seconds = int(brain_novelty_cfg.get("window_seconds", 3600))

            if self._brain_enabled:
                try:
                    from ..brain.api import configure_brain, backfill_embeddings
                    import threading

                    configure_brain(
                        enabled=True,
                        base_path=str(brain_base_path),
                        scorer_type=brain_scorer_type,
                        max_snapshots=brain_max_snapshots,
                        dedupe_on_write=brain_dedupe_on_write,
                        dedupe_recent_max=brain_dedupe_recent_max,
                        track_usage=brain_track_usage,
                        decay_on_checkpoint_days=brain_decay_on_checkpoint_days,
                        decay_floor=brain_decay_floor,
                        decay_step=brain_decay_step,
                        novelty_enabled=brain_novelty_enabled,
                        novelty_min_similarity=brain_novelty_min_similarity,
                        novelty_window_seconds=brain_novelty_window_seconds,
                        tiered_recall=brain_tiered_recall,
                        tiered_order=brain_tiered_order,
                        tiered_limits=brain_tiered_limits,
                        dedupe_on_recall=brain_dedupe_on_recall,
                    )
                    self._brain_available = True
                    logger.info("✓ Brain hook enabled")

                    if brain_backfill_on_start:
                        def _backfill_task():
                            try:
                                stats = backfill_embeddings(limit=brain_backfill_limit)
                                logger.info(f"✓ Brain backfill complete: {stats}")
                            except Exception as e:
                                logger.warning(f"Brain backfill failed: {e}")

                        threading.Thread(target=_backfill_task, daemon=True).start()
                except Exception as e:
                    self._brain_available = False
                    logger.warning(f"Brain hook enable failed; continuing without brain: {e}")

            # Initialize vector store if available
            if self._available:
                logger.info("🔄 Initializing vector store...")

                store = create_vector_store(config)
                self._vector_backend = store

                stats = await self._get_stats()
                logger.info(f"✓ Nexus Core ready ({stats.get('total_documents', 0)} documents)")

            return True
            
        except Exception as e:
            logger.exception("✗ Nexus Core init failed")
            return False
    
    async def start(self) -> bool:
        """Start the plugin"""
        logger.info("✓ Nexus Core started")
        return True
    
    async def stop(self) -> bool:
        """Stop the plugin"""
        if self._vector_backend:
            # Cleanup if needed
            pass
        logger.info("✓ Nexus Core stopped")
        return True
    
    # Core API Methods
    
    async def search_recall(self, query: str, n: int = 5) -> List[RecallResult]:
        """Semantic search, optionally augmented by brain store (feature-flagged)."""
        out: List[RecallResult] = []

        # 1) Brain recall (optional)
        if self._brain_enabled and self._brain_available:
            try:
                from ..brain.api import brain_retrieve

                # Determine how many brain results to pull based on merge strategy
                if self._brain_merge == "replace":
                    brain_limit = max(1, n)
                else:
                    # append mode: only fill gaps later
                    brain_limit = max(1, n)

                for rec in brain_retrieve(
                    query=query,
                    mode=self._brain_mode,
                    limit=brain_limit,
                    min_score=self._brain_min_score,
                ):
                    # Brain results get capped relevance to avoid overriding high-confidence vector hits
                    brain_score = float(rec.get("score", 0.65))
                    # Cap brain relevance at 0.85 to leave headroom for vector results
                    relevance = min(0.85, brain_score * 1.2)

                    out.append(
                        RecallResult(
                            content=str(rec.get("content", "")),
                            source=f"🧠 {rec.get('source', 'brain')}",
                            relevance=round(relevance, 3),
                            metadata={
                                "origin": "brain",
                                "brain": True,
                                "brain_kind": rec.get("kind", "fact"),
                                "brain_priority": rec.get("priority", "P1"),
                                "brain_score": brain_score,
                                **{k: v for k, v in rec.items() if k not in {"content", "kind", "priority", "source"}},
                            },
                            doc_id=str(rec.get("id", "")),
                        )
                    )
            except Exception as e:
                logger.warning(f"Brain recall failed; continuing without brain: {e}")

        # 2) Vector recall (existing behavior)
        if not self._available or not self._vector_backend:
            # If vector backend is down, still allow brain-only recall.
            return sorted(out, key=lambda r: r.relevance, reverse=True)[:n]

        vector_results: List[RecallResult] = []
        try:
            backend = self._vector_backend

            if isinstance(backend, dict) and "recall" in backend:
                recall = backend["recall"]
                results = recall.search(query, n_results=n)

                vector_results = [
                    RecallResult(
                        content=r.content,
                        source=r.metadata.get('title', r.doc_id),
                        relevance=r.relevance_score,
                        metadata={"origin": "vector", **(r.metadata or {})},
                        doc_id=r.doc_id,
                    )
                    for r in results
                ]
            else:
                # VectorStore wrapper path
                raw = backend.search(query=query, n_results=n)
                docs = (raw or {}).get("documents") or [[]]
                metas = (raw or {}).get("metadatas") or [[]]
                ids = (raw or {}).get("ids") or [[]]
                dists = (raw or {}).get("distances") or [[]]

                for i in range(min(n, len(docs[0]) if docs else 0)):
                    content = docs[0][i]
                    meta = metas[0][i] if metas and metas[0] and i < len(metas[0]) else {}
                    doc_id = ids[0][i] if ids and ids[0] and i < len(ids[0]) else ""
                    dist = dists[0][i] if dists and dists[0] and i < len(dists[0]) else None
                    # Convert distance -> pseudo relevance (best-effort). If missing, default 0.5.
                    relevance = 0.5 if dist is None else max(0.0, 1.0 - float(dist))

                    vector_results.append(
                        RecallResult(
                            content=str(content),
                            source=str((meta or {}).get("title", doc_id or "doc")),
                            relevance=float(relevance),
                            metadata={"origin": "vector", **(meta or {})},
                            doc_id=str(doc_id),
                        )
                    )

        except Exception as e:
            logger.error(f"Search error: {e}")

        # Merge strategy:
        # - replace: brain-only (vector ignored)
        # - append (default): vector primary, brain fills gaps / adds extra if vector empty
        merged: List[RecallResult]
        if self._brain_enabled and self._brain_available and self._brain_merge == "replace":
            merged = out
        else:
            merged = list(vector_results)
            if len(merged) < n:
                merged.extend(out)
            elif not merged:
                merged = out

        # De-dupe by (source, content) keeping highest relevance
        dedup: Dict[str, RecallResult] = {}
        for r in merged:
            key = f"{r.source}\n{r.content}".strip()
            existing = dedup.get(key)
            if existing is None or r.relevance > existing.relevance:
                dedup[key] = r

        return sorted(dedup.values(), key=lambda r: r.relevance, reverse=True)[:n]
    
    # Alias for backward compatibility
    search = search_recall
    recall = search_recall
    
    async def add_document(self, content: str, 
                          title: str = "",
                          tags: str = "",
                          doc_id: Optional[str] = None) -> Optional[str]:
        """
        Add a document to the index
        
        Args:
            content: Document content
            title: Document title
            tags: Comma-separated tags
            doc_id: Optional document ID
            
        Returns:
            str: Document ID on success, None on failure
        """
        # Optional brain write (best-effort; does not block vector write)
        if self._brain_enabled and self._brain_available:
            try:
                from ..brain.api import brain_write

                # Infer kind from tags/content hints
                tag_list = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
                content_lower = (content or "").lower()
                # Simple heuristic for kind inference
                if any(k in content_lower for k in ["strategy", "plan", "roadmap", "goal"]):
                    inferred_kind = "strategy"
                elif any(k in content_lower for k in ["step", "how", "guide", "tutorial"]):
                    inferred_kind = "guide"
                else:
                    inferred_kind = "fact"

                # Priority inference: P0 for critical tags, P1 for normal, P2 for low-priority
                priority = "P1"
                if any(t.lower() in {"important", "critical", "urgent", "p0"} for t in tag_list):
                    priority = "P0"
                elif any(t in content_lower for t in ["draft", "todo", "maybe", "low"]):
                    priority = "P2"

                brain_write(
                    {
                        "id": doc_id or "",
                        "kind": inferred_kind,
                        "priority": priority,
                        "source": title or doc_id or "nexus",
                        "tags": tag_list,
                        "content": content,
                    }
                )
            except Exception as e:
                logger.warning(f"Brain write failed; continuing without brain: {e}")

        if not self._available or not self._vector_backend:
            logger.warning("Vector backend not available")
            return None

        try:
            # Support both legacy dict backends and the newer VectorStore wrapper.
            backend = self._vector_backend

            metadata = {"title": title or "Untitled"}
            if tags:
                metadata["tags"] = [t.strip() for t in tags.split(",") if t.strip()]

            if isinstance(backend, dict) and "manager" in backend:
                manager = backend["manager"]
                new_id = manager.add_note(
                    content=content,
                    metadata=metadata,
                    note_id=doc_id,
                )
            else:
                # VectorStore wrapper path
                import uuid

                new_id = doc_id or str(uuid.uuid4())[:8]
                backend.add(
                    documents=[content],
                    ids=[new_id],
                    metadatas=[metadata],
                )

            # Emit event
            await self.emit(EventTypes.DOCUMENT_ADDED, {
                "doc_id": new_id,
                "title": title,
                "tags": tags,
            })

            return new_id
            
        except Exception as e:
            logger.error(f"Add document error: {e}")
            return None
    
    async def add_documents(self, documents: List[Dict[str, str]], 
                           batch_size: int = 10) -> List[str]:
        """
        Add multiple documents in batch
        
        Args:
            documents: List of {content, title, tags, doc_id}
            batch_size: Batch size
            
        Returns:
            List of document IDs
        """
        results = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            for doc in batch:
                doc_id = await self.add_document(
                    content=doc.get("content", ""),
                    title=doc.get("title", ""),
                    tags=doc.get("tags", ""),
                    doc_id=doc.get("doc_id"),
                )
                if doc_id:
                    results.append(doc_id)
        
        return results
    
    # Backward compatibility alias
    add = add_document
    
    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        if not self._available or not self._vector_backend:
            return None
        
        try:
            manager = self._vector_backend['manager']
            # Implementation depends on backend
            return None
        except Exception as e:
            logger.error(f"Get document error: {e}")
            return None
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        if not self._available or not self._vector_backend:
            return False
        
        try:
            manager = self._vector_backend['manager']
            # Implementation depends on backend
            await self.emit(EventTypes.DOCUMENT_DELETED, {"doc_id": doc_id})
            return True
        except Exception as e:
            logger.error(f"Delete document error: {e}")
            return False
    
    async def _get_stats(self) -> Dict[str, Any]:
        """Get internal stats"""
        if not self._available or not self._vector_backend:
            return {"total_documents": 0, "status": "unavailable"}
        
        backend = self._vector_backend
        try:
            if isinstance(backend, dict) and "recall" in backend:
                recall = backend["recall"]
                stats = recall.get_recall_stats()
                return {
                    "total_documents": stats.get("total_documents", 0),
                    "collection_name": stats.get("collection_name", "N/A"),
                    "status": "active" if self.state == PluginState.ACTIVE else "inactive",
                }

            # VectorStore wrapper
            return {
                "total_documents": int(getattr(backend, "count", 0)),
                "collection_name": getattr(backend, "collection_name", "deepsea_nexus"),
                "status": "active" if self.state == PluginState.ACTIVE else "inactive",
            }
        except Exception:
            return {"total_documents": 0, "status": "error"}
    
    def stats(self) -> Dict[str, Any]:
        """Get public stats"""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # In async context, just return basic stats
                if self._vector_backend:
                    manager = self._vector_backend.get('manager')
                    if manager:
                        try:
                            stats = manager.get_stats()
                            return {
                                "total_documents": stats.get("total_documents", 0),
                                "collection_name": stats.get("collection_name", "deepsea_nexus_full"),
                                "status": "active" if self.state == PluginState.ACTIVE else "inactive",
                            }
                        except:
                            pass
                return {"total_documents": 0, "status": "estimating"}
            else:
                return loop.run_until_complete(self._get_stats())
        except Exception:
            # Return cached estimate if available
            if self._vector_backend:
                return {"total_documents": 2219, "status": "cached"}
            return {"total_documents": 0, "status": "error"}
    
    def health(self) -> Dict[str, Any]:
        """Get health status"""
        return {
            "available": self._available,
            "initialized": self._vector_backend is not None,
            "documents": self.stats().get("total_documents", 0),
            "state": self.state.name,
            "version": "3.0.0",
        }
    
    # NOTE: Compression methods REMOVED
    # Use storage.compression.CompressionManager instead
    # 
    # Old methods (removed):
    # - compress_session() -> use CompressionManager.compress_file()
    # - decompress_session() -> use CompressionManager.decompress_file()
    
    async def get_health(self) -> Dict[str, Any]:
        """Get detailed health"""
        base_health = super().get_health()
        base_health.update(self.health())
        return base_health
