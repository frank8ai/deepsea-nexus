"""
数据结构和类型定义
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class SessionStatus(Enum):
    """Session 状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


@dataclass
class SessionMetadata:
    """Session 元数据"""
    uuid: str                          # 唯一标识
    topic: str                        # 话题
    created_at: str                   # 创建时间
    last_active: str                  # 最后活跃
    status: SessionStatus = SessionStatus.ACTIVE
    gold_count: int = 0               # GOLD 标记数
    word_count: int = 0               # 字数
    tags: List[str] = field(default_factory=list)


@dataclass
class Session:
    """完整 Session"""
    metadata: SessionMetadata
    content: str                      # 内容


@dataclass
class DailyIndex:
    """每日索引"""
    date: str                          # 日期 YYYY-MM-DD
    sessions: Dict[str, SessionMetadata]  # Session 列表
    gold_keys: List[str]              # GOLD 关键词
    topics: List[str]                # 话题列表
    paused_sessions: Dict[str, str]  # 暂停的 Session


@dataclass
class RecallResult:
    """召回结果"""
    session_id: str
    relevance: float                 # 相关度 0-1
    content: str                     # 召回内容
    source: str                      # 来源
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IndexEntry:
    """索引条目"""
    session_id: str
    status: str                      # active/paused
    topic: str                      # 话题
    gold_keywords: List[str] = field(default_factory=list)
    last_active: str = ""


@dataclass
class NexusConfig:
    """Nexus 配置"""
    base_path: str = "~/workspace/DEEP_SEA_NEXUS_V2"
    memory_path: str = "memory/90_Memory"
    max_index_tokens: int = 300
    max_session_tokens: int = 1000
    auto_split_size: int = 5000
    flush_enabled: bool = True
    flush_time: str = "03:00"
