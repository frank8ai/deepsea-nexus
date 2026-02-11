"""
上下文自动注入器

功能：
- 会话恢复时自动检索相关历史
- 关键节点自动注入上下文
- 触发词检测 ("还记得")
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from layered_storage import LayeredStorage, MemoryItem, MemoryTier


@dataclass
class ContextEntry:
    """上下文条目"""
    content: str
    source: str
    relevance_score: float
    injected_at: str
    usage_count: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ContextBundle:
    """上下文包"""
    session_id: str
    entries: List[ContextEntry]
    total_tokens: int
    generated_at: str


class ContextInjector:
    """
    上下文自动注入器
    
    使用方法:
    injector = ContextInjector(
        layered_storage=storage,
        max_tokens=2000
    )
    
    # 会话恢复时调用
    bundle = injector.inject_on_resume("Python学习")
    
    # 触发词检测
    result = injector.detect_trigger("还记得上次说的X吗?")
    """
    
    # 触发词模式
    TRIGGER_PATTERNS = [
        r'还记得(.+?)[吗?？]',           # 还记得X吗
        r'上次.*提到(.+)',          # 上次提到X
        r'之前.*说过(.+)',          # 之前说过X
        r'之前.*讨论(.+)',          # 之前讨论X
        r'之前.*决定(.+)',          # 之前决定X
        r'前面.*内容(.+)',          # 前面内容X
        r'之前.*项目(.+)',          # 之前项目X
        r'上次.*对话(.+)',          # 上次对话X
        r'之前.*聊天(.+)',          # 之前聊天X
    ]
    
    def __init__(self,
                 layered_storage: LayeredStorage = None,
                 max_tokens: int = 2000):
        """
        初始化注入器
        
        Args:
            layered_storage: 分层存储实例
            max_tokens: 最大注入 token
        """
        self.storage = layered_storage or LayeredStorage()
        self.max_tokens = max_tokens
        
        # 编译触发词模式
        self.trigger_patterns = [
            re.compile(p, re.IGNORECASE) 
            for p in self.TRIGGER_PATTERNS
        ]
        
        # 注入历史
        self.injection_history: Dict[str, List[ContextEntry]] = {}
        
        # 回调
        self._on_inject: Optional[Callable[[str, ContextBundle], None]] = None
    
    def register_inject_callback(self, callback: Callable[[str, ContextBundle], None]):
        """注册注入回调"""
        self._on_inject = callback
    
    def inject_on_resume(self,
                        session_id: str,
                        topic: str = "",
                        limit: int = 5) -> ContextBundle:
        """
        会话恢复时自动注入上下文
        
        Args:
            session_id: 会话 ID
            topic: 会话话题
            limit: 检索数量
            
        Returns:
            ContextBundle: 上下文包
        """
        # 1. 检索相关历史
        related_items = self._retrieve_related(topic, limit)
        
        # 2. 构建上下文
        entries = []
        total_tokens = 0
        
        for item in related_items:
            entry = ContextEntry(
                content=item.content[:500],  # 截断
                source=f"历史: {item.title}",
                relevance_score=self._calculate_relevance(item, topic),
                injected_at=datetime.now().isoformat(),
                usage_count=item.access_count
            )
            
            entry_tokens = len(entry.content) // 4  # 粗略估算
            if total_tokens + entry_tokens <= self.max_tokens:
                entries.append(entry)
                total_tokens += entry_tokens
        
        bundle = ContextBundle(
            session_id=session_id,
            entries=entries,
            total_tokens=total_tokens,
            generated_at=datetime.now().isoformat()
        )
        
        # 3. 记录注入历史
        self.injection_history[session_id] = entries
        
        # 4. 触发回调
        if self._on_inject:
            self._on_inject(session_id, bundle)
        
        return bundle
    
    def detect_trigger(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        检测触发词
        
        Args:
            user_message: 用户消息
            
        Returns:
            Dict 或 None: 触发结果
        """
        for pattern in self.trigger_patterns:
            match = pattern.search(user_message)
            if match:
                # 提取触发内容
                trigger_content = match.group(0)
                # 尝试提取查询词
                query = self._extract_query(user_message, match)
                
                return {
                    "triggered": True,
                    "pattern": trigger_content,
                    "query": query,
                    "original_message": user_message
                }
        
        return None
    
    def resolve_reference(self,
                         user_message: str,
                         session_id: str = None,
                         limit: int = 3) -> Optional[ContextBundle]:
        """
        解析引用并检索上下文
        
        Args:
            user_message: 用户消息
            session_id: 会话 ID
            limit: 检索数量
            
        Returns:
            ContextBundle 或 None
        """
        # 1. 检测触发
        trigger_result = self.detect_trigger(user_message)
        
        if not trigger_result:
            return None
        
        # 2. 提取查询词
        query = trigger_result.get("query", user_message)
        
        # 3. 检索相关历史
        related_items = self._retrieve_related(query, limit)
        
        # 4. 构建上下文
        entries = []
        total_tokens = 0
        
        for item in related_items:
            entry = ContextEntry(
                content=item.content[:500],
                source=f"引用: {item.title}",
                relevance_score=1.0,
                injected_at=datetime.now().isoformat(),
                usage_count=item.access_count
            )
            
            entry_tokens = len(entry.content) // 4
            if total_tokens + entry_tokens <= self.max_tokens:
                entries.append(entry)
                total_tokens += entry_tokens
        
        return ContextBundle(
            session_id=session_id or "reference",
            entries=entries,
            total_tokens=total_tokens,
            generated_at=datetime.now().isoformat()
        )
    
    def get_injection_history(self, session_id: str) -> List[ContextEntry]:
        """获取注入历史"""
        return self.injection_history.get(session_id, [])
    
    def generate_context_prompt(self, bundle: ContextBundle) -> str:
        """
        生成上下文提示词
        
        Args:
            bundle: 上下文包
            
        Returns:
            str: 提示词
        """
        if not bundle.entries:
            return ""
        
        prompt_parts = [
            "以下是相关历史上下文供参考：",
            ""
        ]
        
        for i, entry in enumerate(bundle.entries, 1):
            prompt_parts.append(f"【历史 {i}】({entry.source})")
            prompt_parts.append(entry.content)
            prompt_parts.append("")
        
        return "\n".join(prompt_parts)
    
    def auto_inject_keywords(self,
                            conversation: str,
                            session_id: str) -> List[str]:
        """
        自动识别对话中的关键词并检索
        
        Args:
            conversation: 对话内容
            session_id: 会话 ID
            
        Returns:
            List[str]: 检索到的上下文摘要
        """
        # 1. 提取关键词
        keywords = self._extract_keywords(conversation)
        
        # 2. 检索每个关键词
        results = []
        for keyword in keywords[:5]:  # 最多5个
            items = self._retrieve_related(keyword, 2)
            for item in items:
                results.append(f"[{keyword}] {item.title}: {item.content[:100]}...")
        
        return results
    
    def _retrieve_related(self, query: str, limit: int) -> List[MemoryItem]:
        """检索相关记忆"""
        # 从热记忆和温记忆检索
        hot_items = [
            i for i in self.storage.index.values()
            if i.tier in (MemoryTier.HOT, MemoryTier.WARM)
        ]
        
        # 关键词匹配
        matched = []
        query_lower = query.lower()
        
        for item in hot_items:
            if query_lower in item.title.lower() or query_lower in item.content.lower():
                matched.append(item)
        
        # 按访问次数排序
        matched.sort(key=lambda x: x.access_count, reverse=True)
        
        return matched[:limit]
    
    def _calculate_relevance(self, item: MemoryItem, topic: str) -> float:
        """计算相关性分数"""
        score = 0.0
        
        # 标题匹配
        if topic.lower() in item.title.lower():
            score += 0.5
        
        # 内容匹配
        if topic.lower() in item.content.lower():
            score += 0.3
        
        # 访问频率加成
        score += min(item.access_count * 0.05, 0.2)
        
        return min(score, 1.0)
    
    def _extract_query(self, message: str, match) -> str:
        """提取查询词"""
        # 去掉触发词后的内容
        after_match = message[match.end():].strip()
        
        # 去掉句末的"吗"等
        after_match = after_match.rstrip("吗?？")
        
        return after_match if after_match else message[:match.start()].strip()
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        
        # 简单分词
        words = re.findall(r'\b\w+\b', text.lower())
        
        # 过滤停用词
        stop_words = {'的', '了', '是', '在', '我', '你', '他', '她', '它', '这', '那', '和', '与', '或'}
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # 返回唯一关键词
        return list(set(keywords))


class ContextManager:
    """
    上下文管理器 - 整合注入和检索
    
    使用方法:
    manager = ContextManager()
    
    # 会话开始
    manager.start_session("Python学习")
    
    # 对话中
    result = manager.handle_message("还记得上次说的X吗?")
    if result:
        print(result['context'])
    """
    
    def __init__(self):
        self.injector = ContextInjector()
        self.current_session_id: Optional[str] = None
    
    def start_session(self, session_id: str, topic: str = ""):
        """开始会话"""
        self.current_session_id = session_id
        return self.injector.inject_on_resume(session_id, topic)
    
    def handle_message(self, message: str) -> Optional[Dict[str, Any]]:
        """处理消息"""
        if not self.current_session_id:
            return None
        
        # 1. 检测触发
        trigger = self.injector.detect_trigger(message)
        
        if trigger:
            # 2. 解析引用
            bundle = self.injector.resolve_reference(
                message,
                self.current_session_id
            )
            
            if bundle and bundle.entries:
                return {
                    "type": "reference",
                    "trigger": trigger,
                    "context": self.injector.generate_context_prompt(bundle),
                    "entries": [e.to_dict() for e in bundle.entries]
                }
        
        # 3. 自动注入关键词
        keywords = self.injector.auto_inject_keywords(message, self.current_session_id)
        
        if keywords:
            return {
                "type": "keywords",
                "keywords": keywords
            }
        
        return None
    
    def get_injected_context(self) -> List[ContextEntry]:
        """获取已注入的上下文"""
        if self.current_session_id:
            return self.injector.get_injection_history(self.current_session_id)
        return []


# ===================== CLI =====================

if __name__ == "__main__":
    print("=== ContextInjector 测试 ===")
    
    # 创建
    injector = ContextInjector()
    
    # 添加测试数据
    print("\n添加测试数据...")
    injector.storage.add(
        "Python的列表推导式很强大，可以一行代码生成列表。",
        "Python列表推导式",
        "python,list"
    )
    injector.storage.add(
        "我们决定使用FastAPI作为Web框架。",
        "技术选型决定",
        "fastapi,web,decision"
    )
    
    # 测试会话恢复注入
    print("\n测试会话恢复注入:")
    bundle = injector.inject_on_resume("session_001", "Python")
    print(f"注入条目: {len(bundle.entries)}")
    for entry in bundle.entries:
        print(f"  - {entry.source}: {entry.content[:50]}...")
    
    # 测试触发词检测
    print("\n测试触发词检测:")
    test_messages = [
        "还记得上次说的Python列表吗?",
        "之前提到过的FastAPI配置",
        "上次讨论的项目进度",
        "今天天气怎么样"
    ]
    
    for msg in test_messages:
        result = injector.detect_trigger(msg)
        if result:
            print(f"  ✅ '{msg}' -> 触发词: {result['pattern']}, 查询: {result['query']}")
        else:
            print(f"  ❌ '{msg}' -> 无触发")
    
    # 测试引用解析
    print("\n测试引用解析:")
    bundle = injector.resolve_reference("还记得上次说的Python列表吗?", "session_001")
    if bundle:
        print(f"找到 {len(bundle.entries)} 条相关历史")
    else:
        print("未找到相关历史")
    
    print("\n✅ ContextInjector 测试完成")
