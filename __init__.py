"""
Deep-Sea Nexus v3.0
AI Agent Long-term Memory System - Hot-Pluggable Architecture

New API (v3.0 - Recommended):
    from deepsea_nexus import create_app
    
    app = create_app()
    await app.initialize()
    await app.start()
    
    # Use plugins
    results = await app.plugins["nexus_core"].search_recall("query")

Backward Compatible API (v2.x - Still Works):
    from deepsea_nexus import nexus_init, nexus_recall
    
    nexus_init()
    results = nexus_recall("query")

Features:
- Hot-pluggable architecture
- Event-driven communication
- Unified compression (no code duplication)
- Swappable storage backends
- 100% backward compatible
"""

__version__ = "3.0.0"
__author__ = "Deep-Sea Nexus Team"

# =============================================================================
# New API (v3.0) - Recommended
# =============================================================================

from .app import (
    create_app,
    NexusApplication,
    get_app,
    set_app,
)

from .core.plugin_system import (
    NexusPlugin,
    PluginMetadata,
    PluginRegistry,
    PluginState,
    get_plugin_registry,
)

from .core.event_bus import (
    EventBus,
    EventTypes,
    EventPriority,
    Event,
    get_event_bus,
)

from .core.config_manager import (
    ConfigManager,
    ConfigChange,
    get_config_manager,
)

from .storage.compression import (
    CompressionManager,
    GzipBackend,
    ZstdBackend,
    Lz4Backend,
    compress_file,
    decompress_file,
    read_compressed,
)

from .storage.base import (
    RecallResult,
    StorageResult,
    VectorStorageBackend,
    SessionStorageBackend,
    CompressionBackend,
)

# =============================================================================
# Backward Compatible API (v2.x)
# =============================================================================

from .compat import (
    # Core
    nexus_init,
    nexus_recall,
    nexus_search,
    nexus_add,
    nexus_add_document,
    nexus_add_documents,
    nexus_stats,
    nexus_health,
    
    # Session
    get_session_manager,
    start_session,
    get_session,
    close_session,
    
    # Flush
    get_flush_manager,
    manual_flush,
    
    # Compression
    nexus_compress_session,
    nexus_decompress_session,
    
    # Utils
    get_version,
)

# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Version
    "__version__",
    
    # New API (v3.0)
    "create_app",
    "NexusApplication",
    "get_app",
    "set_app",
    
    # Core Components
    "NexusPlugin",
    "PluginMetadata",
    "PluginRegistry",
    "PluginState",
    "get_plugin_registry",
    
    # Event Bus
    "EventBus",
    "EventTypes",
    "EventPriority",
    "Event",
    "get_event_bus",
    
    # Config
    "ConfigManager",
    "ConfigChange",
    "get_config_manager",
    
    # Storage
    "RecallResult",
    "StorageResult",
    "VectorStorageBackend",
    "SessionStorageBackend",
    "CompressionBackend",
    
    # Compression
    "CompressionManager",
    "GzipBackend",
    "ZstdBackend",
    "Lz4Backend",
    "compress_file",
    "decompress_file",
    "read_compressed",
    
    # Backward Compatible API (v2.x)
    "nexus_init",
    "nexus_recall",
    "nexus_search",
    "nexus_add",
    "nexus_add_document",
    "nexus_add_documents",
    "nexus_stats",
    "nexus_health",
    "get_session_manager",
    "start_session",
    "get_session",
    "close_session",
    "get_flush_manager",
    "manual_flush",
    "nexus_compress_session",
    "nexus_decompress_session",
    "get_version",
]

# =============================================================================
# Module Info
# =============================================================================

def info():
    """Print module information"""
    print(f"Deep-Sea Nexus v{__version__}")
    print("Hot-Pluggable Architecture")
    print("\nQuick Start:")
    print("  from deepsea_nexus import create_app")
    print("  app = create_app()")
    print("  await app.initialize()")
    print("  await app.start()")
