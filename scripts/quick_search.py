#!/usr/bin/env python3
"""
DeepSea Nexus 快速搜索 - 连接后台预热服务
使用方法：python3 quick_search.py "关键词"
"""

import socket
import json
import sys

# 服务配置
SOCKET_PATH = "/tmp/nexus_warmup.sock"


def send_query(query: str, n: int = 5) -> dict:
    """发送查询到后台服务"""
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        
        request = json.dumps({"query": query, "n": n})
        client.send(request.encode())
        
        response = client.recv(65536).decode()
        client.close()
        
        return json.loads(response)
    except Exception as e:
        return {"error": str(e)}


def main():
    if len(sys.argv) < 2:
        print("用法: python3 quick_search.py \"关键词\" [n]")
        print("示例: python3 quick_search.py \"nightly build\"")
        sys.exit(1)
    
    query = sys.argv[1]
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    result = send_query(query, n)
    
    if "error" in result:
        print(f"✗ 错误: {result['error']}")
        sys.exit(1)
    
    print(f"\n🔍 搜索: \"{query}\"\n")
    
    for i, r in enumerate(result.get("results", []), 1):
        print(f"{i}. [{r['source']}]")
        print(f"   {r['content'][:150]}...")
        print()


if __name__ == '__main__':
    main()
