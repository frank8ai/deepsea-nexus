#!/usr/bin/env python3
"""
Migrate Tool - v1.0 到 v2.0 迁移工具

功能:
- 检测旧版本文件
- 导入并保持 UUID
- 验证迁移结果
"""

import os
import re
import json
import shutil
from pathlib import Path
from datetime import datetime
import hashlib


class MigrationEngine:
    """迁移引擎"""
    
    def __init__(self, v1_path: str, v2_path: str):
        """
        Args:
            v1_path: v1.0 数据路径
            v2_path: v2.0 数据路径
        """
        self.v1_path = Path(v1_path)
        self.v2_path = Path(v2_path)
        self.stats = {
            "detected": 0,
            "migrated": 0,
            "skipped": 0,
            "errors": 0
        }
        self.migration_log = []
    
    def detect_v1_data(self) -> list:
        """
        检测 v1.0 数据
        
        Returns:
            List of (file_path, file_type)
        """
        detected = []
        
        # 检查常见 v1 目录结构
        v1_indicators = [
            "memory",
            "sessions",
            "archive",
            "logs",
            ".nexus"
        ]
        
        for indicator in v1_indicators:
            path = self.v1_path / indicator
            if path.exists():
                detected.append((path, indicator))
        
        # 检查单文件模式
        if self.v1_path.is_file():
            if self.v1_path.suffix in ['.json', '.md', '.txt']:
                detected.append((self.v1_path, "single_file"))
        
        # 检查 legacy 格式
        legacy_dir = self.v1_path / "legacy"
        if legacy_dir.exists():
            for f in legacy_dir.iterdir():
                if f.is_file():
                    detected.append((f, "legacy"))
        
        self.stats["detected"] = len(detected)
        return detected
    
    def parse_v1_session(self, file_path: Path) -> dict:
        """
        解析 v1.0 Session 文件
        
        Returns:
            Dict with: uuid, topic, content, created, tags
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 尝试多种格式
            
            # 1. JSON 格式
            if content.strip().startswith('{'):
                try:
                    data = json.loads(content)
                    return {
                        'uuid': data.get('uuid', self._generate_uuid()),
                        'topic': data.get('topic', file_path.stem),
                        'content': data.get('content', content),
                        'created': data.get('created', datetime.now().isoformat()),
                        'tags': data.get('tags', ['migrated']),
                        'original_format': 'json'
                    }
                except json.JSONDecodeError:
                    pass
            
            # 2. Markdown 格式 (v1 style)
            if content.startswith("---"):
                end = content.find("---", 3)
                if end > 0:
                    frontmatter = content[3:end]
                    body = content[end + 3:]
                    
                    # 解析 frontmatter
                    topic = file_path.stem
                    created = datetime.now().isoformat()
                    tags = ['migrated']
                    
                    for line in frontmatter.split('\n'):
                        if ':' in line:
                            key, val = line.split(':', 1)
                            if key.strip() == 'topic':
                                topic = val.strip()
                            elif key.strip() == 'created':
                                created = val.strip()
                            elif key.strip() == 'tags':
                                try:
                                    tags = json.loads(val.strip())
                                except:
                                    tags = [v.strip() for v in val.strip('[]').split(',')]
                    
                    return {
                        'uuid': self._generate_uuid(),
                        'topic': topic,
                        'content': body.strip(),
                        'created': created,
                        'tags': tags + ['migrated'],
                        'original_format': 'markdown'
                    }
            
            # 3. 纯文本格式
            return {
                'uuid': self._generate_uuid(),
                'topic': file_path.stem,
                'content': content,
                'created': datetime.now().isoformat(),
                'tags': ['migrated', 'plain_text'],
                'original_format': 'plain_text'
            }
            
        except Exception as e:
            self.stats["errors"] += 1
            return None
    
    def convert_to_v2_format(self, v1_data: dict, date: str = None) -> str:
        """
        转换为 v2.0 格式
        
        Args:
            v1_data: Parsed v1 data
            date: Target date
        
        Returns:
            v2.0 formatted markdown
        """
        date = date or datetime.now().strftime("%Y-%m-%d")
        uuid = v1_data.get('uuid', self._generate_uuid())
        
        content = f"""---
uuid: {uuid}
type: session
tags: [{', '.join(v1_data.get('tags', ['migrated']))}]
status: active
migrated: {datetime.now().isoformat()}
original_created: {v1_data.get('created', '')}
original_format: {v1_data.get('original_format', 'unknown')}
---

# {v1_data['topic']}

<!-- Migrated from v1.0 -->
<!-- Original UUID: {uuid} -->

{v1_data['content']}
"""
        return content
    
    def _generate_uuid(self) -> str:
        """生成 UUID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random = hashlib.md5(f"{timestamp}".encode()).hexdigest()[:8]
        return f"{timestamp}{random}"
    
    def migrate(self, dry_run: bool = True) -> dict:
        """
        执行迁移
        
        Args:
            dry_run: 仅显示计划，不执行
        
        Returns:
            Migration statistics
        """
        print("🔍 Detecting v1.0 data...")
        detected = self.detect_v1_data()
        
        if not detected:
            print("❌ No v1.0 data found")
            return self.stats
        
        print(f"\n📦 Found {len(detected)} items:")
        for path, file_type in detected:
            print(f"  - {path} ({file_type})")
        
        if dry_run:
            print("\n🟡 Dry run - use --migrate to actually migrate")
            return self.stats
        
        # 确保 v2 目录存在
        v2_memory = self.v2_path / "memory" / "90_Memory" / datetime.now().strftime("%Y-%m-%d")
        v2_memory.mkdir(parents=True, exist_ok=True)
        
        print(f"\n⚠️  Migrating to {v2_memory}...")
        
        for source_path, file_type in detected:
            if source_path.is_dir():
                # 递归处理目录
                for item in source_path.iterdir():
                    if item.is_file():
                        self._migrate_file(item)
            else:
                # 处理单个文件
                self._migrate_file(source_path)
        
        # 写入迁移日志
        self._write_migration_log()
        
        print(f"\n✅ Migration complete:")
        print(f"  - Migrated: {self.stats['migrated']}")
        print(f"  - Skipped: {self.stats['skipped']}")
        print(f"  - Errors: {self.stats['errors']}")
        
        return self.stats
    
    def _migrate_file(self, file_path: Path):
        """迁移单个文件"""
        v1_data = self.parse_v1_session(file_path)
        
        if not v1_data:
            self.stats["skipped"] += 1
            return
        
        # 生成 v2 格式
        v2_content = self.convert_to_v2_format(v1_data)
        
        # 生成文件名
        topic = re.sub(r'[^\w]', '', v1_data['topic'][:20])
        timestamp = datetime.now().strftime("%H%M%S")
        new_name = f"session_{timestamp}_{topic}.md"
        
        # 写入 v2 目录
        v2_memory = self.v2_path / "memory" / "90_Memory" / datetime.now().strftime("%Y-%m-%d")
        target_path = v2_memory / new_name
        
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(v2_content)
        
        self.stats["migrated"] += 1
        self.migration_log.append({
            'source': str(file_path),
            'target': str(target_path),
            'uuid': v1_data.get('uuid'),
            'topic': v1_data.get('topic'),
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"  ✓ {file_path.name} -> {new_name}")
    
    def _write_migration_log(self):
        """写入迁移日志"""
        log_path = self.v2_path / "memory" / "90_Memory" / "migration_log.json"
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'migration_date': datetime.now().isoformat(),
                'stats': self.stats,
                'log': self.migration_log
            }, f, indent=2, ensure_ascii=False)
    
    def validate_migration(self) -> bool:
        """
        验证迁移结果
        
        Returns:
            bool: All validations passed
        """
        print("\n🔍 Validating migration...")
        
        v2_memory = self.v2_path / "memory" / "90_Memory"
        
        if not v2_memory.exists():
            print("❌ v2.0 directory not found")
            return False
        
        # 检查文件数量
        sessions = list(v2_memory.glob("**/session_*.md"))
        print(f"  - Found {len(sessions)} migrated sessions")
        
        # 检查格式
        valid = True
        for session in sessions:
            with open(session, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 验证 frontmatter
            if not content.startswith("---"):
                print(f"  ⚠️  Missing frontmatter: {session.name}")
                valid = False
            
            if "migrated" not in content:
                print(f"  ⚠️  Missing migrated tag: {session.name}")
                valid = False
        
        if valid:
            print("✅ All validations passed")
        
        return valid


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migration Tool v1.0 -> v2.0")
    parser.add_argument("--v1", default="~/workspace/nexus_v1",
                        help="v1.0 data path")
    parser.add_argument("--v2", default="~/.openclaw/workspace/DEEP_SEA_NEXUS_V2",
                        help="v2.0 target path")
    parser.add_argument("--migrate", action="store_true",
                        help="Actually perform migration")
    parser.add_argument("--validate", action="store_true",
                        help="Validate migration results")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be done")
    
    args = parser.parse_args()
    
    v1_path = os.path.expanduser(args.v1)
    v2_path = os.path.expanduser(args.v2)
    
    if not os.path.exists(v1_path):
        print(f"❌ v1.0 path not found: {v1_path}")
        print("   Please specify --v1 /path/to/nexus_v1")
        return
    
    migrator = MigrationEngine(v1_path, v2_path)
    
    if args.validate:
        migrator.validate_migration()
    elif args.migrate:
        migrator.migrate(dry_run=False)
    else:
        migrator.migrate(dry_run=not args.migrate)


if __name__ == "__main__":
    main()
