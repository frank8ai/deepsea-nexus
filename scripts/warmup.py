#!/usr/bin/env python3
"""
DeepSea Nexus 预热脚本
预加载模型和向量库，避免首次搜索延迟
"""

import sys
import os

WORKSPACE = '/Users/yizhi/.openclaw/workspace'
NEXUS_PATH = os.path.join(WORKSPACE, 'deepsea-nexus')
VECTOR_STORE_PATH = os.path.join(NEXUS_PATH, 'vector_store')
RETRIEVAL_PATH = os.path.join(NEXUS_PATH, 'src', 'retrieval')

for path in [NEXUS_PATH, VECTOR_STORE_PATH, RETRIEVAL_PATH]:
    if path not in sys.path:
        sys.path.insert(0, path)


def warmup():
    """预热所有组件"""
    print("🔥 DeepSea Nexus 预热中...")
    
    # 1. 预加载 embedding 模型
    print("  📦 加载 embedding 模型...")
    from sentence_transformers import SentenceTransformer
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    _ = embedder.encode(["warmup"])  # 触发实际加载
    print("    ✓ 模型加载完成")
    
    # 2. 初始化 ChromaDB
    print("  🗄️  连接向量库...")
    import chromadb
    from chromadb.config import Settings
    
    path = '/Users/yizhi/.openclaw/workspace/memory/.vector_db'
    client = chromadb.PersistentClient(path=path, settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name='deep_sea_nexus_notes')
    print(f"    ✓ 向量库连接成功 ({collection.count()} 文档)")
    
    # 3. 测试检索
    print("  🔍 测试检索...")
    query_embedding = embedder.encode(["test query"]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=1)
    print(f"    ✓ 检索测试成功")
    
    print("\n✅ 预热完成！现在 /recall 命令会快很多。")
    
    # 返回初始化好的组件供后续使用
    return {
        'embedder': embedder,
        'client': client,
        'collection': collection
    }


if __name__ == '__main__':
    warmup()
