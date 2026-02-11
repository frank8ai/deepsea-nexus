#!/usr/bin/env python3
"""
智能摘要存储脚本

用法：
    python3 store_summary.py "对话ID" "LLM回复内容" "用户问题(可选)"

示例：
    python3 store_summary.py "session_001" "回复内容... ---SUMMARY--- 摘要 ---END---"

或交互式使用：
    python3 store_summary.py
    # 然后输入对话ID和回复内容
"""

import sys
import json
from nexus_core import NexusCore
from auto_summary import HybridStorage, SummaryParser


def main():
    nexus = NexusCore()
    if not nexus.init():
        print("✗ 初始化失败")
        sys.exit(1)
    
    storage = HybridStorage(nexus)
    
    if len(sys.argv) >= 3:
        # 命令行参数
        conversation_id = sys.argv[1]
        response = sys.argv[2]
        user_query = sys.argv[3] if len(sys.argv) > 3 else ""
    else:
        # 交互式输入
        print("=== 智能摘要存储 ===")
        conversation_id = input("对话ID: ").strip()
        print("请粘贴 LLM 回复内容 (Ctrl+D 完成):")
        response = sys.stdin.read().strip()
        user_query = input("用户问题 (可选): ").strip()
    
    # 解析
    reply, summary = SummaryParser.parse(response)
    
    print(f"\n✓ 解析成功")
    print(f"  原文: {reply[:50]}...")
    print(f"  摘要: {summary}")
    
    # 存储
    result = storage.process_and_store(
        conversation_id=conversation_id,
        response=response,
        user_query=user_query
    )
    
    print(f"\n✓ 存储完成")
    print(f"  存储数量: {result['stored_count']} 条")
    print(f"  对话ID: {result['conversation_id']}")


if __name__ == "__main__":
    main()
