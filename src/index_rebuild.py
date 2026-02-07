#!/usr/bin/env python3
"""
Index Rebuild Tool - 重建索引

功能:
- 扫描所有 Session 文件
- 重建每日索引
- 修复损坏的索引
"""

import os
import re
from pathlib import Path
from datetime import datetime, timedelta
import yaml


class IndexRebuilder:
    """索引重建器"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.memory_path = self.base_path / "memory" / "90_Memory"
        self.stats = {
            "scanned": 0,
            "rebuilt": 0,
            "errors": 0,
            "sessions_found": 0
        }
    
    def scan_all_sessions(self) -> dict:
        """
        扫描所有 Session 文件
        
        Returns:
            Dict: date -> [session_files]
        """
        sessions_by_date = {}
        
        if not self.memory_path.exists():
            return sessions_by_date
        
        # 扫描所有日期目录
        for date_dir in sorted(self.memory_path.iterdir()):
            if date_dir.is_dir() and re.match(r'\d{4}-\d{2}-\d{2}', date_dir.name):
                sessions = []
                for session_file in date_dir.glob("session_*.md"):
                    if not session_file.name.endswith("_part*.md"):  # 跳过分割的部分
                        sessions.append(session_file)
                        self.stats["scanned"] += 1
                
                if sessions:
                    sessions_by_date[date_dir.name] = sessions
        
        return sessions_by_date
    
    def extract_session_metadata(self, session_path: Path) -> dict:
        """
        从 Session 文件提取元数据
        
        Returns:
            Dict with: uuid, topic, created, tags, status, gold_count
        """
        try:
            with open(session_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 frontmatter
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    frontmatter = content[3:end]
                    try:
                        data = yaml.safe_load(frontmatter)
                        if data:
                            return data
                    except:
                        pass
            
            # 备用解析: 从内容提取
            metadata = {
                'uuid': session_path.stem,
                'topic': 'Unknown',
                'created': datetime.now().isoformat(),
                'tags': [],
                'status': 'active',
                'gold_count': 0
            }
            
            # 提取 topic (第一个 # 标题)
            title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
            if title_match:
                metadata['topic'] = title_match.group(1).strip()
            
            # 统计 GOLD
            metadata['gold_count'] = content.count('#GOLD')
            
            return metadata
        except Exception as e:
            self.stats["errors"] += 1
            return None
    
    def rebuild_index(self, date: str, sessions: list) -> bool:
        """
        重建单个日期的索引
        
        Returns:
            bool: Success
        """
        index_path = self.memory_path / date / "_INDEX.md"
        
        # 收集所有 sessions
        session_list = []
        gold_keys = []
        topics = []
        
        for session_path in sessions:
            metadata = self.extract_session_metadata(session_path)
            if metadata:
                self.stats["sessions_found"] += 1
                
                session_id = session_path.stem.replace("session_", "")
                session_list.append((session_id, metadata))
                
                if metadata.get('topic') and metadata['topic'] not in topics:
                    topics.append(metadata['topic'])
                
                # 收集 gold keys
                if metadata.get('gold_count', 0) > 0:
                    gold_keys.append(f"{session_id}: {metadata['topic']}")
        
        # 生成索引内容
        content = f"""---
uuid: {datetime.now().strftime("%Y%m%d%H%M%S")}
type: daily-index
tags: [daily-index, {date}]
rebuilt: {datetime.now().isoformat()}
created: {date}
---

# {date} Daily Index

## Sessions ({len(session_list)})
"""
        
        for session_id, metadata in sorted(session_list):
            status = metadata.get('status', 'active')
            topic = metadata.get('topic', 'Unknown')
            content += f"- [{status}] session_{session_id} ({topic})\n"
        
        content += f"\n## Gold Keys ({len(gold_keys)})\n"
        if gold_keys:
            for key in gold_keys:
                content += f"- {key}\n"
        else:
            content += "_(no gold keys)_\n"
        
        content += f"\n## Topics ({len(topics)})\n"
        for topic in topics:
            content += f"- {topic}\n"
        
        try:
            # 确保目录存在
            index_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.stats["rebuilt"] += 1
            return True
        except Exception as e:
            print(f"  ❌ Error rebuilding {date}: {e}")
            self.stats["errors"] += 1
            return False
    
    def full_rebuild(self, dry_run: bool = True):
        """
        完整重建所有索引
        
        Args:
            dry_run: 仅显示计划，不实际执行
        """
        print("🔍 Scanning all sessions...")
        sessions_by_date = self.scan_all_sessions()
        
        if not sessions_by_date:
            print("❌ No sessions found")
            return
        
        print(f"\n📊 Found sessions in {len(sessions_by_date)} dates:")
        for date, sessions in sorted(sessions_by_date.items()):
            print(f"  - {date}: {len(sessions)} sessions")
        
        print(f"\n📈 Stats:")
        print(f"  - Total sessions scanned: {self.stats['scanned']}")
        print(f"  - Valid sessions: {self.stats['sessions_found']}")
        
        if dry_run:
            print("\n🟡 Dry run - use --rebuild to actually rebuild")
            return
        
        print(f"\n⚠️  Rebuilding {len(sessions_by_date)} indexes...")
        success_count = 0
        
        for date in sorted(sessions_by_date.keys()):
            print(f"\n📅 Rebuilding {date}...")
            if self.rebuild_index(date, sessions_by_date[date]):
                success_count += 1
        
        print(f"\n✅ Rebuild complete:")
        print(f"  - Indexes rebuilt: {self.stats['rebuilt']}")
        print(f"  - Errors: {self.stats['errors']}")
    
    def incremental_rebuild(self, date: str = None):
        """
        增量重建 (仅重建指定日期)
        
        Args:
            date: 日期 (YYYY-MM-DD), None = 今天
        """
        target_date = date or datetime.now().strftime("%Y-%m-%d")
        date_path = self.memory_path / target_date
        
        if not date_path.exists():
            print(f"❌ Date directory not found: {target_date}")
            return
        
        sessions = []
        for session_file in date_path.glob("session_*.md"):
            if not session_file.name.endswith("_part*.md"):
                sessions.append(session_file)
        
        print(f"📅 Rebuilding index for {target_date}...")
        print(f"   Found {len(sessions)} sessions")
        
        if self.rebuild_index(target_date, sessions):
            print(f"✅ Index rebuilt successfully")
        else:
            print(f"❌ Rebuild failed")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Index Rebuild Tool")
    parser.add_argument("--path", default="~/.openclaw/workspace/DEEP_SEA_NEXUS_V2",
                        help="Base path")
    parser.add_argument("--rebuild", action="store_true",
                        help="Actually perform rebuild")
    parser.add_argument("--date",
                        help="Specific date to rebuild (YYYY-MM-DD)")
    parser.add_argument("--full", action="store_true",
                        help="Full rebuild of all indexes")
    
    args = parser.parse_args()
    
    base_path = os.path.expanduser(args.path)
    rebuilder = IndexRebuilder(base_path)
    
    if args.full or (not args.date):
        rebuilder.full_rebuild(dry_run=not args.rebuild)
    else:
        rebuilder.incremental_rebuild(args.date)


if __name__ == "__main__":
    main()
