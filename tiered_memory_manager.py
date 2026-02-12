#!/usr/bin/env python3
"""
Tiered Memory Manager - 三级优先级记忆管理系统

参考文章：从无限堆积到智能淘汰
https://twitter.com/Bitbird2014/status/189123456789

三级优先级：
- P0 — 核心记忆（永不淘汰）
  身份信息、长期偏好、安全红线、核心工作流
  
- P1 — 阶段性记忆（90 天有效期）
  当前项目进展、近期策略决策、正在执行的计划
  
- P2 — 临时记忆（30 天有效期）
  一次性事件、调试经验、临时偏好、某天的特殊安排
"""

import os
import re
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum


class Priority(Enum):
    """记忆优先级"""
    P0 = "P0"  # 核心 - 永不淘汰
    P1 = "P1"  # 阶段 - 90天
    P2 = "P2"  # 临时 - 30天


@dataclass
class MemoryEntry:
    """记忆条目"""
    content: str
    priority: Priority
    date: str  # YYYY-MM-DD
    source: str = ""  # 来源文件
    line_num: int = 0
    
    @classmethod
    def parse(cls, line: str, source: str = "", line_num: int = 0) -> Optional['MemoryEntry']:
        """解析一行记忆"""
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('---'):
            return None
        
        # 匹配 [P0][2025-10-01] 格式
        pattern = r'\[(P0|P1|P2)\]\[(\d{4}-\d{2}-\d{2})\] (.+)'
        match = re.match(pattern, line)
        
        if match:
            priority_str, date_str, content = match.groups()
            return cls(
                content=content.strip(),
                priority=Priority(priority_str),
                date=date_str,
                source=source,
                line_num=line_num
            )
        
        # 没有标注的，默认为 P2（临时）
        return cls(
            content=line,
            priority=Priority.P2,
            date=datetime.now().strftime("%Y-%m-%d"),
            source=source,
            line_num=line_num
        )
    
    def to_line(self) -> str:
        """转换为带标注的行"""
        return f"[{self.priority.value}][{self.date}] {self.content}"
    
    def is_expired(self, days: int) -> bool:
        """检查是否过期"""
        try:
            entry_date = datetime.strptime(self.date, "%Y-%m-%d")
            expire_date = datetime.now() - timedelta(days=days)
            return entry_date < expire_date
        except Exception:
            return False


class TieredMemoryManager:
    """
    分层记忆管理器
    
    使用方法:
    manager = TieredMemoryManager()
    
    # 加载记忆
    manager.load_memory("~/.openclaw/workspace/MEMORY.md")
    
    # 获取当前有效的记忆
    valid = manager.get_valid_entries()
    
    # 执行淘汰
    manager.evict(limit_lines=200)
    
    # 保存
    manager.save()
    """
    
    # 淘汰策略
    EVICT_POLICY = {
        Priority.P0: {"days": None, "desc": "永不淘汰"},  # 核心
        Priority.P1: {"days": 90, "desc": "90天"},        # 阶段
        Priority.P2: {"days": 30, "desc": "30天"},        # 临时
    }
    
    def __init__(self, base_path: str = None):
        self.base_path = base_path or os.path.expanduser("~/.openclaw/workspace")
        self.memory_file = os.path.join(self.base_path, "MEMORY.md")
        self.archive_dir = os.path.join(self.base_path, "archive")
        
        self.entries: List[MemoryEntry] = []
        self.archive_entries: List[MemoryEntry] = []
        
        # 确保归档目录存在
        os.makedirs(self.archive_dir, exist_ok=True)
    
    def load_memory(self, file_path: str = None) -> Tuple[int, Dict]:
        """
        加载记忆文件
        
        Returns:
            (总条目数, 统计信息)
        """
        path = file_path or self.memory_file
        if not os.path.exists(path):
            return 0, {"P0": 0, "P1": 0, "P2": 0}
        
        self.entries = []
        stats = {"P0": 0, "P1": 0, "P2": 0}
        
        with open(path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                entry = MemoryEntry.parse(line, source=path, line_num=i)
                if entry:
                    self.entries.append(entry)
                    stats[entry.priority.value] += 1
        
        return len(self.entries), stats
    
    def get_valid_entries(self, limit: int = None) -> List[MemoryEntry]:
        """
        获取有效（未过期）的记忆条目
        
        Args:
            limit: 最大返回数量
            
        Returns:
            未过期的条目列表
        """
        valid = []
        
        for entry in self.entries:
            if entry.priority == Priority.P0:
                # P0 永远有效
                valid.append(entry)
            elif entry.priority == Priority.P1:
                # P1 90天有效
                if not entry.is_expired(90):
                    valid.append(entry)
            elif entry.priority == Priority.P2:
                # P2 30天有效
                if not entry.is_expired(30):
                    valid.append(entry)
        
        if limit:
            valid = valid[:limit]
        
        return valid
    
    def get_expired_entries(self) -> Dict[Priority, List[MemoryEntry]]:
        """
        获取过期的记忆条目
        
        Returns:
            按优先级分组的过期条目
        """
        expired = {Priority.P0: [], Priority.P1: [], Priority.P2: []}
        
        for entry in self.entries:
            if entry.priority == Priority.P0:
                continue  # P0 永不过期
            
            days = self.EVICT_POLICY[entry.priority]["days"]
            if entry.is_expired(days):
                expired[entry.priority].append(entry)
        
        return expired
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        valid = self.get_valid_entries()
        expired = self.get_expired_entries()
        
        return {
            "总条目": len(self.entries),
            "有效条目": len(valid),
            "过期条目": sum(len(v) for v in expired.values()),
            "按优先级": {
                "P0(核心)": len([e for e in self.entries if e.priority == Priority.P0]),
                "P1(阶段)": len([e for e in self.entries if e.priority == Priority.P1]),
                "P2(临时)": len([e for e in self.entries if e.priority == Priority.P2]),
            },
            "可淘汰": {
                "P1过期": len(expired[Priority.P1]),
                "P2过期": len(expired[Priority.P2]),
            }
        }
    
    def evict(self, limit_lines: int = None, dry_run: bool = True) -> Dict:
        """
        执行淘汰
        
        Args:
            limit_lines: 最大保留行数（默认 200）
            dry_run: 预览模式，不实际执行
            
        Returns:
            淘汰统计
        """
        if limit_lines is None:
            limit_lines = 200
        
        # 获取过期条目
        expired = self.get_expired_entries()
        
        # 待淘汰的
        to_evict = []
        
        # 1. 淘汰过期的 P2 和 P1
        to_evict.extend(expired[Priority.P2])
        to_evict.extend(expired[Priority.P1])
        
        # 2. 如果超过行数限制，淘汰最旧的 P1
        remaining = [e for e in self.entries if e not in to_evict]
        
        if len(remaining) > limit_lines:
            # 按日期排序，最旧的在前
            remaining.sort(key=lambda x: x.date)
            
            # 淘汰多余的 P1
            excess = len(remaining) - limit_lines
            p1_only = [e for e in remaining if e.priority == Priority.P1]
            
            evict_count = 0
            for entry in p1_only:
                if evict_count >= excess:
                    break
                if entry not in to_evict:
                    to_evict.append(entry)
                    evict_count += 1
        
        # 执行淘汰
        evicted_count = {
            "P0": 0,
            "P1": len(expired[Priority.P1]) + (len([e for e in to_evict if e.priority == Priority.P1]) - len(expired[Priority.P1])),
            "P2": len(expired[Priority.P2]),
        }
        
        if not dry_run:
            # 移动到归档
            for entry in to_evict:
                self._archive_entry(entry)
                self.entries.remove(entry)
        
        return {
            "dry_run": dry_run,
            "evicted_count": evicted_count,
            "total_evicted": len(to_evict),
            "remaining": len(self.entries),
            "archive_dir": self.archive_dir
        }
    
    def _archive_entry(self, entry: MemoryEntry):
        """归档单个条目"""
        date = datetime.now().strftime("%Y-%m-%d")
        archive_file = os.path.join(self.archive_dir, f"archive_{date}.md")
        
        with open(archive_file, 'a', encoding='utf-8') as f:
            f.write(entry.to_line() + "\n")
    
    def categorize_content(self, content: str) -> List[MemoryEntry]:
        """
        智能分类内容
        
        根据内容自动判断优先级
        
        P0: 身份、安全、长期偏好、核心工作流
        P1: 项目进展、策略决策、执行计划
        P2: 调试经验、临时偏好、一次性事件
        """
        entries = []
        
        for line in content.split('\n'):
            if not line.strip():
                continue
            
            # 智能判断优先级
            priority = self._guess_priority(line)
            date = datetime.now().strftime("%Y-%m-%d")
            
            entries.append(MemoryEntry(
                content=line.strip(),
                priority=priority,
                date=date
            ))
        
        return entries
    
    def _guess_priority(self, line: str) -> Priority:
        """猜测优先级"""
        line_lower = line.lower()
        
        # P0 关键词
        p0_keywords = ['身份', '偏好', '安全', '红线', '性格', '核心', '永远', '从不']
        if any(kw in line_lower for kw in p0_keywords):
            return Priority.P0
        
        # P1 关键词
        p1_keywords = ['项目', '策略', '计划', '正在', '当前', '决策', '进展']
        if any(kw in line_lower for kw in p1_keywords):
            return Priority.P1
        
        # 默认 P2
        return Priority.P2
    
    def annotate_existing(self, content: str) -> str:
        """
        为现有内容添加标注（用于 Step 1）
        
        输入无标注的内容，输出带 [P0/P1/P2][YYYY-MM-DD] 标注的内容
        """
        entries = self.categorize_content(content)
        
        lines = []
        for entry in entries:
            lines.append(entry.to_line())
        
        return '\n'.join(lines)
    
    def save(self, file_path: str = None):
        """保存到文件"""
        path = file_path or self.memory_file
        
        with open(path, 'w', encoding='utf-8') as f:
            # 写入头部
            f.write("---\n")
            f.write(f"updated: {datetime.now().isoformat()}\n")
            f.write("---\n\n")
            
            # 按优先级排序写入（P0 优先）
            for priority in [Priority.P0, Priority.P1, Priority.P2]:
                for entry in self.entries:
                    if entry.priority == priority:
                        f.write(entry.to_line() + "\n")
                f.write("\n")
    
    def report(self) -> str:
        """生成报告"""
        stats = self.get_stats()
        
        lines = [
            "=" * 50,
            "🧠 记忆管理报告",
            "=" * 50,
            f"总条目: {stats['总条目']}",
            f"有效条目: {stats['有效条目']}",
            f"过期条目: {stats['过期条目']}",
            "",
            "按优先级:",
            f"  P0(核心,永不过期): {stats['按优先级']['P0(核心)']}",
            f"  P1(阶段,90天): {stats['按优先级']['P1(阶段)']}",
            f"  P2(临时,30天): {stats['按优先级']['P2(临时)']}",
            "",
            "可淘汰:",
            f"  P1过期: {stats['可淘汰']['P1过期']}",
            f"  P2过期: {stats['可淘汰']['P2过期']}",
            "=" * 50,
        ]
        
        return '\n'.join(lines)


# ===================== CLI =====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧠 分层记忆管理器 - 三级优先级 + 自动淘汰",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--load', action='store_true', help='加载并显示统计')
    parser.add_argument('--evict', action='store_true', help='执行淘汰')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（默认）')
    parser.add_argument('--limit', type=int, default=200, help='最大保留行数（默认200）')
    parser.add_argument('--annotate', nargs='+', metavar='TEXT', help='为文本添加标注')
    parser.add_argument('--path', help='指定记忆文件路径')
    
    args = parser.parse_args()
    
    manager = TieredMemoryManager()
    
    if args.load or args.evict:
        manager.load_memory(args.path)
        print(manager.report())
    
    if args.evict:
        result = manager.evict(limit_lines=args.limit, dry_run=args.dry_run)
        
        print("\n" + "=" * 50)
        print("🏷️ 淘汰结果")
        print("=" * 50)
        print(f"模式: {'预览' if result['dry_run'] else '执行'}")
        print(f"淘汰: P1={result['evicted_count']['P1']}, P2={result['evicted_count']['P2']}")
        print(f"剩余: {result['remaining']} 条")
        print(f"归档目录: {result['archive_dir']}")
        
        if result['dry_run']:
            print("\n💡 使用 --evict --no-dry-run 执行实际淘汰")
    
    if args.annotate:
        content = ' '.join(args.annotate)
        annotated = manager.annotate_existing(content)
        print("\n🏷️ 标注结果:")
        print(annotated)


if __name__ == '__main__':
    main()
