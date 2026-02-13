---
name: deepsea-nexus-v3
description: Deep-Sea Nexus v3.2 - Token 优化版 | 分层加载架构 | AI Agent 长期记忆系统
version: 3.2.0
---

# Deep-Sea Nexus v3.2 🧠

**Token 优化版 - 分层加载架构**

> 每轮 System Prompt 从 9.5K 降至 3K，成本降低 68%

## ⚡ 快速开始

```python
# 初始化（仅加载常驻层 ~3K tokens）
from deepsea_nexus import Nexus
nexus = Nexus()

# 语义检索（自动加载按需层）
results = nexus.recall("Python 装饰器", limit=5)

# 添加记忆
nexus.add("今天学习了装饰器", tags="python")
```

## 🎯 核心能力

| 能力 | 命令 | 按需层 |
|------|------|--------|
| 语义检索 | `nexus.recall()` | `semantic_search` |
| 添加记忆 | `nexus.add()` | `memory_management` |
| 会话管理 | `nexus.session.*` | `session_management` |
| 自动归档 | `nexus.flush.*` | `flush_management` |

## 🔗 按需加载规则

- **路由表**: 常驻层，知道自己有哪些能力
- **详细规则**: 按需层，用时再加载
- **缓存**: 常用配置 LRU 缓存，TTL 300s

## 📁 项目结构

```
deepsea-nexus-v3.0/
├── core/              # 核心组件
├── resident/          # 常驻层配置 (~3K)
├── on_demand/         # 按需层配置 (~6K)
└── docs/              # 文档
```

---
*Version: 3.2.0 | Architecture: Layered Loading*
