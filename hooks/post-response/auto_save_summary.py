#!/usr/bin/env python3
"""
智能摘要自动保存 Hook
每次AI回复后自动解析并保存摘要到向量库
"""

import os
import sys
import json
import re
from datetime import datetime

# 添加Deep-Sea Nexus路径
NEXUS_PATH = "/Users/yizhi/.openclaw/workspace/skills/deepsea-nexus"
sys.path.insert(0, NEXUS_PATH)

def main():
    # 从环境变量获取上下文
    context_json = os.environ.get("NEXUS_HOOK_CONTEXT", "{}")
    context = json.loads(context_json)
    
    # 获取回复内容（需要从OpenClaw传递过来）
    response = context.get("response", "")
    user_query = context.get("user_query", "")
    conversation_id = context.get("conversation_id", datetime.now().strftime("%Y%m%d_%H%M%S"))
    
    if not response:
        # 如果没有传递response，尝试从其他方式获取
        print("⚠️ 未检测到回复内容，跳过保存")
        return
    
    # 检查是否包含摘要格式
    if "## 📋 总结" not in response:
        print("ℹ️ 回复中未检测到摘要格式，跳过保存")
        return
    
    # 导入并保存
    try:
        from auto_summary import HybridStorage, SummaryParser
        from vector_store import create_vector_store
        
        # 创建向量库连接
        store = create_vector_store()
        storage = HybridStorage(store)
        
        # 处理并存储
        result = storage.process_and_store(
            conversation_id=conversation_id,
            response=response,
            user_query=user_query
        )
        
        if result['has_summary']:
            print(f"✅ 摘要已保存 | 对话: {conversation_id} | 存储: {result['stored_count']} 条")
        else:
            print(f"⚠️ 解析摘要失败 | 对话: {conversation_id}")
            
    except ImportError as e:
        # 降级方案：直接保存到文件
        save_to_fallback(response, conversation_id)
        print(f"⚠️ 向量库不可用，已保存到备用位置: {e}")
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def save_to_fallback(response: str, conversation_id: str):
    """降级保存到文件"""
    fallback_dir = os.path.expanduser("~/.openclaw/logs/summaries")
    os.makedirs(fallback_dir, exist_ok=True)
    
    # 解析摘要部分
    summary_match = re.search(r'## 📋 总结\s*\n\s*([\s\S]*?)(?=\n\n|$)', response)
    if summary_match:
        summary = summary_match.group(1).strip()
        
        # 保存为JSON
        log_file = os.path.join(fallback_dir, f"{conversation_id}.json")
        data = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "summary": summary,
            "full_response": response
        }
        
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
