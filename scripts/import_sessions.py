#!/usr/bin/env python3
"""
会话记录导入脚本 - 将历史会话导入向量库
"""

import os
import sys
import glob
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 添加 Deep-Sea Nexus 路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEXUS_PATH = os.path.join(PROJECT_ROOT, 'DEEP_SEA_NEXUS_V2')
sys.path.insert(0, NEXUS_PATH)
sys.path.insert(0, os.path.join(NEXUS_PATH, 'src', 'vector_store'))
sys.path.insert(0, os.path.join(NEXUS_PATH, 'src', 'retrieval'))

try:
    from init_chroma import create_vector_store
    from manager import create_manager
    from semantic_recall import create_semantic_recall
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  警告: {e}")
    DEPENDENCIES_AVAILABLE = False


def load_config() -> dict:
    """加载配置"""
    config_path = os.path.join(NEXUS_PATH, 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_session_file(file_path: str) -> Dict[str, Any]:
    """解析会话文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 frontmatter
    lines = content.split('\n')
    metadata = {}
    body = []
    in_frontmatter = False
    in_body = False
    
    for line in lines:
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                in_body = True
            continue
        
        if in_frontmatter and ':' in line:
            key = line.split(':')[0].strip()
            value = line.split(':', 1)[1].strip()
            if value.startswith('[') or value.startswith('{'):
                try:
                    value = eval(value)
                except:
                    pass
            metadata[key] = value
        elif in_body:
            body.append(line)
    
    return {
        'title': metadata.get('title', Path(file_path).stem),
        'content': '\n'.join(body),
        'uuid': metadata.get('uuid', ''),
        'created': metadata.get('created', ''),
        'tags': metadata.get('tags', []),
        'type': metadata.get('type', 'session'),
        'source': file_path
    }


def import_sessions(session_dir: str, store, config: dict) -> Dict[str, Any]:
    """导入会话目录下的所有会话"""
    session_files = glob.glob(os.path.join(session_dir, 'session_*.md'))
    
    stats = {
        'total': len(session_files),
        'imported': 0,
        'failed': 0,
        'chunks': 0
    }
    
    # 从文件名提取日期
    date_match = os.path.basename(session_dir)
    
    for file_path in session_files:
        try:
            session_data = parse_session_file(file_path)
            
            # 构建元数据
            metadata = {
                'title': session_data['title'],
                'source_file': session_data['source'],
                'type': 'session',
                'date': date_match,
                'uuid': session_data['uuid'],
                'created_at': session_data['created'],
                'tags': ','.join(session_data['tags']) if session_data['tags'] else 'session'
            }
            
            # 添加到向量库
            doc_id = store.add_note(
                content=session_data['content'],
                metadata=metadata
            )
            
            stats['imported'] += 1
            print(f"✅ 导入: {session_data['title']}")
            
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
        print("❌ 缺少依赖，请先安装 chromadb 和 sentence-transformers")
        return
    
    # 加载配置
    config = load_config()
    print(f"✅ 配置加载完成")
    
    # 初始化向量存储
    store = create_vector_store(config_path=os.path.join(NEXUS_PATH, 'config.yaml'))
    print(f"✅ 向量库连接成功: {store.collection.name}")
    
    # 查找会话目录
    session_dirs = [
        # Deep-Sea Nexus 备份中的会话
        os.path.join(PROJECT_ROOT, 'DEEP_SEA_NEXUS_V2/memory/90_Memory/2026-02'),
        os.path.join(PROJECT_ROOT, '~/Library/CloudStorage/GoogleDrive*/frank20170808@gmail.com/其他计算机/我的计算机 (2)/Documents/frank/编程学习/0.01-阿爪独立工作区/DEEP_SEA_NEXUS_V2/memory/90_Memory/2026-02'),
        # 工作区中的会话
        os.path.join(PROJECT_ROOT, 'memory/90_Memory/2026-02'),
    ]
    
    all_stats = {
        'total': 0,
        'imported': 0,
        'failed': 0,
        'chunks': 0
    }
    
    for session_dir in session_dirs:
        # 展开 ~
        session_dir = os.path.expanduser(session_dir)
        
        if os.path.exists(session_dir):
            print(f"\n📁 发现会话目录: {session_dir}")
            stats = import_sessions(session_dir, store, config)
            
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
    print(f"  - 向量库文档数: {store.collection.count()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
