"""
Configuration management module for Deep-Sea Nexus v2.0
"""
import os
import json


class NexusConfig:
    """
    Nexus Configuration Manager
    
    Features:
    - Load configuration from JSON/YAML
    - Support environment variable overrides
    - Path expansion
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NexusConfig, cls).__new__(cls)
            cls._instance._config = {}
            cls._instance._load_config()
        return cls._instance
    
    @staticmethod
    def _load_config():
        """Load configuration file"""
        # This method is called on the instance, so we need to reference it properly
        pass
    
    def __init__(self):
        # Only load config once
        if not hasattr(self, '_initialized'):
            self._config = {}
            self._load_config_instance()
            self._initialized = True
    
    def _load_config_instance(self):
        """Load configuration file for the instance"""
        # Try to load from multiple locations
        config_paths = [
            os.path.join(os.getcwd(), "config.json"),  # Current working directory
            os.path.join(os.getcwd(), "config.yaml"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json"),  # Project config
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml"),  # Project config
            os.path.join(os.path.expanduser("~"), ".config", "deep-sea-nexus", "config.json"),
            os.path.join(os.environ.get("DEEP_SEA_NEXUS_CONFIG", "config.json")),
        ]
        
        config_path = None
        for p in config_paths:
            if os.path.exists(p):
                config_path = os.path.abspath(p)
                break
        
        # If no config file exists, use default config
        if config_path is None:
            self._config = self._default_config()
            return
        
        # Determine file type and load accordingly
        if config_path.endswith('.json'):
            with open(config_path, 'r') as f:
                self._config = json.load(f)
        else:
            # For YAML files, use default config if yaml module not available
            self._config = self._default_config()
    
    def _default_config(self):
        """Return default configuration"""
        return {
            "project": {
                "name": "Deep-Sea Nexus v2.0",
                "version": "2.0.0"
            },
            "paths": {
                "base": os.path.join(os.path.expanduser("~"), "workspace", "DEEP_SEA_NEXUS_V2"),
                "memory": "memory/90_Memory"
            },
            "index": {
                "max_index_tokens": 300,
                "max_session_tokens": 1000
            },
            "session": {
                "auto_split_size": 5000
            },
            "optional": {
                "vector_store": False,
                "rag_enabled": False,
                "mcp_enabled": False,
                "cross_date_search": False
            }
        }
    
    def get(self, key, default=None):
        """
        Get configuration value (supports dot notation)
        
        Args:
            key: Configuration key using dot notation (e.g. "index.max_tokens")
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        # Handle environment variable references
        if isinstance(value, str) and value.startswith('$'):
            env_key = value[1:]
            return os.environ.get(env_key, default)
        
        return value if value is not None else default
    
    def base_path(self):
        """Base path for the application"""
        return self.get("paths.base", os.path.join(os.getcwd()))
    
    def memory_path(self):
        """Memory storage path"""
        return os.path.join(self.base_path(), self.get("paths.memory", "memory/90_Memory"))
    
    def max_index_tokens(self):
        """Maximum tokens allowed in index"""
        return int(self.get("index.max_index_tokens", 300))
    
    def max_session_tokens(self):
        """Maximum tokens allowed per session"""
        return int(self.get("index.max_session_tokens", 1000))
    
    def vector_store_enabled(self):
        """Whether vector store is enabled"""
        return bool(self.get("optional.vector_store", False))
    
    def mcp_enabled(self):
        """Whether MCP is enabled"""
        return bool(self.get("optional.mcp_enabled", False))
    
    def cross_date_search_enabled(self):
        """Whether cross-date search is enabled"""
        return bool(self.get("optional.cross_date_search", False))


# Global config instance
config = NexusConfig()
