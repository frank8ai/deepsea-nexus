# Deep-Sea Nexus v2.0

> AI Agent 长期记忆系统 | 极轻量 | 按需加载 | 零依赖

## 核心特性

| 特性 | 指标 | 说明 |
|------|------|------|
| 启动加载 | < 300 tokens | 只读索引 |
| 每轮对话 | < 1000 tokens | 按需加载 |
| 召回延迟 | < 100ms | 关键词搜索 |
| 零依赖 | 纯 Python | 标准库实现 |

## 快速开始

```bash
cd ~/.openclaw/workspace/DEEP_SEA_NEXUS_V2

# 初始化
python src/nexus_core.py --init

# 创建会话
python src/nexus_core.py --session "Python学习"

# 写入内容
python src/nexus_core.py --write "今天学习列表推导式"

# 召回记忆
python src/nexus_core.py --recall "列表"

# 查看索引
python src/nexus_core.py --index
```

## Python API

```python
from src.nexus_core import NexusCore

nexus = NexusCore()

# 创建会话
session_id = nexus.start_session("话题名称")

# 写入内容（支持 #GOLD 标记）
nexus.write_session(session_id, "关键信息", is_gold=True)

# 召回记忆
results = nexus.recall("搜索词")

# 每日 Flush
stats = nexus.daily_flush()
```

## 工具脚本

```bash
# 分割大文件
python scripts/session_split.py --scan

# 重建索引
python scripts/index_rebuild.py --all

# 迁移 v1.0
python scripts/migrate.py --source /path/to/v1 --verify
```

## 目录结构

```
DEEP_SEA_NEXUS_V2/
├── src/
│   ├── nexus_core.py      # 核心引擎
│   ├── config.py          # 配置管理
│   ├── data_structures.py  # 数据结构
│   ├── exceptions.py      # 异常定义
│   ├── lock.py            # 文件锁
│   └── logger.py          # 日志系统
├── scripts/
│   ├── session_split.py    # 会话分割
│   ├── index_rebuild.py   # 索引重建
│   └── migrate.py         # v1.0 迁移
├── tests/
│   ├── test_core.py       # 单元测试
│   └── conftest.py        # 测试配置
├── docs/
│   ├── PRD.md             # 产品规格
│   └── TASK_LIST.md       # 任务清单
└── memory/
    └── 90_Memory/         # 记忆存储
```

## 集成到 OpenClaw

修改 `~/.openclaw/workspace/AGENTS.md`:

```markdown
# Deep-Sea Nexus v2.0 集成

## 启动规则
1. 启动时只读 `_DAILY_INDEX.md`
2. 不加载任何 Session 历史

## 对话规则
1. 用户提问时调用 `nexus.recall(query)`
2. 只加载相关内容 (< 500 tokens)
3. 不注入完整上下文

## 写入规则
1. 关键信息添加 `#GOLD` 标记
2. 每次交互后调用 `nexus.write_session()`
```

## 性能基准

| 场景 | 指标 | 状态 |
|------|------|------|
| 启动 | < 1s | ✅ |
| 索引 | < 300t | ✅ |
| 召回 | < 100ms | ✅ |
| 并发 | 文件锁 | ✅ |

## 许可证

MIT
