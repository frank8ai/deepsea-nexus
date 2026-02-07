"""
配置管理模块
"""
import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml
from dotenv import load_dotenv


class NexusConfig:
    """
    Nexus 配置管理器
    
    功能：
    - 加载 YAML 配置
    - 支持环境变量覆盖
    - 路径展开
    """
    
    _instance: Optional['NexusConfig'] = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """加载配置文件"""
        load_dotenv()
        
        # 查找配置文件
        config_paths = [
            Path.cwd() / "config.yaml",
            Path.home() / ".config" / "deep-sea-nexus" / "config.yaml",
            Path(os.environ.get("DEEP_SEA_NEXUS_CONFIG", "config.yaml"))
        ]
        
        config_path = None
        for p in config_paths:
            if p.exists():
                config_path = p
                break
        
        if config_path is None:
            # 使用默认配置
            self._config = self._default_config()
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self._config = yaml.safe_load(f)
    
    def _default_config(self) -> Dict:
        """默认配置"""
        return {
            "project": {
                "name": "Deep-Sea Nexus v2.0",
                "version": "2.0.0"
            },
            "paths": {
                "base": str(Path.home() / "workspace" / "DEEP_SEA_NEXUS_V2"),
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
                "mcp_enabled": False
            },
            "flush": {
                "enabled": True,
                "time": "03:00"
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值 (支持点号路径)"""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        # 环境变量覆盖
        if isinstance(value, str) and value.startswith('$'):
            return os.environ.get(value[1:], default)
        
        return value if value is not None else default
    
    @property
    def base_path(self) -> Path:
        path_str = self.get("paths.base", str(Path.cwd()))
        return Path(os.path.expanduser(path_str))
    
    @property
    def memory_path(self) -> Path:
        return self.base_path / self.get("paths.memory", "memory/90_Memory")
    
    @property
    def max_index_tokens(self) -> int:
        return int(self.get("index.max_index_tokens", 300))
    
    @property
    def max_session_tokens(self) -> int:
        return int(self.get("index.max_session_tokens", 1000))
    
    @property
    def vector_store_enabled(self) -> bool:
        return bool(self.get("optional.vector_store", False))
    
    @property
    def mcp_enabled(self) -> bool:
        return bool(self.get("optional.mcp_enabled", False))
    
    @property
    def flush_enabled(self) -> bool:
        return bool(self.get("flush.enabled", True))
    
    @property
    def flush_time(self) -> str:
        return self.get("flush.time", "03:00")
    
    def __repr__(self) -> str:
        return f"NexusConfig(base={self.base_path})"
