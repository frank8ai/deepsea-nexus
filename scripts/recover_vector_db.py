#!/usr/bin/env python3
"""
向量库恢复脚本
从损坏的 deep_sea_nexus_notes 集合中恢复 2208 条数据
"""

import sqlite3
import chromadb
from chromadb.config import Settings
import json

VECTOR_DB_PATH = "/Users/yizhi/.openclaw/workspace/memory/.vector_db"
BACKUP_COLLECTION = "deepsea_nexus_backup"

def extract_data(limit=None):
    """从 SQLite 提取数据"""
    conn = sqlite3.connect(f"{VECTOR_DB_PATH}/chroma.sqlite3")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT e.embedding_id
        FROM embeddings e
        WHERE e.segment_id = '7c02facf-8a51-4f32-a773-d1decdc2f27b'
    """)
    embedding_ids = [row[0] for row in cursor.fetchall()]
    print(f"找到 {len(embedding_ids)} 条记录")
    
    documents = []
    metadatas = []
    ids = []
    
    for emb_id in embedding_ids[:limit] if limit else embedding_ids:
        # 获取文档内容
        cursor.execute("""
            SELECT string_value FROM embedding_metadata
            WHERE id = (SELECT id FROM embeddings WHERE embedding_id = ?)
            AND key = 'chroma:document'
        """, (emb_id,))
        doc_row = cursor.fetchone()
        
        if not doc_row:
            continue
            
        # 获取所有 metadata（排除 chroma:document）
        cursor.execute("""
            SELECT key, string_value FROM embedding_metadata
            WHERE id = (SELECT id FROM embeddings WHERE embedding_id = ?)
        """, (emb_id,))
        meta_rows = cursor.fetchall()
        
        documents.append(doc_row[0])
        # 过滤掉 chroma:document 键
        meta = {row[0]: row[1] for row in meta_rows if row[1] and row[0] != 'chroma:document'}
        metadatas.append(meta)
        ids.append(emb_id)
    
    conn.close()
    return ids, documents, metadatas

def recover_to_new_collection(batch_size=100):
    """恢复到新集合"""
    print("\n" + "=" * 50)
    print("开始恢复数据到新集合")
    print("=" * 50)
    
    # 获取所有数据
    all_ids, all_docs, all_metas = extract_data()
    print(f"准备恢复 {len(all_ids)} 条数据...")
    
    # 连接向量库
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    
    # 创建或获取备份集合
    try:
        coll = client.get_collection(BACKUP_COLLECTION)
        print(f"集合已存在，有 {coll.count()} 条数据")
    except:
        print(f"创建新集合: {BACKUP_COLLECTION}")
        coll = client.create_collection(BACKUP_COLLECTION)
    
    # 批量添加数据
    total = len(all_ids)
    for i in range(0, total, batch_size):
        batch_ids = all_ids[i:i+batch_size]
        batch_docs = all_docs[i:i+batch_size]
        batch_metas = all_metas[i:i+batch_size]
        
        coll.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        print(f"进度: {min(i+batch_size, total)}/{total}")
    
    print(f"\n✅ 恢复完成! 共 {coll.count()} 条数据")
    return coll

def test_search():
    """测试搜索"""
    client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    coll = client.get_collection(BACKUP_COLLECTION)
    
    print(f"\n集合 '{BACKUP_COLLECTION}': {coll.count()} 条数据")
    
    # 搜索测试
    results = coll.query(query_texts=["agent forum"], n_results=5)
    print(f"\n搜索 'agent forum': {len(results['documents'][0])} 条结果")
    for doc in results['documents'][0][:3]:
        print(f"  - {doc[:80]}...")

if __name__ == "__main__":
    recover_to_new_collection()
    test_search()
