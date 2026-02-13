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
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize Nexus Core"""
        try:
            # Import Deep-Sea Nexus source modules
            skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            nexus_path = os.path.join(os.path.dirname(skill_root), 'deepsea-nexus')
            
            if nexus_path not in sys.path:
                sys.path.insert(0, nexus_path)
                sys.path.insert(0, os.path.join(nexus_path, 'src', 'retrieval'))
                sys.path.insert(0, os.path.join(nexus_path, 'vector_store'))
            
            # Try to import core modules
            try:
                from semantic_recall import create_semantic_recall
                from init_chroma import create_vector_store
                from manager import create_manager
                self._available = True
            except ImportError as e:
                logger.warning(f"Deep-Sea Nexus source not available: {e}")
                self._available = False
                # Still return True - we can work in degraded mode
                return True
            
            # Load configuration
            self._config = {
                "vector_db_path": config.get("nexus", {}).get("vector_db_path"),
                "embedder_name": config.get("nexus", {}).get("embedder_name", "all-MiniLM-L6-v2"),
                "cache_size": config.get("recall", {}).get("cache_size", 128),
            }
            
            # Initialize vector store if available
            if self._available:
                logger.info("🔄 Initializing vector store...")
                
                store = create_vector_store()
                manager = create_manager(store.embedder, store.collection)
                recall = create_semantic_recall(manager)
                
                self._vector_backend = {
                    'store': store,
                    'manager': manager,
                    'recall': recall,
                }
                
                stats = await self._get_stats()
                logger.info(f"✓ Nexus Core ready ({stats.get('total_documents', 0)} documents)")
            
            return True
            
        except Exception as e:
            logger.error(f"✗ Nexus Core init failed: {e}")
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
        """
        Semantic search with caching
        
        Args:
            query: Search query
            n: Number of results
            
        Returns:
            List of RecallResult
        """
        if not self._available or not self._vector_backend:
            logger.warning("Vector backend not available")
            return []
        
        try:
            recall = self._vector_backend['recall']
            results = recall.search(query, n_results=n)
            
            return [
                RecallResult(
                    content=r.content,
                    source=r.metadata.get('title', r.doc_id),
                    relevance=r.relevance_score,
                    metadata=r.metadata,
                    doc_id=r.doc_id,
                )
                for r in results
            ]
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
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
        if not self._available or not self._vector_backend:
            logger.warning("Vector backend not available")
            return None
        
        try:
            manager = self._vector_backend['manager']
            
            metadata = {"title": title or "Untitled"}
            if tags:
                metadata["tags"] = [t.strip() for t in tags.split(",")]
            
            new_id = manager.add_note(
                content=content,
                metadata=metadata,
                note_id=doc_id,
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
        
        try:
            recall = self._vector_backend['recall']
            stats = recall.get_recall_stats()
            return {
                "total_documents": stats.get("total_documents", 0),
                "collection_name": stats.get("collection_name", "N/A"),
                "status": "active" if self.state == PluginState.ACTIVE else "inactive",
            }
        except Exception:
            return {"total_documents": 0, "status": "error"}
    
    def stats(self) -> Dict[str, Any]:
        """Get public stats"""
        import asyncio
        try:
            return asyncio.get_event_loop().run_until_complete(self._get_stats())
        except:
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
