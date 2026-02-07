#!/usr/bin/env python3
"""
Session Split Tool - 自动分割大文件

功能:
- 检测超过指定大小的 Session 文件
- 按大小分割文件
- 更新索引
"""

import os
import re
from pathlib import Path
from datetime import datetime


class SessionSplitter:
    """Session 文件分割器"""
    
    def __init__(self, base_path: str, threshold: int = 5000):
        """
        Args:
            base_path: 基础路径
            threshold: 分割阈值 (字节)
        """
        self.base_path = Path(base_path)
        self.threshold = threshold
    
    def detect_large_sessions(self, max_size: int = None) -> list:
        """
        检测超过大小的 Session 文件
        
        Returns:
            List of (file_path, size)
        """
        threshold = max_size or self.threshold
        memory_path = self.base_path / "memory" / "90_Memory"
        large_files = []
        
        if not memory_path.exists():
            return []
        
        for date_dir in memory_path.iterdir():
            if date_dir.is_dir() and re.match(r'\d{4}-\d{2}-\d{2}', date_dir.name):
                for session_file in date_dir.glob("session_*.md"):
                    if session_file.stat().st_size > threshold:
                        large_files.append((session_file, session_file.stat().st_size))
        
        return sorted(large_files, key=lambda x: x[1], reverse=True)
    
    def split_session(self, session_path: Path, max_parts: int = 5) -> list:
        """
        分割 Session 文件
        
        Args:
            session_path: Session 文件路径
            max_parts: 最大分割数
        
        Returns:
            List of new file paths
        """
        with open(session_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 读取头部 (frontmatter)
        header_end = content.find("---", 3)
        if header_end == -1:
            header_end = 0
        
        header = content[:header_end + 3] if header_end > 0 else ""
        body = content[header_end + 3:] if header_end > 0 else content
        
        # 按行分割
        lines = body.split('\n')
        parts = []
        current_part = []
        current_size = 0
        
        for line in lines:
            line_size = len(line.encode('utf-8'))
            if current_size + line_size > self.threshold and current_part:
                parts.append('\n'.join(current_part))
                current_part = []
                current_size = 0
            current_part.append(line)
            current_size += line_size
        
        if current_part:
            parts.append('\n'.join(current_part))
        
        # 创建分割文件
        new_files = []
        session_dir = session_path.parent
        session_name = session_path.stem  # session_HHMM_Topic
        
        for i, part_content in enumerate(parts[:max_parts]):
            part_file = session_dir / f"{session_name}_part{i+1}.md"
            
            new_content = f"""{header}

# Part {i+1} of {len(parts)}

---

{part_content}
"""
            
            with open(part_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            new_files.append(part_file)
        
        # 标记原文件为已分割
        old_content = f"""# SPLITTED - Original: {session_path.name}
# Split into {len(parts)} parts
# Parts: {', '.join([f.name for f in new_files])}

---

*(This file has been split. See individual part files.)*
"""
        
        with open(session_path, 'w', encoding='utf-8') as f:
            f.write(old_content)
        
        return new_files
    
    def update_index_for_split(self, original_file: Path, new_files: list):
        """更新索引以反映分割"""
        # 简化的索引更新: 添加注释说明
        # 实际项目中应该更新 _INDEX.md
        print(f"  Note: {original_file.name} split into {len(new_files)} parts")
        for f in new_files:
            print(f"    - {f.name}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Session Split Tool")
    parser.add_argument("--path", default="~/.openclaw/workspace/DEEP_SEA_NEXUS_V2",
                        help="Base path")
    parser.add_argument("--size", type=int, default=5000,
                        help="Split threshold in bytes")
    parser.add_argument("--split", action="store_true",
                        help="Actually perform split")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done without doing it")
    
    args = parser.parse_args()
    
    base_path = os.path.expanduser(args.path)
    splitter = SessionSplitter(base_path, args.size)
    
    print(f"🔍 Scanning for large sessions (>{args.size} bytes)...")
    large_files = splitter.detect_large_sessions()
    
    if not large_files:
        print("✅ No large sessions found")
        return
    
    print(f"Found {len(large_files)} large files:")
    for file_path, size in large_files:
        print(f"  - {file_path.name}: {size} bytes")
    
    if args.dry_run or not args.split:
        print("\nUse --split to actually split these files")
        return
    
    print(f"\n⚠️  Splitting {len(large_files)} files...")
    for file_path, size in large_files:
        print(f"\n📄 Splitting {file_path.name}...")
        new_files = splitter.split_session(file_path)
        splitter.update_index_for_split(file_path, new_files)
    
    print("\n✅ Split complete")


if __name__ == "__main__":
    main()
