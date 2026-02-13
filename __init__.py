"""
Deep-Sea Nexus v3.0 - Token Optimized Memory System
分层加载架构 | Token 成本降低 63-75%
"""

__version__ = "3.2.0"
__author__ = "Deep-Sea Nexus Team"

from core.nexus_v3 import Nexus, nexus_recall, nexus_add
from core.config_loader import (
    get_config_loader,
    get_resident_config,
    load_task_config,
    list_capabilities
)

__all__ = [
    "Nexus",
    "nexus_recall",
    "nexus_add",
    "get_config_loader",
    "get_resident_config",
    "load_task_config",
    "list_capabilities",
]
