"""
智能摘要模块 - 自动生成并存储对话摘要

功能：
- 从 LLM 回复中解析摘要
- 混合存储摘要 + 原文到向量库
- 支持回溯到原始对话
"""

import re
from typing import Optional, Dict, Any, List


class SummaryParser:
    """摘要解析器"""
    
    # 分隔符模式 - 支持多种格式
    SUMMARY_PATTERNS = [
        re.compile(r'## 📋 总结[^\n]*\n([\s\S]*?)(?=\n\n|$)', re.DOTALL),  # ## 📋 总结 格式
        re.compile(r'---SUMMARY---\s*(.+?)\s*---END---', re.DOTALL | re.IGNORECASE),  # 旧格式
    ]
    
    @classmethod
    def parse(cls, response: str) -> tuple:
        """
        解析 LLM 回复，提取摘要和原文
        
        Args:
            response: LLM 原始回复
            
        Returns:
            (reply, summary) 元组
            - reply: 主体回复内容
            - summary: 摘要内容，无摘要时为 None
        """
        summary = None
        
        for pattern in cls.SUMMARY_PATTERNS:
            match = pattern.search(response)
            if match:
                summary = match.group(1).strip()
                # 移除摘要部分，得到原文
                response = pattern.sub('', response).strip()
                break
        
        return response, summary
    
    @classmethod
    def create_summary_prompt(cls, conversation_history: str) -> str:
        """
        生成摘要提示词
        
        Args:
            conversation_history: 对话历史
            
        Returns:
            包含摘要要求的完整提示词
        """
        return f"""
{conversation_history}

---
SUMMARY---
[用1-2句话总结本次对话核心要点]
---END---
"""


class HybridStorage:
    """混合存储管理器"""
    
    def __init__(self, vector_store):
        """
        初始化混合存储
        
        Args:
            vector_store: 向量库实例（需有 add 和 search 方法）
        """
        self.vector_store = vector_store
        self.parser = SummaryParser()
    
    def process_and_store(self, conversation_id: str, response: str, 
                          user_query: str = "") -> Dict[str, Any]:
        """
        处理 LLM 回复，解析并混合存储
        
        Args:
            conversation_id: 对话 ID
            response: LLM 原始回复
            user_query: 用户问题（可选，用于上下文）
            
        Returns:
            处理结果字典
        """
        # 1. 解析回复和摘要
        reply, summary = self.parser.parse(response)
        
        results = {
            "conversation_id": conversation_id,
            "reply": reply,
            "has_summary": summary is not None,
            "stored_count": 0
        }
        
        # 2. 存储原文
        try:
            self.vector_store.add(
                content=reply,
                title=f"对话 {conversation_id} - 原文",
                tags=f"type:content,source:{conversation_id}"
            )
            results["stored_count"] += 1
        except Exception as e:
            print(f"存储原文失败: {e}")
        
        # 3. 如果有摘要，也存储摘要
        if summary:
            try:
                self.vector_store.add(
                    content=summary,
                    title=f"对话 {conversation_id} - 摘要",
                    tags=f"type:summary,source:{conversation_id}"
                )
                results["stored_count"] += 1
            except Exception as e:
                print(f"存储摘要失败: {e}")
        
        return results
    
    def search_with_context(self, query: str, limit: int = 5) -> List[Dict]:
        """
        搜索并返回上下文信息
        
        Args:
            query: 搜索词
            limit: 返回数量
            
        Returns:
            搜索结果列表，包含类型标注
        """
        results = self.vector_store.search(query, limit=limit)
        
        # 添加类型标注
        for item in results:
            item["display_type"] = "摘要" if "type:summary" in (item.get("metadata", {}).get("tags", "") or "") else "原文"
        
        return results


def create_summary_system_prompt() -> str:
    """
    创建系统提示词模板
    
    Returns:
        包含摘要生成指令的系统提示词
    """
    return """
你是一个 AI 助手。请在回复结束时，按以下格式添加摘要：

[你的完整回复内容]

---SUMMARY---
[1-2句话总结本次对话的核心要点]
---END---

要求：
- 摘要要简洁明了
- 包含关键决策、技术术语、重要信息
- 不要包含客套话
"""


if __name__ == "__main__":
    # 测试
    parser = SummaryParser()
    
    test_response = """
Python 列表推导式是一种简洁的创建列表方式。

例如：[x for x in range(10) if x % 2 == 0]

---SUMMARY---
学习 Python 列表推导式的基本语法和用法
---END---
"""
    
    reply, summary = parser.parse(test_response)
    print("Reply:", reply)
    print("Summary:", summary)
