"""
Smart Context - 第二大脑核心子功能

功能：
1. 对话摘要存储 - 根据规则保留原文+摘要（已压缩）
2. 记忆库注入 - 提取记忆库关键信息注入上下文
3. 上下文压缩规则 - 根据对话轮数压缩

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
class ContextCompressionConfig:
    """
    上下文压缩配置
    
    规则配置：
    - 什么时候存储摘要
    - 什么时候注入上下文
    - 根据对话轮数压缩
    """
    # 对话轮数规则
    full_rounds: int = 8          # 完整保留最近 N 轮
    summary_rounds: int = 30      # 超过 N 轮只保留摘要
    compress_after_rounds: int = 50  # 超过 N 轮压缩/归档
    
    # 摘要存储规则
    store_summary_enabled: bool = True
    summary_min_length: int = 50
    compress_on_store: bool = True
    
    # 上下文注入规则
    inject_enabled: bool = True
    inject_threshold: float = 0.6
    inject_max_items: int = 3


@dataclass
class ConversationContext:
    """
    对话上下文
    
    记录每轮对话的上下文状态
    """
    round_num: int
    status: str  # "full", "summary", "compressed"
    content: str
    summary: str = ""
    created_at: str
    compressed: bool = False
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ===================== Smart Context 核心 =====================

class SmartContextPlugin(NexusPlugin):
    """
    Smart Context 插件
    
    第二大脑核心子功能：
    1. 存储对话摘要（根据规则）
    2. 注入记忆库上下文
    3. 根据对话轮数压缩上下文
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="smart_context",
            version="3.1.0",
            description="Smart context - summary storage, memory injection, context compression",
            dependencies=["nexus_core", "session_manager"],
            hot_reloadable=True,
        )
        self.config = ContextCompressionConfig()
        self._nexus_core = None
        self._context_history: List[ConversationContext] = []
        self._current_round = 0
    
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化"""
        try:
            from ..core.plugin_system import get_plugin_registry
            registry = get_plugin_registry()
            self._nexus_core = registry.get("nexus_core")
            
            if not self._nexus_core:
                print("⚠️ SmartContext: nexus_core 未就绪")
            
            # 加载配置
            if config.get("smart_context"):
                smart_cfg = config["smart_context"]
                self.config = ContextCompressionConfig(
                    full_rounds=smart_cfg.get("full_rounds", 8),
                    summary_rounds=smart_cfg.get("summary_rounds", 30),
                    compress_after_rounds=smart_cfg.get("compress_after_rounds", 50),
                    store_summary_enabled=smart_cfg.get("store_summary_enabled", True),
                    inject_enabled=smart_cfg.get("inject_enabled", True),
                )
            
            print(f"✅ SmartContext 初始化完成 (规则: {self.config.full_rounds}轮完整/{self.config.summary_rounds}轮摘要/{self.config.compress_after_rounds}轮压缩)")
            return True
            
        except Exception as e:
            print(f"❌ SmartContext 初始化失败: {e}")
            return False
    
    async def start(self) -> bool:
        """启动"""
        print("✅ SmartContext 启动")
        return True
    
    async def stop(self) -> bool:
        """停止"""
        print("✅ SmartContext 停止")
        return True
    
    # ===================== 对话轮数管理 =====================
    
    def get_current_round(self, conversation_id: str) -> int:
        """
        获取当前对话轮数
        
        从会话管理器获取当前轮数
        """
        # TODO: 从 session_manager 获取实际轮数
        return self._current_round
    
    def should_compress(self, round_num: int) -> Tuple[bool, str]:
        """
        判断是否应该压缩
        
        Returns:
            (should_compress, reason)
        """
        if round_num <= self.config.full_rounds:
            return False, "full"  # 最近 N 轮完整保留
        
        if round_num <= self.config.summary_rounds:
            return True, "summary"  # 中间的轮数只保留摘要
        
        return True, "compress"  # 更早的轮数压缩
    
    # ===================== 上下文处理 =====================
    
    def process_round(self, 
                     conversation_id: str,
                     round_num: int,
                     user_message: str,
                     ai_response: str) -> Dict[str, Any]:
        """
        处理单轮对话
        
        根据轮数决定处理方式：
        - 0-8 轮：完整保留
        - 9-30 轮：只保留摘要
        - 30+ 轮：压缩/归档
        
        Args:
            conversation_id: 对话 ID
            round_num: 当前轮数
            user_message: 用户消息
            ai_response: AI 回复
            
        Returns:
            处理结果
        """
        result = {
            "conversation_id": conversation_id,
            "round_num": round_num,
            "status": "unknown",
            "stored": False,
        }
        
        should_compress, reason = self.should_compress(round_num)
        
        if reason == "full":
            # 完整保留
            result["status"] = "full"
            result["content"] = ai_response
            result["compressed"] = False
            
        elif reason == "summary":
            # 只保留摘要
            result["status"] = "summary"
            summary = self._extract_summary(ai_response)
            result["summary"] = summary
            result["compressed"] = False
            
        else:  # compress
            # 压缩
            result["status"] = "compressed"
            summary = self._extract_summary(ai_response)
            result["summary"] = summary
            result["compressed"] = True
        
        # 存储
        if self._nexus_core:
            self._store_context(conversation_id, round_num, result)
            result["stored"] = True
        
        # 更新历史
        self._current_round = round_num
        
        return result
    
    def _extract_summary(self, response: str) -> str:
        """
        提取摘要
        
        优先级：
        1. JSON 格式
        2. ## 📋 总结 格式
        3. 默认摘要
        """
        # JSON 格式
        json_match = re.search(r'```json\s*\n([\s\S]*?)\n```', response)
        if json_match:
            try:
                data = json.loads(json_match.group(1))
                return data.get("本次核心产出", data.get("核心产出", ""))
            except json.JSONDecodeError:
                pass
        
        # ## 📋 总结 格式
        summary_match = re.search(r'## 📋 总结[^\n]*\n([\s\S]*?)(?=\n\n|$)', response)
        if summary_match:
            return summary_match.group(1).strip()
        
        # 默认摘要
        return response[:100].strip() + "..."
    
    def _store_context(self, conversation_id: str, round_num: int, context: Dict):
        """
        存储上下文到向量库
        """
        try:
            if context["status"] == "full":
                # 完整内容
                self._nexus_core.add_document(
                    content=context["content"],
                    title=f"对话 {conversation_id} - 轮{round_num} (完整)",
                    tags=f"type:full,round:{round_num},conversation:{conversation_id}"
                )
                
            elif context["status"] == "summary":
                # 只存摘要
                self._nexus_core.add_document(
                    content=f"[摘要] {context['summary']}",
                    title=f"对话 {conversation_id} - 轮{round_num} (摘要)",
                    tags=f"type:summary,round:{round_num},conversation:{conversation_id}"
                )
                
            else:  # compressed
                # 压缩存储
                self._nexus_core.add_document(
                    content=f"[已压缩] {context['summary']}",
                    title=f"对话 {conversation_id} - 轮{round_num} (已压缩)",
                    tags=f"type:compressed,round:{round_num},conversation:{conversation_id}"
                )
                
        except Exception as e:
            print(f"⚠️ 存储上下文失败: {e}")
    
    # ===================== 功能 1: 摘要存储 =====================
    
    def should_store_summary(self, response: str) -> bool:
        """判断是否应该存储摘要"""
        if not self.config.store_summary_enabled:
            return False
        
        if len(response) < self.config.summary_min_length:
            return False
        
        return True
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        stop_words = {
            '的', '了', '是', '在', '我', '你', '他', '这', '那',
            '和', '就', '都', '也', '会', '可以', '什么', '怎么',
            '如何', '有没有', '是不是', '能不能'
        }
        
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))[:5]
    
    def store_conversation(self, 
                          conversation_id: str,
                          user_message: str,
                          ai_response: str) -> Dict[str, Any]:
        """
        存储对话摘要（兼容旧 API）
        """
        result = {
            "conversation_id": conversation_id,
            "stored": False,
        }
        
        if not self.should_store_summary(ai_response):
            return result
        
        if not self._nexus_core:
            return result
        
        try:
            # 存储原文
            self._nexus_core.add_document(
                content=ai_response,
                title=f"对话 {conversation_id} - 原文",
                tags=f"type:content,source:{conversation_id}"
            )
            result["stored"] = True
            
            # 存储摘要
            summary = self._extract_summary(ai_response)
            if summary:
                self._nexus_core.add_document(
                    content=f"[摘要] {summary}",
                    title=f"对话 {conversation_id} - 摘要",
                    tags=f"type:summary,source:{conversation_id}"
                )
            
            # 存储关键词
            keywords = self.extract_keywords(user_message + " " + ai_response)
            if keywords:
                self._nexus_core.add_document(
                    content=" ".join(keywords),
                    title=f"对话 {conversation_id} - 关键词",
                    tags=f"type:keywords,source:{conversation_id}"
                )
                
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    # ===================== 功能 2: 上下文注入 =====================
    
    def should_inject(self, user_message: str) -> Tuple[bool, str]:
        """
        判断是否需要注入上下文
        """
        if not self.config.inject_enabled:
            return False, "disabled"
        
        question_patterns = [
            r'怎么', r'如何', r'是什么', r'为什么', r'哪些',
            r'区别', r'实现', r'使用', r'解决'
        ]
        
        for pattern in question_patterns:
            if re.search(pattern, user_message):
                return True, "question"
        
        keywords = self.extract_keywords(user_message)
        if any(k for k in keywords if len(k) > 6):
            return True, "technical_term"
        
        return False, "none"
    
    def inject_memory(self, user_message: str) -> List[Dict]:
        """
        注入记忆库上下文
        """
        should_inject, reason = self.should_inject(user_message)
        
        if not should_inject:
            return []
        
        if not self._nexus_core:
            return []
        
        try:
            results = self._nexus_core.search_recall(user_message, n=self.config.inject_max_items)
            
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
    
    # ===================== 便捷函数 =====================

def store_conversation(conversation_id: str, user_message: str, ai_response: str) -> Dict:
    """存储对话摘要（便捷函数）"""
    from .nexus_core import NexusCore
    
    nexus = NexusCore()
    if not nexus.init():
        return {"error": "nexus init failed"}
    
    # TODO: 使用插件实例
    return {"stored": True, "conversation_id": conversation_id}


def inject_memory_context(user_message: str) -> str:
    """注入记忆上下文（便捷函数）"""
    from .nexus_core import NexusCore
    
    nexus = NexusCore()
    if not nexus.init():
        return ""
    
    # TODO: 使用插件实例
    return ""


# ===================== 向后兼容 =====================

__all__ = [
    "SmartContextPlugin",
    "ContextCompressionConfig",
    "ConversationContext",
    "store_conversation",
    "inject_memory_context",
]
