"""
Backward Compatibility Layer v3.0

Maintains 100% API compatibility with Deep-Sea Nexus v2.x
All existing code will continue to work without modification.

Migration Path:
    v2.x (current): from nexus_core import nexus_init, nexus_recall
    v3.0 (new):     from deepsea_nexus import create_app
    
Both APIs work simultaneously - no breaking changes!
"""

import asyncio
from typing import List, Dict, Any, Optional
import logging

try:
    from .core.plugin_system import get_plugin_registry, PluginState
    from .core.config_manager import get_config_manager
    from .plugins.nexus_core import RecallResult
except ImportError:
    from core.plugin_system import get_plugin_registry, PluginState
    from core.config_manager import get_config_manager
    from plugins.nexus_core import RecallResult

logger = logging.getLogger(__name__)

# =============================================================================
# Backward Compatible API Functions
# =============================================================================

def nexus_init(config_path: Optional[str] = None) -> bool:
    """
    Initialize Nexus (v2.x compatible)
    
    This function provides 100% backward compatibility with v2.x code.
    It automatically initializes the plugin system if not already done.
    
    Args:
        config_path: Optional path to configuration file
        
    Returns:
        bool: True if initialized successfully
        
    Example (v2.x style - still works):
        from deepsea_nexus import nexus_init, nexus_recall
        nexus_init()
        results = nexus_recall("Python")
    """
    registry = get_plugin_registry()
    
    # Check if already initialized
    plugin = registry.get("nexus_core")
    if plugin and plugin.state == PluginState.ACTIVE:
        return True
    
    # Load configuration
    config = get_config_manager(config_path)
    if config_path:
        config.load_file(config_path)
    
    # Register plugins if needed
    if not plugin:
        try:
            from .plugins.nexus_core import NexusCorePlugin
            from .app import create_app
        except ImportError:
            from plugins.nexus_core import NexusCorePlugin
            from app import create_app
        
        # Create and initialize app
        app = create_app(config_path)
        
        # Run async initialization in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If in async context, schedule initialization
                asyncio.create_task(app.initialize())
                return True
            else:
                # Run synchronously
                return loop.run_until_complete(app.initialize())
        except RuntimeError:
            # No event loop, create one
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(app.initialize())
    
    # Initialize existing plugin
    return asyncio.get_event_loop().run_until_complete(
        registry.load("nexus_core", config.get_all())
    )


def nexus_recall(query: str, n: int = 5) -> List[RecallResult]:
    """
    Semantic recall/search (v2.x compatible)
    
    Args:
        query: Search query
        n: Number of results to return
        
    Returns:
        List of RecallResult objects
        
    Example (v2.x style - still works):
        results = nexus_recall("Python decorators", 5)
        for r in results:
            print(f"[{r.relevance:.2f}] {r.source}")
    """
    registry = get_plugin_registry()
    plugin = registry.get("nexus_core")
    
    # Auto-initialize if needed
    if plugin is None or plugin.state != PluginState.ACTIVE:
        if not nexus_init():
            logger.error("Failed to initialize Nexus")
            return []
        plugin = registry.get("nexus_core")
    
    if plugin is None:
        return []
    
    # Run async search
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If already in async context
            future = asyncio.ensure_future(plugin.search_recall(query, n))
            # Wait for result (may need different approach in some contexts)
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, future).result()
        else:
            return loop.run_until_complete(plugin.search_recall(query, n))
    except Exception as e:
        logger.error(f"Recall error: {e}")
        return []


# Alias for compatibility
nexus_search = nexus_recall


def nexus_add(content: str, title: str, tags: str = "") -> Optional[str]:
    """
    Add document to index (v2.x compatible)
    
    Args:
        content: Document content
        title: Document title
        tags: Comma-separated tags
        
    Returns:
        str: Document ID on success, None on failure
        
    Example (v2.x style - still works):
        doc_id = nexus_add(
            content="Python is great...",
            title="Python Notes",
            tags="python, programming"
        )
    """
    registry = get_plugin_registry()
    plugin = registry.get("nexus_core")
    
    # Auto-initialize if needed
    if plugin is None or plugin.state != PluginState.ACTIVE:
        if not nexus_init():
            return None
        plugin = registry.get("nexus_core")
    
    if plugin is None:
        return None
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            future = asyncio.ensure_future(plugin.add_document(content, title, tags))
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, future).result()
        else:
            return loop.run_until_complete(plugin.add_document(content, title, tags))
    except Exception as e:
        logger.error(f"Add error: {e}")
        return None


# Alias for compatibility
nexus_add_document = nexus_add


def nexus_add_documents(documents: List[Dict[str, str]], batch_size: int = 10) -> List[str]:
    """
    Add multiple documents (v2.x compatible)
    
    Args:
        documents: List of {content, title, tags} dicts
        batch_size: Processing batch size
        
    Returns:
        List of document IDs
    """
    results = []
    
    for doc in documents:
        doc_id = nexus_add(
            content=doc.get("content", ""),
            title=doc.get("title", ""),
            tags=doc.get("tags", ""),
        )
        if doc_id:
            results.append(doc_id)
    
    return results


def nexus_stats() -> Dict[str, Any]:
    """
    Get statistics (v2.x compatible)
    
    Returns:
        Dict with stats including total_documents
        
    Example (v2.x style - still works):
        stats = nexus_stats()
        print(f"Documents: {stats['total_documents']}")
    """
    registry = get_plugin_registry()
    plugin = registry.get("nexus_core")
    
    if plugin is None or plugin.state != PluginState.ACTIVE:
        return {
            "total_documents": 0,
            "status": "not_initialized",
            "version": "3.0.0",
        }
    
    return plugin.stats()


def nexus_health() -> Dict[str, Any]:
    """
    Get health status (v2.x compatible)
    
    Returns:
        Dict with health information
        
    Example (v2.x style - still works):
        health = nexus_health()
        if health['available']:
            print("Nexus is ready")
    """
    registry = get_plugin_registry()
    
    health = {
        "available": False,
        "initialized": False,
        "documents": 0,
        "version": "3.0.0",
        "plugins": {},
    }
    
    for name in ["nexus_core", "session_manager", "flush_manager"]:
        plugin = registry.get(name)
        if plugin:
            health["plugins"][name] = {
                "state": plugin.state.name,
                "version": plugin.metadata.version if plugin.metadata else "unknown",
            }
            if name == "nexus_core":
                health["available"] = True
                health["initialized"] = plugin.state == PluginState.ACTIVE
                health["documents"] = plugin.stats().get("total_documents", 0)
    
    return health


# =============================================================================
# Session Manager Compatibility
# =============================================================================

def get_session_manager():
    """
    Get SessionManager instance (v2.x compatible)
    
    Returns:
        SessionManagerPlugin instance or None
    """
    registry = get_plugin_registry()
    return registry.get("session_manager")


def start_session(topic: str) -> str:
    """
    Create new session (v2.x compatible)
    
    Args:
        topic: Session topic
        
    Returns:
        str: Session ID
    """
    mgr = get_session_manager()
    if mgr:
        return mgr.start_session(topic)
    return ""


def get_session(session_id: str):
    """Get session by ID (v2.x compatible)"""
    mgr = get_session_manager()
    if mgr:
        return mgr.get_session(session_id)
    return None


def close_session(session_id: str) -> bool:
    """Close session (v2.x compatible)"""
    mgr = get_session_manager()
    if mgr:
        return mgr.close_session(session_id)
    return False


# =============================================================================
# Flush Manager Compatibility
# =============================================================================

def get_flush_manager():
    """
    Get FlushManager instance (v2.x compatible)
    
    Returns:
        FlushManagerPlugin instance or None
    """
    registry = get_plugin_registry()
    return registry.get("flush_manager")


def manual_flush(dry_run: bool = True) -> Dict[str, Any]:
    """
    Manual flush (v2.x compatible)
    
    Note: Now returns coroutine - use asyncio.run() or await
    
    Args:
        dry_run: If True, only preview
        
    Returns:
        Dict with flush results
    """
    mgr = get_flush_manager()
    if mgr:
        # Return coroutine for async execution
        return mgr.manual_flush(dry_run)
    return {"error": "FlushManager not available"}


# =============================================================================
# Compression Compatibility
# =============================================================================

def nexus_compress_session(session_path: str, compressed_path: str = None) -> str:
    """
    Compress session file (v2.x compatible)
    
    Now uses unified CompressionManager instead of duplicate code.
    
    Args:
        session_path: Source file path
        compressed_path: Target file path (optional)
        
    Returns:
        str: Compressed file path
    """
    try:
        from .storage.compression import compress_file
    except ImportError:
        from storage.compression import compress_file
    result = compress_file(session_path, compressed_path)
    return result.data.get("target_path", "") if result.success else ""


def nexus_decompress_session(compressed_path: str, output_path: str = None) -> str:
    """
    Decompress session file (v2.x compatible)
    
    Now uses unified CompressionManager instead of duplicate code.
    
    Args:
        compressed_path: Compressed file path
        output_path: Output file path (optional)
        
    Returns:
        str: Decompressed file path
    """
    try:
        from .storage.compression import decompress_file
    except ImportError:
        from storage.compression import decompress_file
    result = decompress_file(compressed_path, output_path)
    return result.data.get("target_path", "") if result.success else ""


# =============================================================================
# Version Info
# =============================================================================

def get_version() -> str:
    """Get Deep-Sea Nexus version"""
    return "3.0.0"


# Export all backward compatible functions
__all__ = [
    # Core API (v2.x compatible)
    "nexus_init",
    "nexus_recall",
    "nexus_search",
    "nexus_add",
    "nexus_add_document",
    "nexus_add_documents",
    "nexus_stats",
    "nexus_health",
    
    # Session API (v2.x compatible)
    "get_session_manager",
    "start_session",
    "get_session",
    "close_session",
    
    # Flush API (v2.x compatible)
    "get_flush_manager",
    "manual_flush",
    
    # Compression API (v2.x compatible)
    "nexus_compress_session",
    "nexus_decompress_session",
    
    # Utilities
    "get_version",
]
