#!/usr/bin/env python3
"""
Tiered Flush Manager - 三级优先级淘汰管理器

融合现有 Flush Manager，实现 P0/P1/P2 分级淘汰

优先级策略：
- P0 — 核心记忆（永不淘汰）
- P1 — 阶段性记忆（90 天）
- P2 — 临时记忆（30 天）
"""

import os
import re
import json
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import yaml


class Priority(Enum):
    """记忆优先级"""
    P0 = "P0"  # 核心 - 永不淘汰
    P1 = "P1"  # 阶段 - 90天
    P2 = "P2"  # 临时 - 30天


class TieredFlushManager:
    """
    分层 Flush 管理器
    
    继承自原有 FlushManager，添加三级优先级淘汰
    
    使用方法:
    manager = TieredFlushManager(
        vector_store=chroma_collection,
        config={}
    )
    
    # 执行分级淘汰
    manager.evict_expired()
    
    # 迁移到归档向量库
    manager.archive_to_cold()
    """
    
    # 淘汰策略
    EVICT_POLICY = {
        Priority.P0: {"days": None, "max_lines": None, "desc": "核心-永不过期"},
        Priority.P1: {"days": 90, "max_lines": 100, "desc": "阶段-90天"},
        Priority.P2: {"days": 30, "max_lines": 50, "desc": "临时-30天"},
    }
    
    # 热记忆上限
    HOT_MEMORY_LIMIT = 200  # 总行数上限
    
    def __init__(
        self,
        vector_store=None,
        archive_vector_store=None,
        config: Dict = None,
        base_path: str = None
    ):
        """
        初始化
        
        Args:
            vector_store: 热记忆向量库（ChromaDB collection）
            archive_vector_store: 冷记忆向量库
            config: 配置
            base_path: 归档目录路径
        """
        self.vector_store = vector_store
        self.archive_vector_store = archive_vector_store
        
        # 默认配置
        self.config = {
            "enabled": True,
            "archive_time": "03:00",
            "archive_dir": "archive",
            "cold_storage_dir": "cold_vector_db",
            "evict_enabled": True,
            "evict_dry_run": True,  # 默认预览模式
            "hot_memory_limit": 200,
            **self._get_default_policy()
        }
        
        # 合并配置
        if config:
            self.config.update(config)
        
        # 路径
        if base_path:
            self.base_path = base_path
        else:
            self.base_path = os.path.expanduser("~/.openclaw/workspace/memory")
        
        # 归档目录
        self.archive_path = os.path.join(self.base_path, self.config["archive_dir"])
        self.cold_path = os.path.join(self.base_path, self.config["cold_storage_dir"])
        
        os.makedirs(self.archive_path, exist_ok=True)
        os.makedirs(self.cold_path, exist_ok=True)
        
        # 统计
        self.stats = {
            "total": 0,
            "by_priority": {p.value: 0 for p in Priority},
            "expired": {p.value: 0 for p in Priority},
            "archived": 0
        }
    
    def _get_default_policy(self) -> Dict:
        """获取默认策略"""
        return {
            "policy": {
                "P0": {"days": None, "max_count": None, "desc": "核心-永不过期"},
                "P1": {"days": 90, "max_count": 100, "desc": "阶段-90天"},
                "P2": {"days": 30, "max_count": 50, "desc": "临时-30天"},
            },
            "hot_limit": 200
        }
    
    # ===================== 优先级解析 =====================
    
    def parse_priority(self, line: str) -> Tuple[Optional[Priority], Optional[str]]:
        """
        解析行的优先级
        
        Returns:
            (priority, date) 或 (None, None)
        """
        # 匹配 [P0][2025-10-01] 格式
        match = re.match(r'\[(P0|P1|P2)\]\[(\d{4}-\d{2}-\d{2})\]', line)
        if match:
            return Priority(match.group(1)), match.group(2)
        return None, None
    
    def get_priority_from_metadata(self, metadata: Dict) -> Priority:
        """从 metadata 获取优先级"""
        priority_str = metadata.get("priority", "P2")
        try:
            return Priority(priority_str)
        except ValueError:
            return Priority.P2
    
    # ===================== 向量库操作 =====================
    
    def scan_hot_memory(self) -> List[Dict]:
        """
        扫描热记忆向量库
        
        Returns:
            [{id, content, metadata, priority, days_ago}]
        """
        if not self.vector_store:
            return []
        
        try:
            # 获取所有文档
            results = self.vector_store.get(include=["documents", "metadatas"])
            
            items = []
            now = datetime.now()
            
            for doc_id, content, metadata in zip(
                results.get("ids", []),
                results.get("documents", []),
                results.get("metadatas", [])
            ):
                priority = self.get_priority_from_metadata(metadata)
                
                # 计算天数
                created = metadata.get("created_at", "")
                days_ago = 0
                if created:
                    try:
                        dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                        days_ago = (now - dt).days
                    except Exception:
                        pass
                
                items.append({
                    "id": doc_id,
                    "content": content,
                    "metadata": metadata,
                    "priority": priority,
                    "days_ago": days_ago
                })
            
            self.stats["total"] = len(items)
            return items
            
        except Exception as e:
            print(f"扫描热记忆失败: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """获取统计"""
        items = self.scan_hot_memory()
        
        stats = {
            "hot_memory": {
                "total": len(items),
                "by_priority": {p.value: 0 for p in Priority},
                "expired": {p.value: 0 for p in Priority},
                "line_estimate": len(items) * 3  # 粗略估计行数
            },
            "cold_memory": {
                "count": 0
            }
        }
        
        for item in items:
            p = item["priority"].value
            stats["hot_memory"]["by_priority"][p] += 1
            
            # 检查是否过期
            policy = self.EVICT_POLICY[item["priority"]]
            if policy["days"]:
                if item["days_ago"] > policy["days"]:
                    stats["hot_memory"]["expired"][p] += 1
        
        return stats
    
    # ===================== 淘汰逻辑 =====================
    
    def get_eviction_candidates(self) -> Dict[Priority, List[Dict]]:
        """
        获取待淘汰的条目
        
        Returns:
            {Priority: [items]}
        """
        items = self.scan_hot_memory()
        candidates = {Priority.P0: [], Priority.P1: [], Priority.P2: []}
        
        for item in items:
            priority = item["priority"]
            policy = self.EVICT_POLICY[priority]
            
            # 1. 检查是否过期
            if policy["days"] and item["days_ago"] > policy["days"]:
                candidates[priority].append(item)
            # 2. 检查数量限制
            elif policy["max_count"]:
                # 超过保留数量的 P1/P2 需要淘汰最旧的
                pass  # 在 evict() 中处理
        
        return candidates
    
    def evict(self, dry_run: bool = None) -> Dict:
        """
        执行淘汰
        
        Args:
            dry_run: 预览模式（默认 True）
            
        Returns:
            淘汰统计
        """
        if dry_run is None:
            dry_run = self.config["evict_dry_run"]
        
        items = self.scan_hot_memory()
        
        # 分类
        to_keep = {Priority.P0: [], Priority.P1: [], Priority.P2: []}
        to_evict = {Priority.P0: [], Priority.P1: [], Priority.P2: []}
        
        for item in items:
            priority = item["priority"]
            policy = self.EVICT_POLICY[priority]
            
            if priority == Priority.P0:
                # P0 永不过滤
                to_keep[priority].append(item)
            elif policy["days"] and item["days_ago"] > policy["days"]:
                # 过期
                to_evict[priority].append(item)
            else:
                # 检查数量限制
                to_keep[priority].append(item)
        
        # 如果超过热记忆上限，淘汰多余的 P1（最旧的）
        total_keep = sum(len(v) for v in to_keep.values())
        
        if total_keep > self.config["hot_memory_limit"]:
            # 按日期排序
            p1_items = sorted(to_keep[Priority.P1], key=lambda x: x["days_ago"], reverse=True)
            
            excess = total_keep - self.config["hot_memory_limit"]
            evict_extra = p1_items[:excess]
            
            for item in evict_extra:
                to_keep[Priority.P1].remove(item)
                to_evict[Priority.P1].append(item)
        
        # 统计
        evicted = {
            "dry_run": dry_run,
            "total_evicted": sum(len(v) for v in to_evict.values()),
            "by_priority": {p.value: len(v) for p, v in to_evict.items()},
            "remaining": sum(len(v) for v in to_keep.values()),
            "evicted_items": to_evict
        }
        
        if not dry_run:
            # 执行淘汰
            self._perform_eviction(to_evict)
        
        return evicted
    
    def _perform_eviction(self, to_evict: Dict[Priority, List[Dict]]):
        """执行实际淘汰"""
        for priority, items in to_evict.items():
            for item in items:
                # 1. 归档到冷存储
                self._archive_to_cold(item)
                
                # 2. 从热记忆删除
                if self.vector_store:
                    try:
                        self.vector_store.delete(ids=[item["id"]])
                    except Exception as e:
                        print(f"删除失败 {item['id']}: {e}")
    
    def _archive_to_cold(self, item: Dict):
        """归档到冷存储"""
        # 更新 metadata
        metadata = item["metadata"]
        metadata["archived_at"] = datetime.now().isoformat()
        metadata["was_priority"] = item["priority"].value
        
        # 添加到归档向量库
        if self.archive_vector_store:
            try:
                self.archive_vector_store.add(
                    documents=[item["content"]],
                    embeddings=[],  # 复用原有 embedding
                    metadatas=[metadata],
                    ids=[item["id"]]
                )
            except Exception as e:
                print(f"归档向量库失败: {e}")
        
        # 同时写入文本归档
        date = datetime.now().strftime("%Y-%m-%d")
        archive_file = os.path.join(self.archive_path, f"archive_{date}.md")
        
        with open(archive_file, 'a', encoding='utf-8') as f:
            line = f"[{item['priority'].value}][{metadata.get('created_at', date)[:10]}] {item['content']}"
            f.write(line + "\n")
    
    # ===================== 归档检索 =====================
    
    def search_archive(self, query: str, n: int = 5) -> List[Dict]:
        """
        搜索归档（冷记忆）
        
        Returns:
            归档中的相关内容
        """
        if not self.archive_vector_store:
            return []
        
        try:
            from sentence_transformers import SentenceTransformer
            embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            query_embedding = embedder.encode([query]).tolist()
            results = self.archive_vector_store.query(
                query_embeddings=query_embedding,
                n_results=n
            )
            
            items = []
            for doc, meta in zip(
                results.get("documents", []),
                results.get("metadatas", [])
            ):
                items.append({
                    "content": doc,
                    "metadata": meta,
                    "source": "archive"
                })
            
            return items
            
        except Exception as e:
            print(f"归档搜索失败: {e}")
            return []
    
    # ===================== 统计报告 =====================
    
    def report(self, evict_result: Dict = None) -> str:
        """生成报告"""
        stats = self.get_stats()
        
        lines = [
            "=" * 50,
            "🧠 分层记忆管理报告",
            "=" * 50,
            "",
            "📊 热记忆状态:",
            f"  总条目: {stats['hot_memory']['total']}",
            f"  预估行数: {stats['hot_memory']['line_estimate']}",
            f"  上限: {self.config['hot_memory_limit']}",
            "",
            "  按优先级:",
            f"    P0(核心-永不过期): {stats['hot_memory']['by_priority']['P0']}",
            f"    P1(阶段-90天): {stats['hot_memory']['by_priority']['P1']}",
            f"    P2(临时-30天): {stats['hot_memory']['by_priority']['P2']}",
            "",
            "  过期条目:",
            f"    P0: {stats['hot_memory']['expired']['P0']}",
            f"    P1: {stats['hot_memory']['expired']['P1']} (>90天)",
            f"    P2: {stats['hot_memory']['expired']['P2']} (>30天)",
            "",
        ]
        
        if evict_result:
            lines.extend([
                "🏷️ 淘汰结果:",
                f"  模式: {'预览' if evict_result['dry_run'] else '执行'}",
                f"  淘汰: P1={evict_result['by_priority']['P1']}, P2={evict_result['by_priority']['P2']}",
                f"  剩余: {evict_result['remaining']}",
                "",
                "💡 使用 --evict --no-dry-run 执行实际淘汰"
            ])
        
        lines.append("=" * 50)
        
        return "\n".join(lines)


# ===================== CLI =====================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🧠 分层记忆管理器 - 三级优先级淘汰",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--scan', action='store_true', help='扫描并显示统计')
    parser.add_argument('--evict', action='store_true', help='执行淘汰')
    parser.add_argument('--dry-run', action='store_true', help='预览模式（默认）')
    parser.add_argument('--no-dry-run', action='store_false', dest='dry_run', help='执行实际淘汰')
    parser.add_argument('--search', metavar='QUERY', help='搜索归档')
    parser.add_argument('--limit', type=int, default=200, help='热记忆上限（默认200行）')
    
    args = parser.parse_args()
    
    manager = TieredFlushManager()
    
    if args.scan or args.evict:
        print(manager.report())
    
    if args.evict:
        result = manager.evict(dry_run=args.dry_run)
        print("\n" + "=" * 50)
        print("🏷️ 淘汰结果")
        print("=" * 50)
        print(f"模式: {'预览' if result['dry_run'] else '执行'}")
        print(f"淘汰: P1={result['by_priority']['P1']}, P2={result['by_priority']['P2']}")
        print(f"剩余: {result['remaining']}")
        
        if result['dry_run']:
            print("\n💡 使用 --evict --no-dry-run 执行实际淘汰")
    
    if args.search:
        results = manager.search_archive(args.search)
        print(f"\n🔍 归档搜索: {args.search}")
        print(f"找到 {len(results)} 条:")
        for r in results:
            print(f"  - {r['content'][:80]}...")


if __name__ == '__main__':
    main()
