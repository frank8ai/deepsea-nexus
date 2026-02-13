"""
Context Engine - 统一的智能上下文引擎

整合功能：
1. 摘要生成与存储（来自 auto_summary.py）
2. 上下文注入（来自 context_injector.py）
3. 触发词检测
4. 关键词注入
5. 会话恢复

让第二大脑越来越聪明 - 核心引擎
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum

from .nexus_core import NexusCore
from .session_manager import SessionManagerPlugin
from ..core.plugin_system import NexusPlugin, PluginMetadata
from ..core.event_bus import EventTypes


class MemoryTier(Enum):
    """记忆层级"""
    HOT = "hot"    # 最近活跃
    WARM = "warm"   # 最近使用
    COLD = "cold"   # 历史归档


@dataclass
class StructuredSummary:
    """
    结构化摘要 - 让第二大脑越来越聪明的核心数据类
    
    9 个字段设计：
    - core_output: 本次核心产出
    - tech_points: 技术要点
    - code_pattern: 代码模式
    - decision_context: 决策上下文
    - pitfall_record: 避坑记录
    - applicable_scene: 适用场景
    - search_keywords: 搜索关键词
    - project关联: 项目关联
    - confidence: 置信度
    """
    core_output: str = ""
    tech_points: List[str] = None
    code_pattern: str = ""
    decision_context: str = ""
    pitfall_record: str = ""
    applicable_scene: str = ""
    search_keywords: List[str] = None
    project关联: str = ""
    confidence: str = "medium"
    
    def __post_init__(self):
        if self.tech_points is None:
            self.tech_points = []
        if self.search_keywords is None:
            self.search_keywords = []
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StructuredSummary':
        return cls(
            core_output=data.get("本次核心产出", ""),
            tech_points=data.get("技术要点", []),
            code_pattern=data.get("代码模式", ""),
            decision_context=data.get("决策上下文", ""),
            pitfall_record=data.get("避坑记录", ""),
            applicable_scene=data.get("适用场景", ""),
            search_keywords=data.get("搜索关键词", []),
            project关联=data.get("项目关联", ""),
            confidence=data.get("置信度", "medium")
        )
    
    def to_searchable_text(self) -> str:
        parts = [
            self.core_output,
            " ".join(self.tech_points),
            self.code_pattern,
            self.decision_context,
            self.pitfall_record,
            self.applicable_scene,
            " ".join(self.search_keywords),
            self.project关联,
        ]
        return " ".join(p for p in parts if p)
    
    def to_tags(self) -> str:
        return ",".join(self.search_keywords)


@dataclass
class ContextEntry:
    """上下文条目"""
    content: str
    source: str
    relevance_score: float
    injected_at: str
    usage_count: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


class SummaryParser:
    """
    摘要解析器
    
    支持：
    - JSON 格式结构化摘要（新标准）
    - 旧格式兼容（---SUMMARY---）
    """
    
    JSON_PATTERN = re.compile(
        r'```json\s*\n([\s\S]*?)\n```',
        re.DOTALL
    )
    
    LEGACY_PATTERNS = [
        re.compile(r'## 📋 总结[^\n]*\n([\s\S]*?)(?=\n\n|$)', re.DOTALL),
        re.compile(r'---SUMMARY---\s*(.+?)\s*---END---', re.DOTALL | re.IGNORECASE),
    ]
    
    @classmethod
    def parse(cls, response: str) -> tuple:
        """解析 LLM 回复，提取摘要"""
        summary = None
        
        # 优先解析 JSON 格式
        json_match = cls.JSON_PATTERN.search(response)
        if json_match:
            json_str = json_match.group(1).strip()
            try:
                data = json.loads(json_str)
                summary = StructuredSummary.from_dict(data)
                response = cls.JSON_PATTERN.sub('', response).strip()
            except (json.JSONDecodeError, AttributeError):
                pass
        
        # 兼容旧格式
        if summary is None:
            for pattern in cls.LEGACY_PATTERNS:
                match = pattern.search(response)
                if match:
                    summary_text = match.group(1).strip()
                    summary = StructuredSummary(
                        core_output=summary_text,
                        confidence="low"
                    )
                    response = pattern.sub('', response).strip()
                    break
        
        return response, summary
    
    @classmethod
    def create_summary_prompt(cls) -> str:
        """生成结构化摘要提示词"""
        return """
## 🧠 知识沉淀（每次回复必须）

请用 JSON 格式总结本次对话要点：

```json
{
  "本次核心产出": "一句话说明解决了什么问题",
  "技术要点": ["关键点1", "关键点2"],
  "代码模式": "提取的可复用代码片段（如果有）",
  "决策上下文": "为什么选择这个方案",
  "避坑记录": "应避免的错误/弯路",
  "适用场景": "这个方案适用的场景",
  "搜索关键词": ["标签1", "标签2"],
  "项目关联": "所属项目（可选）",
  "置信度": "high/medium/low"
}
```

**要求**：
- 每个字段都要思考后填写
- 避免泛泛而谈，要具体可操作
- 重点突出"未来能用到"的信息
"""


class ContextEnginePlugin(NexusPlugin):
    """
    智能上下文引擎插件
    
    核心功能：
    1. 摘要生成与存储
    2. 上下文注入（触发词、引用）
    3. 关键词自动注入
    4. 会话恢复
    """
    
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="context_engine",
            version="3.1.0",
            description="Smart context engine - summaries, injection, keywords",
            dependencies=["nexus_core", "session_manager"],
            hot_reloadable=True,
        )
        self._nexus_core = None
        self._parser = SummaryParser()
        self._trigger_patterns = None
        
    async def initialize(self, config: Dict[str, Any]) -> bool:
        """初始化"""
        try:
            # 获取 nexus_core
            from ..core.plugin_system import get_plugin_registry
            registry = get_plugin_registry()
            self._nexus_core = registry.get("nexus_core")
            
            # 编译触发词模式
            self._trigger_patterns = [
                re.compile(p, re.IGNORECASE)
                for p in [
                    r'还记得(.+?)[吗?？]',
                    r'上次.*提到(.+)',
                    r'之前.*说过(.+)',
                    r'之前.*讨论(.+)',
                    r'之前.*决定(.+)',
                ]
            ]
            
            return True
        except Exception as e:
            print(f"ContextEngine init failed: {e}")
            return False
    
    async def start(self) -> bool:
        """启动"""
        return True
    
    async def stop(self) -> bool:
        """停止"""
        return True
    
    # ===================== 摘要功能 =====================
    
    def parse_summary(self, response: str) -> tuple:
        """解析摘要"""
        return self._parser.parse(response)
    
    def store_summary(self, conversation_id: str, response: str, 
                      user_query: str = "") -> Dict[str, Any]:
        """
        存储摘要到向量库
        
        Args:
            conversation_id: 对话 ID
            response: LLM 回复
            user_query: 用户问题
            
        Returns:
            存储结果
        """
        if not self._nexus_core:
            return {"error": "NexusCore not available"}
        
        reply, summary = self.parse_summary(response)
        
        results = {
            "conversation_id": conversation_id,
            "stored_count": 0,
            "has_summary": summary is not None,
        }
        
        try:
            # 1. 存储原文
            self._nexus_core.add_document(
                content=reply,
                title=f"对话 {conversation_id} - 原文",
                tags=f"type:content,source:{conversation_id}"
            )
            results["stored_count"] += 1
            
            # 2. 存储摘要
            if summary:
                if isinstance(summary, StructuredSummary):
                    # 结构化摘要
                    searchable = summary.to_searchable_text()
                    tags = f"type:structured_summary,confidence:{summary.confidence}"
                    if summary.search_keywords:
                        tags += "," + ",".join(summary.search_keywords)
                    
                    self._nexus_core.add_document(
                        content=searchable,
                        title=f"对话 {conversation_id} - 摘要",
                        tags=tags
                    )
                    results["stored_count"] += 1
                    
                    # 元数据
                    self._nexus_core.add_document(
                        content=json.dumps(summary.to_dict(), ensure_ascii=False),
                        title=f"对话 {conversation_id} - 元数据",
                        tags=f"type:metadata,source:{conversation_id}"
                    )
                    results["stored_count"] += 1
                    
                    results["summary_data"] = summary.to_dict()
                else:
                    # 旧格式
                    self._nexus_core.add_document(
                        content=summary.core_output,
                        title=f"对话 {conversation_id} - 摘要",
                        tags=f"type:summary,source:{conversation_id}"
                    )
                    results["stored_count"] += 1
                    results["summary_data"] = {"core_output": summary.core_output}
                    
        except Exception as e:
            results["error"] = str(e)
        
        return results
    
    # ===================== 触发词检测 =====================
    
    def detect_trigger(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        检测触发词
        
        Args:
            user_message: 用户消息
            
        Returns:
            触发结果或 None
        """
        if not self._trigger_patterns:
            return None
        
        for pattern in self._trigger_patterns:
            match = pattern.search(user_message)
            if match:
                return {
                    "triggered": True,
                    "pattern": match.group(0),
                    "query": user_message[match.end():].strip().rstrip("吗?？") or user_message[:match.start()].strip(),
                    "original_message": user_message
                }
        
        return None
    
    def resolve_reference(self, query: str, limit: int = 3) -> List[Dict]:
        """
        解析引用，检索相关历史
        
        Args:
            query: 查询词
            limit: 返回数量
            
        Returns:
            相关历史列表
        """
        if not self._nexus_core:
            return []
        
        try:
            from ..plugins.nexus_core import RecallResult
            results = self._nexus_core.search_recall(query, n=limit)
            
            return [
                {
                    "content": r.content,
                    "source": r.source,
                    "relevance": r.relevance,
                    "metadata": r.metadata,
                }
                for r in results
            ]
        except Exception:
            return []
    
    # ===================== 关键词注入 =====================
    
    def extract_keywords(self, text: str, max_count: int = 5) -> List[str]:
        """
        提取关键词
        
        Args:
            text: 文本
            max_count: 最大数量
            
        Returns:
            关键词列表
        """
        # 简单分词
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 停用词
        stop_words = {'的', '了', '是', '在', '我', '你', '他', '她', '它', '这', '那', 
                      '和', '与', '或', '就', '都', '也', '会', '可以', '什么', '怎么', '如何'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # 去重返回
        return list(dict.fromkeys(keywords))[:max_count]
    
    def inject_keywords(self, conversation: str, limit: int = 3) -> List[Dict]:
        """
        关键词自动注入
        
        Args:
            conversation: 对话内容
            limit: 每个关键词返回数量
            
        Returns:
            检索结果列表
        """
        keywords = self.extract_keywords(conversation, 5)
        results = []
        
        for keyword in keywords:
            related = self.resolve_reference(keyword, limit)
            for r in related:
                if r not in results:
                    results.append(r)
        
        return results[:10]  # 最多返回 10 条
    
    # ===================== 会话恢复 =====================
    
    def resume_session(self, session_id: str, topic: str = "", 
                       limit: int = 5) -> List[Dict]:
        """
        会话恢复，检索相关历史
        
        Args:
            session_id: 会话 ID
            topic: 话题
            limit: 返回数量
            
        Returns:
            相关历史列表
        """
        return self.resolve_reference(topic or session_id, limit)
    
    # ===================== 生成提示词 =====================
    
    def generate_context_prompt(self, 
                               references: List[Dict],
                               system_prompt: str = "") -> str:
        """
        生成上下文提示词
        
        Args:
            references: 参考列表
            system_prompt: 系统提示词
            
        Returns:
            完整提示词
        """
        if not references:
            return system_prompt
        
        context_parts = [
            system_prompt,
            "",
            "## 相关历史上下文",
            ""
        ]
        
        for i, ref in enumerate(references, 1):
            context_parts.append(f"【历史 {i}】({ref.get('source', '未知')})")
            context_parts.append(ref.get('content', '')[:500])
            context_parts.append("")
        
        return "\n".join(context_parts)


# ===================== 向后兼容 =====================

# 便捷函数
_parser = SummaryParser()


def parse_summary(response: str) -> tuple:
    """解析摘要（兼容旧 API）"""
    return _parser.parse(response)


def create_summary_prompt() -> str:
    """生成摘要提示词"""
    return _parser.create_summary_prompt()


# CLI 入口
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("🧠 Context Engine - 智能上下文引擎")
    print("=" * 60)
    
    # 测试解析
    test_response = """
这是测试回复。

```json
{
  "本次核心产出": "测试结构化摘要功能",
  "技术要点": ["测试", "解析"],
  "代码模式": "print('hello')",
  "决策上下文": "测试目的",
  "避坑记录": "无",
  "适用场景": "单元测试",
  "搜索关键词": ["测试", "上下文"],
  "项目关联": "Context Engine",
  "置信度": "high"
}
```
"""
    
    reply, summary = parse_summary(test_response)
    
    print("\n✅ 测试解析:")
    print(f"  原文: {reply[:50]}...")
    if summary:
        print(f"  核心产出: {summary.core_output}")
        print(f"  技术要点: {summary.tech_points}")
        print(f"  置信度: {summary.confidence}")
    
    print("\n✅ Context Engine 正常工作")
