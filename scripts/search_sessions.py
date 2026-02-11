#!/usr/bin/env python3
"""
会话记录搜索工具
"""

import os
import sqlite3
import sys

def search_sessions(query: str, db_path: str = None) -> list:
    """搜索会话"""
    if db_path is None:
        db_path = os.path.expanduser("~/.openclaw/workspace/memory/sessions.db")
    
    conn = sqlite3.connect(db_path)
    
    # 简单 LIKE 搜索
    cursor = conn.execute('''
        SELECT id, title, date, doc_type, source,
               CASE 
                   WHEN title LIKE ? OR content LIKE ? THEN 1
                   ELSE 0
               END as relevance
        FROM sessions
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY date DESC, relevance DESC
        LIMIT 10
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'id': row[0],
            'title': row[1],
            'date': row[2],
            'type': row[3],
            'source': row[4]
        })
    
    conn.close()
    return results


def show_session(session_id: str, db_path: str = None):
    """显示会话内容"""
    if db_path is None:
        db_path = os.path.expanduser("~/.openclaw/workspace/memory/sessions.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('''
        SELECT title, content, date, doc_type, created, source
        FROM sessions WHERE id = ?
    ''', (session_id,))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        print("=" * 60)
        print(f"标题: {row[0]}")
        print(f"日期: {row[2]} | 类型: {row[3]}")
        print(f"创建: {row[4]}")
        print("-" * 60)
        print(row[1][:500] + "..." if len(row[1]) > 500 else row[1])
        print("=" * 60)
    else:
        print(f"❌ 未找到会话: {session_id}")


def list_all(db_path: str = None, limit: int = 20):
    """列出所有会话"""
    if db_path is None:
        db_path = os.path.expanduser("~/.openclaw/workspace/memory/sessions.db")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('''
        SELECT id, title, date, doc_type
        FROM sessions
        ORDER BY date DESC, id DESC
        LIMIT ?
    ''', (limit,))
    
    print("=" * 60)
    print(f"{'日期':<12} | {'类型':<15} | {'标题'}")
    print("-" * 60)
    
    for row in cursor.fetchall():
        print(f"{row[2]:<12} | {row[3]:<15} | {row[1]}")
    
    conn.close()
    print("=" * 60)


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 search_sessions.py list          # 列出所有")
        print("  python3 search_sessions.py search <词>  # 搜索")
        print("  python3 search_sessions.py show <ID>    # 显示详情")
        return
    
    command = sys.argv[1]
    db_path = os.path.expanduser("~/.openclaw/workspace/memory/sessions.db")
    
    if command == 'list':
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        list_all(db_path, limit)
        
    elif command == 'search':
        if len(sys.argv) < 3:
            print("用法: python3 search_sessions.py search <查询词>")
            return
        query = sys.argv[2]
        results = search_sessions(query, db_path)
        
        print(f"\n🔍 搜索: '{query}'")
        print(f"📊 找到: {len(results)} 条结果\n")
        
        for r in results:
            print(f"  [{r['type']:<15}] {r['title']} ({r['date']})")
            
    elif command == 'show':
        if len(sys.argv) < 3:
            print("用法: python3 search_sessions.py show <会话ID>")
            return
        session_id = sys.argv[2]
        show_session(session_id, db_path)
    
    else:
        print("未知命令:", command)


if __name__ == "__main__":
    main()
