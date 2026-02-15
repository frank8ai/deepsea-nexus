"""Config Manager Plugin

Provides `config_manager` as a first-class plugin so other plugins can depend on it.
The underlying implementation remains `core.config_manager.ConfigManager`.
"""

from __future__ import annotations

from typing import Any, Dict

from ..core.plugin_system import NexusPlugin, PluginMetadata
from ..core.config_manager import get_config_manager


class ConfigManagerPlugin(NexusPlugin):
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="config_manager",
            version="3.0.0",
            description="Configuration manager plugin",
            dependencies=[],
            hot_reloadable=True,
        )
        self._cfg = None

    async def initialize(self, config: Dict[str, Any]) -> bool:
        # Initialize singleton config manager with optional path.
        # If DeepSeaNexusApp already loaded a file, this becomes a no-op.
        self._cfg = get_config_manager()
        return True

    async def start(self) -> bool:
        return True

    async def stop(self) -> bool:
        return True
