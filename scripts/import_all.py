#!/usr/bin/env python3
"""
批量导入会话和重要笔记到数据库
"""

import os
import sys
import glob
import sqlite3
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
    """初始化数据库"""
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
            doc_type TEXT
        )
    ''')
    conn.commit()
    return conn


def import_file(file_path: str, conn, doc_type: str = 'session') -> bool:
    """导入单个文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata, body = parse_frontmatter(content)
        title = metadata.get('title', Path(file_path).stem)
        doc_id = f"{doc_type}_{Path(file_path).stem}"
        
        conn.execute('''
            INSERT OR REPLACE INTO sessions 
            (id, title, content, date, tags, uuid, created, source, doc_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            doc_id,
            title,
            body,
            metadata.get('created', '')[:10] if metadata.get('created') else '',
            metadata.get('tags', doc_type),
            metadata.get('uuid', ''),
            metadata.get('created', ''),
            file_path,
            doc_type
        ))
        
        print(f"✅ 导入 [{doc_type}]: {title}")
        return True
        
    except Exception as e:
        print(f"❌ 失败: {os.path.basename(file_path)} - {e}")
        return False


def import_directory(session_dir: str, conn, pattern: str = "*.md", doc_type: str = 'session') -> dict:
    """导入目录下所有匹配的文件"""
    files = glob.glob(os.path.join(session_dir, pattern))
    stats = {'total': len(files), 'imported': 0, 'failed': 0}
    
    for file_path in files:
        if import_file(file_path, conn, doc_type):
            stats['imported'] += 1
        else:
            stats['failed'] += 1
    
    conn.commit()
    return stats


def main():
    print("=" * 60)
    print("批量导入工具 - 会话和笔记")
    print("=" * 60)
    
    db_path = os.path.expanduser("~/.openclaw/workspace/memory/sessions.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = init_db(db_path)
    print(f"✅ 数据库: {db_path}")
    
    all_stats = {'total': 0, 'imported': 0, 'failed': 0}
    
    # 1. 导入 2026-02 会话
    workspace_root = os.environ.get("OPENCLAW_WORKSPACE", os.path.expanduser("~/.openclaw/workspace"))
    nexus_root = os.path.join(workspace_root, "DEEP_SEA_NEXUS_V2")
    session_dir = os.path.join(nexus_root, "memory/90_Memory/2026-02")
    if os.path.exists(session_dir):
        print(f"\n📁 导入会话: {session_dir}")
        stats = import_directory(session_dir, conn, "session_*.md", 'session')
        all_stats['total'] += stats['total']
        all_stats['imported'] += stats['imported']
        all_stats['failed'] += stats['failed']
    
    # 2. 导入 Rescue 目录的会话
    rescue_dir = os.path.expanduser(
        "~/.openclaw/workspace/Obsidian/90_Memory/2026-02-11-Rescue"
    )
    if os.path.exists(rescue_dir):
        print(f"\n📁 导入 Rescue 会话: {rescue_dir}")
        stats = import_directory(rescue_dir, conn, "SESSION_*.md", 'rescue-session')
        all_stats['total'] += stats['total']
        all_stats['imported'] += stats['imported']
        all_stats['failed'] += stats['failed']
    
    # 3. 导入重要的 daily notes
    for date in ['2026-02-06', '2026-02-07', '2026-02-10']:
        daily_file = os.path.expanduser(f"~/.openclaw/workspace/memory/{date}.md")
        if os.path.exists(daily_file):
            print(f"\n📄 导入每日笔记: {date}")
            if import_file(daily_file, conn, 'daily-note'):
                all_stats['imported'] += 1
                all_stats['total'] += 1
    
    # 显示统计
    print("\n" + "=" * 60)
    print("导入完成!")
    print(f"  - 处理: {all_stats['total']}")
    print(f"  - 成功: {all_stats['imported']}")
    print(f"  - 失败: {all_stats['failed']}")
    
    cursor = conn.execute('SELECT COUNT(*), doc_type FROM sessions GROUP BY doc_type')
    print("\n📊 按类型统计:")
    for row in cursor.fetchall():
        print(f"  - {row[1]}: {row[0]}")
    
    conn.close()
    print("=" * 60)


if __name__ == "__main__":
    main()
