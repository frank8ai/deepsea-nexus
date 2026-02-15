"""
Deep-Sea Nexus v3.0 Application

Main entry point for the hot-pluggable architecture.
Provides unified lifecycle management and backward compatibility.
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from pathlib import Path

from .core.config_manager import get_config_manager, ConfigManager
from .core.event_bus import get_event_bus, EventBus
from .core.plugin_system import get_plugin_registry, PluginRegistry, PluginState

# Import plugins
from .plugins.config_manager_plugin import ConfigManagerPlugin
from .plugins.nexus_core_plugin import NexusCorePlugin
from .plugins.session_manager import SessionManagerPlugin
from .plugins.flush_manager import FlushManagerPlugin
from .plugins.smart_context import SmartContextPlugin

logger = logging.getLogger(__name__)


class NexusApplication:
    """
    Deep-Sea Nexus Application
    
    Main application container managing all plugins and services.
    Provides hot-reload and graceful shutdown capabilities.
    
    Usage:
        # New API (v3.0)
        app = create_app()
        await app.initialize()
        await app.start()
        
        # Use plugins
        results = await app.plugins["nexus_core"].search_recall("query")
        
        # Hot reload
        await app.reload()
        
        # Shutdown
        await app.stop()
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize application
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config_path = config_path
        self.config: ConfigManager = get_config_manager(config_path)
        self.event_bus: EventBus = get_event_bus()
        self.registry: PluginRegistry = get_plugin_registry()
        
        # Set up event bus in registry
        self.registry.set_event_bus(self.event_bus)
        
        # Plugin instances
        self._plugins_registered = False
        self._initialized = False
        self._started = False
    
    @property
    def plugins(self) -> Dict[str, Any]:
        """Access loaded plugins by name"""
        return self.registry._plugins
    
    async def initialize(self) -> bool:
        """
        Initialize the application and all plugins
        
        Returns:
            bool: True if initialization successful
        """
        if self._initialized:
            logger.warning("Application already initialized")
            return True
        
        try:
            logger.info("🚀 Initializing Deep-Sea Nexus v3.0...")
            
            # 1. Load configuration
            if self.config_path:
                success = self.config.load_file(self.config_path)
                if not success:
                    logger.warning(f"Failed to load config from {self.config_path}, using defaults")
            
            # Validate config
            errors = self.config.validate()
            if errors:
                for error in errors:
                    logger.warning(f"Config validation: {error}")
            
            # 2. Register plugins
            await self._register_plugins()
            
            # 3. Initialize plugins in dependency order
            config_dict = self.config.get_all()
            success = await self._initialize_plugins(config_dict)
            
            if success:
                self._initialized = True
                logger.info("✓ Deep-Sea Nexus initialized")
                return True
            else:
                logger.error("✗ Initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"✗ Initialization error: {e}")
            return False
    
    async def _register_plugins(self):
        """Register all plugins"""
        if self._plugins_registered:
            return
        
        nexus_core = NexusCorePlugin()
        session_manager = SessionManagerPlugin()
        smart_context = SmartContextPlugin()
        flush_manager = FlushManagerPlugin()

        config_manager = ConfigManagerPlugin()

        plugins = [
            (config_manager, config_manager.metadata),
            (nexus_core, nexus_core.metadata),
            (session_manager, session_manager.metadata),
            (smart_context, smart_context.metadata),  # 智能上下文
            (flush_manager, flush_manager.metadata),
        ]
        
        for plugin, metadata in plugins:
            success = self.registry.register(plugin, metadata)
            if not success:
                logger.error(f"Failed to register plugin: {metadata.name}")
        
        self._plugins_registered = True
        logger.info(f"✓ Registered {len(plugins)} plugins")
    
    async def _initialize_plugins(self, config: Dict[str, Any]) -> bool:
        """Initialize all plugins in dependency order"""
        # Get auto-load list from config
        auto_load = config.get("plugins", {}).get("auto_load", [
            "config_manager",
            "nexus_core",
            "session_manager",
            "smart_context",  # 智能上下文（核心功能）
            "flush_manager",
        ])
        
        # Load in order
        for plugin_name in auto_load:
            plugin = self.registry.get(plugin_name)
            if not plugin:
                logger.warning(f"Plugin not found: {plugin_name}")
                continue
            
            success = await self.registry.load(plugin_name, config)
            if not success:
                logger.error(f"Failed to load plugin: {plugin_name}")
                # Continue loading other plugins
        
        # Check if critical plugins loaded
        critical = ["nexus_core", "session_manager"]
        for name in critical:
            state = self.registry.get_state(name)
            if state != PluginState.ACTIVE:
                logger.error(f"Critical plugin not active: {name}")
                return False
        
        return True
    
    async def start(self) -> bool:
        """
        Start all initialized plugins
        
        Returns:
            bool: True if all plugins started
        """
        if not self._initialized:
            logger.error("Application not initialized")
            return False
        
        if self._started:
            logger.warning("Application already started")
            return True
        
        try:
            logger.info("▶️ Starting plugins...")
            
            for name in self.registry.list_active():
                plugin = self.registry.get(name)
                if plugin and plugin.state == PluginState.ACTIVE:
                    success = await plugin.start()
                    if not success:
                        logger.error(f"Failed to start plugin: {name}")
            
            self._started = True
            logger.info("✓ Deep-Sea Nexus started")
            return True
            
        except Exception as e:
            logger.error(f"✗ Start error: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop all plugins gracefully
        
        Returns:
            bool: True if all plugins stopped
        """
        if not self._started:
            return True
        
        try:
            logger.info("⏹️ Stopping plugins...")
            
            # Stop in reverse order
            active = list(reversed(self.registry.list_active()))
            for name in active:
                success = await self.registry.unload(name)
                if not success:
                    logger.warning(f"Failed to stop plugin: {name}")
            
            self._started = False
            logger.info("✓ Deep-Sea Nexus stopped")
            return True
            
        except Exception as e:
            logger.error(f"✗ Stop error: {e}")
            return False
    
    async def reload(self) -> bool:
        """
        Hot-reload configuration and plugins
        
        Returns:
            bool: True if reloaded successfully
        """
        try:
            logger.info("🔄 Reloading...")
            
            # Stop
            await self.stop()
            
            # Reload config
            if self.config_path:
                self.config.load_file(self.config_path)
            
            # Reinitialize
            self._initialized = False
            self._plugins_registered = False
            
            success = await self.initialize()
            if success:
                await self.start()
            
            return success
            
        except Exception as e:
            logger.error(f"✗ Reload error: {e}")
            return False
    
    def get_health(self) -> Dict[str, Any]:
        """Get application health status"""
        return {
            "initialized": self._initialized,
            "started": self._started,
            "plugins": self.registry.get_health(),
            "config_path": self.config_path,
        }
    
    async def __aenter__(self):
        await self.initialize()
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()


def create_app(config_path: Optional[str] = None) -> NexusApplication:
    """
    Create and configure a new Nexus application
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        NexusApplication instance
        
    Example:
        app = create_app("/path/to/config.yaml")
        await app.initialize()
        await app.start()
    """
    return NexusApplication(config_path)


# Global application instance (for convenience)
_global_app: Optional[NexusApplication] = None


def get_app() -> Optional[NexusApplication]:
    """Get the global application instance"""
    global _global_app
    return _global_app


def set_app(app: NexusApplication):
    """Set the global application instance"""
    global _global_app
    _global_app = app
