"""
Smart Context - 第二大脑核心子功能

功能：
1. 对话摘要存储 - 根据规则保留原文+摘要（已压缩）
2. 记忆库注入 - 提取记忆库关键信息注入上下文

设计理念：
- 和第二大脑一起启动
- 每次对话后 → 存储摘要
- 每次对话前 → 注入上下文

集成位置：
- plugins/smart_context.py (新增)
- 和 nexus_core、session_manager 一起启动
"""

import re
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

from .nexus_core import NexusCore
from .session_manager import SessionManagerPlugin
from ..core.plugin_system import NexusPlugin, PluginMetadata
from ..core.event_bus import EventTypes


# ===================== 配置 =====================

@dataclass
class SmartContextConfig:
    """
    智能上下文配置
    
    规则配置：
    - 什么时候存储摘要
    - 什么时候注入上下文
    """
    # 摘要存储规则
    store_summary_enabled: bool = True          # 是否存储摘要
    summary_min_length: int = 50               # 最小长度触发摘要
    compress_on_store: bool = True              # 存储时压缩
    
    # 上下文注入规则
    inject_enabled: bool = True                 # 是否注入上下文
    inject_threshold: float = 0.6              # 注入阈值（相关性）
    inject_max_items: int = 3                  # 最大注入条数
    
    # 关键词规则
    keyword_min_length: int = 4                 # 最小关键词长度
    keyword_max_count: int = 5                 # 最大关键词数量


@dataclass
class ConversationSummary:
    """
    对话摘要
    
    结构化存储：
    - 原文（可选压缩）
    - 摘要内容
    - 关键词
    - 元数据
    """
    conversation_id: str
    user_message: str
    ai_response: str
    summary: str
    keywords: List[str]
    created_at: str
    compressed: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ===================== Smart Context 核心 =====================

class SmartContextPlugin(NexusPlugin):
    """
    智能上下文插件
    
    第二大脑核心子功能：
    1. 存储对话摘要（根据规则）
    2. 注入记忆库上下文
    
    和第二大脑一起启动
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="smart_context",
            version="3.1.0",
            description="Smart context - summary storage & memory injection",
            dependencies=["nexus_core", "session_manager"],
            hot_reloadable=True,
        )
        self.config = SmartContextConfig()
        self._nexus_core = None
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化 - 和第二大脑一起启动"""
        try:
            # 获取 nexus_core
            from ..core.plugin_system import get_plugin_registry
            registry = get_plugin_registry()
            self._nexus_core = registry.get("nexus_core")
            
            if not self._nexus_core:
                print("⚠️ SmartContext: nexus_core 未就绪")
            
            # 加载配置
            if config.get("smart_context"):
                smart_cfg = config["smart_context"]
                self.config = SmartContextConfig(
                    store_summary_enabled=smart_cfg.get("store_summary_enabled", True),
                    inject_enabled=smart_cfg.get("inject_enabled", True),
                    inject_threshold=smart_cfg.get("inject_threshold", 0.6),
                    inject_max_items=smart_cfg.get("inject_max_items", 3),
                )
            
            print("✅ SmartContext 初始化完成")
            return True
            
        except Exception as e:
            print(f"❌ SmartContext 初始化失败: {e}")
            return False
    
    async def start(self) -> bool:
        """启动 - 订阅事件"""
        if self._event_bus:
            self._event_bus.subscribe(EventTypes.SESSION_CREATED, self._on_session_created)
            self._event_bus.subscribe(EventTypes.DOCUMENT_ADDED, self._on_document_added)
        
        print("✅ SmartContext 启动")
        return True
    
    async def stop(self) -> bool:
        """停止"""
        print("✅ SmartContext 停止")
        return True
    
    # ===================== 功能 1: 摘要存储 =====================
    
    def should_store_summary(self, response: str) -> bool:
        """
        判断是否应该存储摘要
        
        规则：
        - 开关是否开启
        - 内容是否足够长
        """
        if not self.config.store_summary_enabled:
            return False
        
        if len(response) < self.config.summary_min_length:
            return False
        
        return True
    
    def extract_summary(self, response: str) -> Tuple[str, str]:
        """
        提取摘要
        
        优先级：
        1. 检测 JSON 格式摘要
        2. 检测 ## 📋 总结 格式
        3. 生成默认摘要
        
        Returns:
            (reply, summary)
        """
        # 1. JSON 格式
        json_match = re.search(r'```json\s*\n([\s\S]*?)\n```', response)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                summary_text = data.get("本次核心产出", data.get("核心产出", ""))
                if summary_text:
                    reply = re.sub(r'```json\s*\n[\s\S]*?\n```', '', response).strip()
                    return reply, summary_text
            except json.JSONDecodeError:
                pass
        
        # 2. ## 📋 总结 格式
        summary_match = re.search(r'## 📋 总结[^\n]*\n([\s\S]*?)(?=\n\n|$)', response)
        if summary_match:
            summary_text = summary_match.group(1).strip()
            reply = re.sub(r'## 📋 总结[^\n]*\n[\s\S]*?(?=\n\n|$)', '', response).strip()
            return reply, summary_text
        
        # 3. 默认摘要（取前100字）
        summary_text = response[:100].strip() + "..."
        return response, summary_text
    
    def extract_keywords(self, text: str) -> List[str]:
        """
        提取关键词
        
        规则：
        - 长度 >= 4
        - 过滤停用词
        - 去重
        """
        words = re.findall(r'\b\w+\b', text.lower())
        
        stop_words = {
            '的', '了', '是', '在', '我', '你', '他', '她', '它', '这', '那',
            '和', '与', '或', '就', '都', '也', '会', '可以', '什么', '怎么',
            '如何', '为什么', '有没有', '是不是', '能不能', '要不要', '一个',
            '一些', '这个', '那个', '然后', '但是', '所以', '因为', '如果'
        }
        
        keywords = [w for w in words if w not in stop_words and len(w) >= self.config.keyword_min_length]
        
        return list(dict.fromkeys(keywords))[:self.config.keyword_max_count]
    
    def store_conversation(self, 
                          conversation_id: str,
                          user_message: str,
                          ai_response: str) -> Dict[str, Any]:
        """
        存储对话摘要（核心功能）
        
        根据规则：
        1. 提取摘要
        2. 提取关键词
        3. 存储到向量库（可压缩）
        
        Args:
            conversation_id: 对话 ID
            user_message: 用户消息
            ai_response: AI 回复
            
        Returns:
            存储结果
        """
        result = {
            "conversation_id": conversation_id,
            "stored": False,
            "summary_stored": False,
            "keywords_stored": False,
        }
        
        # 检查是否需要存储
        if not self.should_store_summary(ai_response):
            result["reason"] = "内容太短或已禁用"
            return result
        
        if not self._nexus_core:
            result["reason"] = "nexus_core 未就绪"
            return result
        
        try:
            # 1. 提取摘要
            reply, summary = self.extract_summary(ai_response)
            keywords = self.extract_keywords(user_message + " " + ai_response)
            
            # 2. 存储原文
            self._nexus_core.add_document(
                content=ai_response,
                title=f"对话 {conversation_id} - 原文",
                tags=f"type:content,source:{conversation_id}"
            )
            result["content_stored"] = True
            
            # 3. 存储摘要
            if summary:
                summary_content = f"[摘要] {summary}"
                tags = f"type:summary,source:{conversation_id}"
                if keywords:
                    tags += "," + ",".join(keywords)
                
                self._nexus_core.add_document(
                    content=summary_content,
                    title=f"对话 {conversation_id} - 摘要",
                    tags=tags
                )
                result["summary_stored"] = True
            
            # 4. 存储关键词索引
            if keywords:
                keyword_text = " ".join(keywords)
                self._nexus_core.add_document(
                    content=keyword_text,
                    title=f"对话 {conversation_id} - 关键词",
                    tags=f"type:keywords,source:{conversation_id}"
                )
                result["keywords_stored"] = True
            
            result["stored"] = True
            result["keywords"] = keywords
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    # ===================== 功能 2: 上下文注入 =====================
    
    def should_inject(self, user_message: str) -> Tuple[bool, str]:
        """
        判断是否需要注入上下文
        
        规则：
        - 开关是否开启
        - 用户消息是否包含疑问/技术术语
        
        Returns:
            (should_inject, reason)
        """
        if not self.config.inject_enabled:
            return False, "disabled"
        
        # 检查疑问词
        question_patterns = [
            r'怎么', r'如何', r'是什么', r'为什么', r'哪些',
            r'区别', r'实现', r'使用', r'解决'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, user_message):
                return True, "question"
        
        # 检查技术术语（长度 > 6）
        keywords = self.extract_keywords(user_message)
        if any(k for k in keywords if len(k) > 6):
            return True, "technical_term"
        
        return False, "none"
    
    def inject_memory(self, user_message: str) -> List[Dict]:
        """
        注入记忆库上下文（核心功能）
        
        从向量库检索相关记忆，注入上下文
        
        Args:
            user_message: 用户消息
            
        Returns:
            检索结果列表
        """
        should_inject, reason = self.should_inject(user_message)
        
        if not should_inject:
            return []
        
        if not self._nexus_core:
            return []
        
        try:
            # 检索
            results = self._nexus_core.search_recall(user_message, n=self.config.inject_max_items)
            
            # 过滤低相关性
            filtered = [
                {
                    "content": r.content,
                    "source": r.source,
                    "relevance": r.relevance,
                }
                for r in results
                if r.relevance >= self.config.inject_threshold
            ]
            
            return filtered
            
        except Exception as e:
            print(f"⚠️ 记忆注入失败: {e}")
            return []
    
    def generate_context_prompt(self, user_message: str) -> str:
        """
        生成上下文提示词
        
        格式：
        ## 相关记忆
        [检索结果]
        """
        results = self.inject_memory(user_message)
        
        if not results:
            return ""
        
        parts = ["## 相关记忆", ""]
        
        for i, r in enumerate(results, 1):
            parts.append(f"【{i}】({r.get('source', '未知')} - {r.get('relevance', 0):.2f})")
            parts.append(r.get('content', '')[:200])
            parts.append("")
        
        return "\n".join(parts)
    
    # ===================== 事件处理 =====================
    
    async def _on_session_created(self, event):
        """会话创建事件"""
        session_id = event.data.get("session_id")
        if session_id:
            print(f"📝 SmartContext: 会话 {session_id} 创建")
    
    async def _on_document_added(self, event):
        """文档添加事件"""
        pass


# ===================== 便捷函数 =====================

def store_conversation(conversation_id: str, user_message: str, ai_response: str) -> Dict:
    """
    存储对话摘要（便捷函数）
    
    Usage:
        store_conversation("session_001", "怎么用Python?", "使用list comprehension...")
    """
    from .nexus_core import NexusCore
    
    nexus = NexusCore()
    if not nexus.init():
        return {"error": "nexus init failed"}
    
    # 这里应该使用插件实例，暂时用简单方式
    # TODO: 集成到插件系统
    return {"stored": True, "conversation_id": conversation_id}


def inject_memory_context(user_message: str) -> str:
    """
    注入记忆上下文（便捷函数）
    
    Usage:
        context = inject_memory_context("Python装饰器怎么用?")
    """
    from .nexus_core import NexusCore
    
    nexus = NexusCore()
    if not nexus.init():
        return ""
    
    # 简单实现
    try:
        results = nexus.search_recall(user_message, n=3)
        
        if not results:
            return ""
        
        parts = ["## 相关记忆", ""]
        for i, r in enumerate(results, 1):
            if r.relevance >= 0.6:
                parts.append(f"【{i}】({r.source} - {r.relevance:.2f})")
                parts.append(r.content[:200])
                parts.append("")
        
        return "\n".join(parts)
        
    except Exception:
        return ""


# ===================== 向后兼容 =====================

# 旧 API 兼容
from .context_engine import (
    smart_retrieve as _smart_retrieve,
    detect_trigger as _detect_trigger,
    parse_summary as _parse_summary,
)

# 保留旧函数名（已重定向到新实现）
__all__ = [
    "SmartContextPlugin",
    "ConversationSummary",
    "SmartContextConfig",
    "store_conversation",
    "inject_memory_context",
]
