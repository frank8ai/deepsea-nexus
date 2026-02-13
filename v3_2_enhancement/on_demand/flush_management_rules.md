# Flush Management Rules - 自动归档详细规则 (F5)
# 按需层 - 执行归档操作时加载

## 概述

Flush 系统负责自动归档和清理旧会话，保持系统轻量。

## 触发条件

| 条件 | 触发时间 | 保留策略 |
|------|---------|---------|
| 30天不活跃 | 每日 03:00 | 归档保留90天 |
| 手动触发 | 立即执行 | 同上 |
| 容量告警 | 存储 > 80% | 清理最旧会话 |

## API 使用

### FlushManager

```python
from flush_manager import FlushManager
from session_manager import SessionManager

manager = SessionManager()
flush_mgr = FlushManager()

# 预览归档（干跑）
preview = flush_mgr.manual_flush(manager, dry_run=True)
print(f"将归档 {preview['sessions_to_archive']} 个会话")

# 执行归档
result = flush_mgr.daily_flush(manager)
print(f"归档完成: {result}")

# 清理旧归档
cleanup = flush_mgr.cleanup_old_archives()
print(f"清理了 {cleanup['deleted_count']} 个旧归档")
```

## 归档标准

### 自动归档条件

```python
def should_archive(session):
    return (
        session.last_active < now - 30_days
        and session.chunk_count >= 5  # 只归档有实质内容的
    )
```

### 清理标准

```python
def should_cleanup(archive):
    return archive.created_at < now - 90_days
```

## Cron 配置

```bash
# 添加每日 Flush 任务
openclaw cron add \
  --name "daily-flush" \
  --schedule "0 3 * * *" \
  --message "执行每日Flush：检查30天前会话，归档到 memory/archive/" \
  --session-target isolated
```

## 归档结构

```
memory/
├── archive/
│   ├── 2026-01/
│   │   └── session_0101_OldTopic.md
│   └── 2026-02/
│       └── session_0131_AnotherOld.md
└── sessions.db  # 元数据保留
```

## 恢复归档

```python
# 从归档恢复
from flush_manager import FlushManager

flush_mgr = FlushManager()
flush_mgr.restore_from_archive(
    archive_path="memory/archive/2026-01/session_0101_OldTopic.md",
    target_date="2026-02-13"
)
```

## 统计信息

Flush 执行后会返回统计：

```python
{
    "archived_count": 5,
    "archived_sessions": ["id1", "id2", ...],
    "skipped_count": 2,
    "skipped_sessions": ["id3", "id4"],
    "errors": []
}
```

## 监控与告警

### 容量监控

```python
# 检查存储使用率
stats = nexus_stats()
if stats['document_count'] > 5000:
    print("⚠️ 建议执行清理")
```

### 健康检查

```bash
# 每周检查
python3 -c "
from nexus_core import nexus_stats
stats = nexus_stats()
print(f'文档数: {stats[\"document_count\"]}')
print(f'存储大小: {stats[\"storage_size\"]}')
"
```

## 最佳实践

1. **每日自动 Flush**: 设置 cron 任务
2. **定期检查**: 每周检查向量库健康
3. **及时清理**: 不要等存储告警再处理
4. **保留重要会话**: P0/P1 标签的会话考虑手动保留
