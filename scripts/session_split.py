#!/usr/bin/env python
"""
Session Split Tool
Automatically split large session files (>50KB)
"""

import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.nexus_core import NexusCore


def split_session(session_file, max_size=50000):
    """
    Split a session file if it exceeds max_size
    
    Args:
        session_file: Path to session file
        max_size: Maximum size in bytes (default 50KB)
    
    Returns:
        List of new session files
    """
    if not os.path.exists(session_file):
        return []
    
    file_size = os.path.getsize(session_file)
    if file_size <= max_size:
        return [session_file]
    
    # Read content
    with open(session_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Parse header
    header_end = content.find('---\n\n')
    if header_end == -1:
        header_end = content.find('\n\n')
    
    header = content[:header_end + 4]
    body = content[header_end + 4:]
    
    # Split by chunks
    chunks = []
    chunk_num = 1
    current_chunk = ""
    
    for paragraph in body.split('\n\n'):
        if len(current_chunk) + len(paragraph) < max_size - len(header):
            current_chunk += paragraph + '\n\n'
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = paragraph + '\n\n'
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Write chunks
    base_name = os.path.basename(session_file)
    dir_name = os.path.dirname(session_file)
    new_files = []
    
    for i, chunk in enumerate(chunks):
        if i == 0:
            new_file = session_file
        else:
            name_parts = base_name.replace('.md', '').split('_')
            new_name = f"{name_parts[0]}_{name_parts[1]}_part{i+1}.md"
            new_file = os.path.join(dir_name, new_name)
        
        with open(new_file, 'w', encoding='utf-8') as f:
            f.write(header + chunk)
        
        new_files.append(new_file)
        print(f"  Created: {os.path.basename(new_file)} ({len(chunk)} chars)")
    
    return new_files


def scan_and_split(nexus, max_size=50000):
    """
    Scan all sessions and split large ones
    
    Args:
        nexus: NexusCore instance
        max_size: Maximum size in bytes
    
    Returns:
        Dict: Statistics
    """
    base_path = nexus.config.get("paths.base")
    memory_path = nexus.config.get("paths.memory")
    today = datetime.now().strftime("%Y-%m-%d")
    today_dir = os.path.join(base_path, memory_path, today)
    
    if not os.path.exists(today_dir):
        return {"scanned": 0, "split": 0}
    
    sessions = []
    for f in os.listdir(today_dir):
        if f.startswith("session_") and f.endswith(".md"):
            sessions.append(os.path.join(today_dir, f))
    
    split_count = 0
    for session_file in sessions:
        size = os.path.getsize(session_file)
        if size > max_size:
            print(f"⚠️ Splitting: {os.path.basename(session_file)} ({size} bytes)")
            new_files = split_session(session_file, max_size)
            split_count += len(new_files) - 1  # -1 because original kept
    
    return {
        "scanned": len(sessions),
        "split": split_count
    }


if __name__ == "__main__":
    import argparse
    from datetime import datetime
    
    parser = argparse.ArgumentParser(description="Session Split Tool")
    parser.add_argument('--scan', action='store_true', help='Scan and split large sessions')
    parser.add_argument('--file', type=str, help='Split specific file')
    parser.add_argument('--size', type=int, default=50000, help='Max size in bytes (default: 50000)')
    
    args = parser.parse_args()
    
    nexus = NexusCore()
    
    if args.scan:
        print("🔍 Scanning for large sessions...")
        stats = scan_and_split(nexus, args.size)
        print(f"✅ Scanned {stats['scanned']}, split {stats['split']} files")
    
    elif args.file:
        if os.path.exists(args.file):
            new_files = split_session(args.file, args.size)
            print(f"✅ Split into {len(new_files)} files")
        else:
            print(f"❌ File not found: {args.file}")
    
    else:
        print("Usage:")
        print("  python session_split.py --scan          # Scan and split all large sessions")
        print("  python session_split.py --file FILE    # Split specific file")
        print("  python session_split.py --size 30000   # Set max size (bytes)")
