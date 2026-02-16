#!/usr/bin/env python3
"""
DeepSea Nexus 智能记忆注入
==========================

通过 Socket 连接后台预热服务，实现毫秒级响应

功能：
- 自动检测触发词 ("还记得"、"上次提到" 等)
- 自动提取关键词搜索
- 每次对话自动注入相关记忆

使用方法：
    from nexus_autoinject import inject_memory, smart_search
    
    # 智能搜索（推荐）
    result = smart_search("还记得上次说的Python吗?")
    if result["triggered"]:
        print(f"触发: {result['trigger_pattern']}")
    
    # 简单注入
    context = inject_memory(user_message)
"""

import sys
import os
import socket
import json
from typing import Dict, List, Any, Optional

SOCKET_PATH = "/tmp/nexus_warmup.sock"


def _socket_search(query: str, n: int = 5) -> Optional[Dict]:
    """通过 socket 搜索，失败则返回 None"""
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)

        request = json.dumps({"query": query, "n": n})
        client.send(request.encode())

        response = client.recv(131072).decode()
        client.close()

        return json.loads(response)
    except Exception:
        return None


def _compat_search(query: str, n: int = 5) -> Optional[Dict]:
    """通过 compat API 搜索（无 socket 时的回退路径）"""
    try:
        from .compat import nexus_init, nexus_recall
    except Exception:
        try:
            from compat import nexus_init, nexus_recall
        except Exception:
            return None

    if not nexus_init():
        return None

    results = nexus_recall(query, n)
    if results is None:
        return None

    out = []
    for r in results:
        out.append({
            "content": getattr(r, "content", ""),
            "source": getattr(r, "source", ""),
            "relevance": getattr(r, "relevance", 0.0),
            "metadata": getattr(r, "metadata", {}) or {},
        })
    return {"query": query, "results": out}


# ===================== 统一触发词检测（已移到 utils/triggers.py） =====================
from .utils.triggers import detect_trigger, extract_keywords, smart_parse


# ===================== 智能搜索 =====================

def smart_search(user_input: str, n: int = 3) -> Dict[str, Any]:
    """
    智能搜索
    
    Returns:
        {
            "triggered": bool,
            "query": str,
            "trigger_pattern": str,
            "keywords": List[str],
            "results": str,  # 格式化结果
            "context": str  # 可注入上下文
        }
    """
    # 1. 检测触发词
    trigger = detect_trigger(user_input)
    
    if trigger:
        result = _socket_search(trigger["query"], n)
        if result is None:
            result = _compat_search(trigger["query"], n)
        return {
            "triggered": True,
            "query": trigger["query"],
            "trigger_pattern": trigger["pattern"],
            "keywords": [],
            "results": _format_result(result, trigger["query"]) if result else "",
            "context": _build_context(result) if result else ""
        }
    
    # 2. 关键词搜索
    keywords = extract_keywords(user_input, 3)
    if not keywords:
        return {"triggered": False, "query": "", "results": "", "context": ""}
    
    # 合并搜索
    all_results = []
    seen = set()
    
    for kw in keywords:
        result = _socket_search(kw, n)
        if result is None:
            result = _compat_search(kw, n)
        if result and "results" in result:
            for r in result["results"]:
                key = r["content"][:100]
                if key not in seen:
                    seen.add(key)
                    all_results.append(r)
    
    all_results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
    all_results = all_results[:n]
    
    return {
        "triggered": False,
        "query": " ".join(keywords),
        "keywords": keywords,
        "results": _format_keyword_results(all_results, keywords),
        "context": _build_keyword_context(all_results)
    }


def inject_memory(user_input: str, n: int = 3) -> str:
    """
    自动注入记忆上下文
    
    Args:
        user_input: 用户输入
        n: 结果数量
    
    Returns:
        str: 格式化的记忆上下文（无则为空）
    """
    result = smart_search(user_input, n)
    return result.get("context", "")


def _format_result(result: Dict, query: str) -> str:
    """格式化触发搜索结果"""
    if not result or not result.get("results"):
        return f"🔍 未找到与 \"{query}\" 相关的记忆"
    
    lines = [f"🔍 找到 {len(result['results'])} 条相关记忆:\n"]
    for i, r in enumerate(result["results"], 1):
        lines.append(f"{i}. **{r['source']}**")
        content = r['content'][:150] + "..." if len(r['content']) > 150 else r['content']
        lines.append(f"   {content}")
        lines.append("")
    return "\n".join(lines)


def _build_context(result: Dict) -> str:
    """构建可注入的上下文"""
    if not result or not result.get("results"):
        return ""
    
    lines = ["**相关记忆：**\n"]
    for i, r in enumerate(result["results"], 1):
        lines.append(f"{i}. **{r['source']}**")
        content = r['content'][:200] + "..." if len(r['content']) > 200 else r['content']
        lines.append(f"   {content}")
        lines.append("")
    return "\n".join(lines)


def _format_keyword_results(results: List[Dict], keywords: List[str]) -> str:
    """格式化关键词搜索结果"""
    if not results:
        return f"🔍 未找到与 \"{' '.join(keywords)}\" 相关的记忆"
    
    lines = [f"🔍 找到 {len(results)} 条相关记忆:\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r['source']}**")
        content = r['content'][:150] + "..." if len(r['content']) > 150 else r['content']
        lines.append(f"   {content}")
        lines.append("")
    return "\n".join(lines)


def _build_keyword_context(results: List[Dict]) -> str:
    """构建关键词搜索上下文"""
    if not results:
        return ""
    
    lines = ["**相关记忆：**\n"]
    for i, r in enumerate(results, 1):
        lines.append(f"{i}. **{r['source']}**")
        content = r['content'][:200] + "..." if len(r['content']) > 200 else r['content']
        lines.append(f"   {content}")
        lines.append("")
    return "\n".join(lines)


# ===================== 快捷函数 =====================

def quick_recall(query: str) -> str:
    """快速召回"""
    result = _socket_search(query, 5)
    return _format_result(result, query) if result else "❌ 搜索失败"


if __name__ == '__main__':
    print("=== 智能记忆注入测试 ===\n")
    
    test_cases = [
        "还记得上次说的Python列表吗?",
        "之前提到过的FastAPI配置",
        "上次讨论的项目进度",
        "nightly build",
        "OpenClaw 设置"
    ]
    
    for test in test_cases:
        print(f"用户输入: {test}")
        result = smart_search(test)
        
        if result["triggered"]:
            print(f"  ✅ 触发: '{result['trigger_pattern']}' → 搜索: {result['query']}")
        else:
            print(f"  ℹ️ 关键词: {result.get('keywords', [])}")
        
        if result["context"]:
            print(f"\n{result['context']}")
        else:
            print(f"  (无相关记忆)")
        
        print("\n" + "="*50 + "\n")
