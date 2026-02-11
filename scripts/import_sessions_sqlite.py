#!/usr/bin/env python3
"""
会话导入脚本 - 使用系统 sqlite3
"""

import os
import sys
import glob
import sqlite3
import json
from pathlib import Path
from datetime import datetime

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
                metadata[key] = value
        elif found_opening and not in_frontmatter:
            body_lines.append(line)
    
    return metadata, '\n'.join(body_lines)


def init_db(db_path: str):
    """初始化 SQLite 数据库"""
    conn = sqlite3.connect(db_path)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            date TEXT,
            tags TEXT,
            uuid TEXT,
            created TEXT,
            source TEXT,
            embedding BLOB
        )
    ''')
    conn.commit()
    return conn


def import_sessions(session_dir: str, conn) -> dict:
    """导入会话"""
    session_files = glob.glob(os.path.join(session_dir, 'session_*.md'))
    
    stats = {'total': len(session_files), 'imported': 0, 'failed': 0}
    date_match = Path(session_dir).name
    
    for file_path in session_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            metadata, body = parse_frontmatter(content)
            title = metadata.get('title', Path(file_path).stem)
            doc_id = f"session_{Path(file_path).stem}"
            
            conn.execute('''
                INSERT OR REPLACE INTO sessions 
                (id, title, content, date, tags, uuid, created, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                doc_id,
                title,
                body,
                date_match,
                metadata.get('tags', 'session'),
                metadata.get('uuid', ''),
                metadata.get('created', ''),
                file_path
            ))
            
            stats['imported'] += 1
            print(f"✅ 导入: {title}")
            
        except Exception as e:
            stats['failed'] += 1
            print(f"❌ 失败: {os.path.basename(file_path)}")
    
    conn.commit()
    return stats


def main():
    print("=" * 60)
    print("会话记录导入工具 (SQLite)")
    print("=" * 60)
    
    # 数据库路径
    db_path = os.path.expanduser("~/.openclaw/workspace/memory/sessions.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = init_db(db_path)
    print(f"✅ 数据库: {db_path}")
    
    # 查找会话目录
    session_dir = os.path.expanduser(
        "~/.openclaw/workspace/deepsea-nexus/~/.openclaw/workspace/DEEP_SEA_NEXUS_V2/memory/90_Memory/2026-02"
    )
    
    if os.path.exists(session_dir):
        print(f"\n📁 会话目录: {session_dir}")
        stats = import_sessions(session_dir, conn)
        
        print("\n" + "=" * 60)
        print("导入完成!")
        print(f"  - 发现: {stats['total']}")
        print(f"  - 成功: {stats['imported']}")
        print(f"  - 失败: {stats['failed']}")
        
        # 显示统计
        cursor = conn.execute('SELECT COUNT(*) FROM sessions')
        print(f"  - 数据库总数: {cursor.fetchone()[0]}")
    else:
        print(f"⚠️  目录不存在: {session_dir}")
    
    conn.close()
    print("=" * 60)


if __name__ == "__main__":
    main()
