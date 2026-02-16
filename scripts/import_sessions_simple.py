#!/usr/bin/env python3
"""
简单会话导入脚本 - 将历史会话导入向量库
"""

import os
import sys
import glob
import json
from pathlib import Path
from datetime import datetime

# 尝试导入 chromadb
try:
    import chromadb
    from chromadb.config import Settings
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    print("⚠️  警告: chromadb 未安装")


def parse_frontmatter(content: str) -> tuple:
    """解析 markdown frontmatter"""
    lines = content.split('\n')
    metadata = {}
    body_lines = []
    in_frontmatter = False
    found_opening = False
    
    for line in lines:
        if line.strip() == '---':
            if not found_opening:
                found_opening = True
                in_frontmatter = True
                continue
            else:
                in_frontmatter = False
                continue
        
        if in_frontmatter and ':' in line:
            parts = line.split(':', 1)
            if len(parts) == 2:
                key = parts[0].strip()
                value = parts[1].strip()
                # 移除列表/字典标记
                value = value.strip('[]{}')
                metadata[key] = value
        elif found_opening and not in_frontmatter:
            body_lines.append(line)
    
    return metadata, '\n'.join(body_lines)


def import_sessions(session_dir: str, collection) -> dict:
    """导入会话目录下的所有会话"""
    session_files = glob.glob(os.path.join(session_dir, 'session_*.md'))
    
    stats = {
        'total': len(session_files),
        'imported': 0,
        'failed': 0
    }
    
    # 从目录名提取日期
    date_match = Path(session_dir).name
    
    for file_path in session_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata, body = parse_frontmatter(content)
            
            title = metadata.get('title', Path(file_path).stem)
            tags = metadata.get('tags', 'session')
            
            # 添加到向量库
            doc_id = f"session_{Path(file_path).stem}"
            
            collection.add(
                documents=[body],
                metadatars=[{
                    'title': title,
                    'type': 'session',
                    'date': date_match,
                    'source': file_path,
                    'tags': tags,
                    'uuid': metadata.get('uuid', ''),
                    'created': metadata.get('created', '')
                }],
                ids=[doc_id]
            )
            
            stats['imported'] += 1
            print(f"✅ 导入: {title}")
            
        except Exception as e:
            stats['failed'] += 1
            print(f"❌ 失败: {os.path.basename(file_path)} - {e}")
    
    return stats


def main():
    """主函数"""
    print("=" * 60)
    print("会话记录导入工具")
    print("=" * 60)
    
    if not DEPENDENCIES_AVAILABLE:
        print("❌ 缺少 chromadb，请先安装")
        return
    
    # 初始化 ChromaDB
    persist_dir = os.path.expanduser("~/.openclaw/workspace/memory/.vector_db")
    
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=Settings(anonymized_telemetry=False)
    )
    
    collection = client.get_or_create_collection(
        name="deep_sea_nexus_sessions"
    )
    
    print(f"✅ 向量库连接成功")
    
    # 查找会话目录
    workspace_root = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
    nexus_root = os.path.join(workspace_root, "DEEP_SEA_NEXUS_V2")
    session_dirs = [
        os.path.expanduser("~/Library/CloudStorage/GoogleDrive*/frank20170808@gmail.com/其他计算机/我的计算机 (2)/Documents/frank/编程学习/0.01-阿爪独立工作区/DEEP_SEA_NEXUS_V2/memory/90_Memory/2026-02"),
        os.path.join(nexus_root, "memory/90_Memory/2026-02"),
    ]
    
    all_stats = {'total': 0, 'imported': 0, 'failed': 0}
    
    for session_dir in session_dirs:
        if os.path.exists(session_dir):
            print(f"\n📁 发现会话目录: {session_dir}")
            stats = import_sessions(session_dir, collection)
            all_stats['total'] += stats['total']
            all_stats['imported'] += stats['imported']
            all_stats['failed'] += stats['failed']
        else:
            print(f"⚠️  目录不存在: {session_dir}")
    
    # 显示统计
    print("\n" + "=" * 60)
    print("导入完成!")
    print(f"📊 总计:")
    print(f"  - 发现会话: {all_stats['total']}")
    print(f"  - 成功导入: {all_stats['imported']}")
    print(f"  - 失败: {all_stats['failed']}")
    print(f"  - 向量库文档数: {collection.count()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
