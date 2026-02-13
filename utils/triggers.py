#!/usr/bin/env python3
"""
统一触发词检测模块

从多个文件中提取并合并的触发词检测逻辑
"""

import re
from typing import Dict, Any, Optional, List

# ===================== 触发词配置 =====================
TRIGGER_PATTERNS = [
    (r'还记得(.+?)[吗?？]', "还记得...吗"),
    (r'上次.*提到(.+)', "上次提到"),
    (r'之前.*说过(.+)', "之前说过"),
    (r'之前.*讨论(.+)', "之前讨论"),
    (r'之前.*决定(.+)', "之前决定"),
    (r'前面.*内容(.+)', "前面内容"),
    (r'之前.*项目(.+)', "之前项目"),
    (r'上次.*对话(.+)', "上次对话"),
    (r'之前.*聊天(.+)', "之前聊天"),
]

# 停用词
STOP_WORDS = {
    '的', '了', '是', '在', '我', '你', '他', '她', '它', '这', '那',
    '和', '与', '或', '就', '都', '也', '会', '可以', '什么', '怎么',
    '如何', '一下', '那个', '这个', '哪个', '吗', '呢', '吧'
}

# 预编译正则
_COMPILED_PATTERNS = [(re.compile(p, re.IGNORECASE), n) for p, n in TRIGGER_PATTERNS]


# ===================== 触发词检测 =====================
def detect_trigger(user_input: str) -> Optional[Dict[str, Any]]:
    """
    检测用户输入中的触发词
    
    Args:
        user_input: 用户输入文本
        
    Returns:
        Dict: {
            "triggered": bool,
            "pattern": str,      # 触发模式名称
            "query": str,        # 提取的查询词
            "original": str      # 原始输入
        }
        无触发时返回 None
    """
    for pattern, name in _COMPILED_PATTERNS:
        match = pattern.search(user_input)
        if match:
            # 提取查询词
            query = user_input[match.end():].strip().rstrip("吗?？")
            if not query:
                query = user_input[:match.start()].strip()
            
            return {
                "triggered": True,
                "pattern": name,
                "query": query or user_input,
                "original": user_input
            }
    return None


def has_trigger(user_input: str) -> bool:
    """快速检查是否有触发词"""
    return detect_trigger(user_input) is not None


# ===================== 关键词提取 =====================
def extract_keywords(text: str, max_keywords: int = 5) -> List[str]:
    """
    从文本中提取关键词
    
    Args:
        text: 输入文本
        max_keywords: 最大返回数量
        
    Returns:
        List[str]: 关键词列表
    """
    # 简单分词
    words = re.findall(r'\b\w+\b', text.lower())
    
    # 过滤停用词和短词
    keywords = [w for w in words if w not in STOP_WORDS and len(w) > 2]
    
    # 去重并返回
    return list(dict.fromkeys(keywords))[:max_keywords]


def extract_content_after_trigger(trigger_result: Dict) -> str:
    """
    从触发结果中提取查询内容
    
    Args:
        trigger_result: detect_trigger() 返回的结果
        
    Returns:
        str: 查询内容
    """
    return trigger_result.get("query", "")


# ===================== 便捷函数 =====================
def smart_parse(user_input: str) -> Dict[str, Any]:
    """
    智能解析用户输入
    
    Returns:
        {
            "has_trigger": bool,
            "is_keyword_search": bool,
            "trigger_info": Dict or None,
            "keywords": List[str],
            "query": str  # 实际查询词
        }
    """
    trigger = detect_trigger(user_input)
    
    if trigger:
        return {
            "has_trigger": True,
            "is_keyword_search": False,
            "trigger_info": trigger,
            "keywords": [],
            "query": trigger["query"]
        }
    
    keywords = extract_keywords(user_input, 5)
    
    return {
        "has_trigger": False,
        "is_keyword_search": len(keywords) > 0,
        "trigger_info": None,
        "keywords": keywords,
        "query": " ".join(keywords) if keywords else ""
    }


# ===================== 导出 =====================
__all__ = [
    "detect_trigger",
    "has_trigger", 
    "extract_keywords",
    "extract_content_after_trigger",
    "smart_parse",
    "TRIGGER_PATTERNS",
    "STOP_WORDS"
]


if __name__ == "__main__":
    # 测试
    test_cases = [
        "还记得上次说的Python吗?",
        "之前提到过的API配置",
        "nightly build 是什么",
        "帮我查一下日志"
    ]
    
    for text in test_cases:
        result = smart_parse(text)
        print(f"输入: {text}")
        print(f"  触发: {result['has_trigger']}")
        print(f"  关键词: {result['keywords']}")
        print(f"  查询: {result['query']}")
        print()
