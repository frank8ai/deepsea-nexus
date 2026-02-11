#!/usr/bin/env python3
"""
DeepSea Nexus 工具 - 通过 Socket 快速调用
专为 OpenClaw 工具设计
"""

import socket
import json
import sys

SOCKET_PATH = "/tmp/nexus_warmup.sock"


def nexus_recall(query: str, n: int = 5) -> str:
    """通过 socket 调用预热服务"""
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        
        request = json.dumps({"query": query, "n": n})
        client.send(request.encode())
        
        response = client.recv(131072).decode()  # 128KB buffer
        client.close()
        
        result = json.loads(response)
        
        if "error" in result:
            return f"❌ 搜索失败: {result['error']}"
        
        results = result.get("results", [])
        if not results:
            return f"🔍 未找到与 \"{query}\" 相关的记忆"
        
        lines = [f"🔍 找到 {len(results)} 条相关记忆:\n"]
        
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. **{r['source']}**")
            content = r['content'][:150] + "..." if len(r['content']) > 150 else r['content']
            lines.append(f"   {content}")
            lines.append("")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"❌ 错误: {e}"


if __name__ == '__main__':
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else ""
    if not query:
        print("用法: python3 nexus_tool.py 关键词")
        sys.exit(1)
    
    print(nexus_recall(query))
