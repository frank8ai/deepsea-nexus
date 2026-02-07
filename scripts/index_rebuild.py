#!/usr/bin/env python
"""
Index Rebuild Tool
Rebuild daily index from all session files
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import re

# Add project to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.nexus_core import NexusCore


def extract_session_info(session_file):
    """
    Extract metadata from session file
    
    Args:
        session_file: Path to session file
    
    Returns:
        Dict: Session metadata
    """
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract header fields
        topic = "Unknown"
        created = None
        gold_keywords = []
        
        lines = content.split('\n')
        in_header = False
        header_lines = []
        
        for line in lines:
            if line.startswith('---'):
                if not in_header:
                    in_header = True
                    continue
                else:
                    break
            if in_header:
                header_lines.append(line)
        
        # Parse header
        for line in header_lines:
            if line.startswith('tags:'):
                # Extract topic from tags
                tags_match = re.search(r'\[(.*?)\]', line)
                if tags_match:
                    tags = tags_match.group(1).split(',')
                    if tags:
                        topic = tags[0].strip()
            if 'created:' in line:
                created = line.split(':')[1].strip()
        
        # Extract GOLD keywords
        for line in lines:
            if '#GOLD' in line:
                keywords = line.replace('#GOLD', '').strip()
                if keywords:
                    gold_keywords.append(keywords[:50])
        
        # Extract filename for session_id
        basename = os.path.basename(session_file)
        session_id = basename.replace('session_', '').replace('.md', '')
        
        return {
            'session_id': session_id,
            'topic': topic,
            'created': created,
            'gold_keywords': gold_keywords,
            'file': session_file
        }
    except Exception as e:
        print(f"Error parsing {session_file}: {e}")
        return None


def rebuild_index_for_date(date_str, nexus):
    """
    Rebuild index for a specific date
    
    Args:
        date_str: Date in YYYY-MM-DD format
        nexus: NexusCore instance
    
    Returns:
        Dict: Rebuild statistics
    """
    base_path = nexus.config.get("paths.base")
    memory_path = nexus.config.get("paths.memory")
    date_dir = os.path.join(base_path, memory_path, date_str)
    index_file = os.path.join(date_dir, "_INDEX.md")
    
    if not os.path.exists(date_dir):
        print(f"❌ Directory not found: {date_dir}")
        return None
    
    # Collect all sessions
    sessions = []
    for f in os.listdir(date_dir):
        if f.startswith("session_") and f.endswith(".md"):
            session_file = os.path.join(date_dir, f)
            info = extract_session_info(session_file)
            if info:
                sessions.append(info)
    
    # Sort by session_id (which contains time)
    sessions.sort(key=lambda x: x['session_id'])
    
    # Build index content
    sessions_lines = []
    gold_lines = []
    topics = set()
    
    for s in sessions:
        sessions_lines.append(f"- [active] session_{s['session_id']} ({s['topic']})")
        topics.add(s['topic'])
        for gold in s['gold_keywords']:
            gold_lines.append(f"- session_{s['session_id']}: {gold}")
    
    sessions_section = "\n".join(sessions_lines) if sessions_lines else "_(no active sessions)_"
    gold_section = "\n".join(gold_lines) if gold_lines else "_(no gold keys)_"
    topics_section = "\n".join([f"- {t}" for t in topics]) if topics else "_(no topics)_"
    
    index_content = f"""---
uuid: {datetime.now().strftime("%Y%m%d%H%M%S")}
type: daily-index
tags: [daily-index, {date_str}]
created: {date_str}
---

# {date_str} Daily Index

## Sessions ({len(sessions)})
{sessions_section}

## Gold Keys ({len(gold_lines)})
{gold_section}

## Topics ({len(topics)})
{topics_section}

---
updated: {datetime.now().isoformat()}
"""
    
    # Write index file
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(index_content)
    
    print(f"✅ Rebuilt index for {date_str}: {len(sessions)} sessions, {len(gold_lines)} gold keys")
    
    return {
        "date": date_str,
        "sessions": len(sessions),
        "gold_keys": len(gold_lines),
        "topics": len(topics)
    }


def rebuild_all(nexus, month=None):
    """
    Rebuild all indices
    
    Args:
        nexus: NexusCore instance
        month: Specific month to rebuild (YYYY-MM format)
    
    Returns:
        List: Rebuild results
    """
    base_path = nexus.config.get("paths.base")
    memory_path = nexus.config.get("paths.memory")
    memory_dir = os.path.join(base_path, memory_path)
    
    results = []
    
    if month:
        # Rebuild specific month
        month_dir = os.path.join(memory_dir, month)
        if os.path.exists(month_dir):
            for d in os.listdir(month_dir):
                if re.match(r'\d{4}-\d{2}-\d{2}', d):
                    result = rebuild_index_for_date(d, nexus)
                    if result:
                        results.append(result)
        else:
            print(f"❌ Month directory not found: {month}")
    
    else:
        # Rebuild all dates
        for item in os.listdir(memory_dir):
            item_path = os.path.join(memory_dir, item)
            if os.path.isdir(item_path) and re.match(r'\d{4}-\d{2}-\d{2}', item):
                result = rebuild_index_for_date(item, nexus)
                if result:
                    results.append(result)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Index Rebuild Tool")
    parser.add_argument('--date', type=str, help='Rebuild index for specific date (YYYY-MM-DD)')
    parser.add_argument('--month', type=str, help='Rebuild all indices for month (YYYY-MM)')
    parser.add_argument('--all', action='store_true', help='Rebuild all indices')
    
    args = parser.parse_args()
    
    nexus = NexusCore()
    
    if args.date:
        rebuild_index_for_date(args.date, nexus)
    
    elif args.month:
        results = rebuild_all(nexus, args.month)
        print(f"✅ Rebuilt {len(results)} dates in {args.month}")
    
    elif args.all:
        results = rebuild_all(nexus)
        print(f"✅ Rebuilt {len(results)} dates total")
    
    else:
        print("Usage:")
        print("  python index_rebuild.py --date 2026-02-07    # Rebuild specific date")
        print("  python index_rebuild.py --month 2026-02       # Rebuild all dates in month")
        print("  python index_rebuild.py --all                 # Rebuild all dates")
