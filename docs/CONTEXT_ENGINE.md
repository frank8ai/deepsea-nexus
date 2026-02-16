# Context Engine v3.1 - 智能上下文引擎

## 概述

`Context Engine` 是 Deep-Sea Nexus v3.1 的核心子功能，整合了所有智能上下文相关代码。

## 文件结构

```
deepsea-nexus/
├── plugins/
│   ├── context_engine.py    🆕 统一的智能上下文引擎
│   ├── nexus_core.py         # 语义搜索
│   ├── session_manager.py   # 会话管理
│   └── flush_manager.py      # 自动清理
├── auto_summary.py           # 保留（向后兼容）
├── context_injector.py       # 保留（兼容回退）
└── layered_storage.py        # 保留（依赖）
```

## 核心功能

### 1. 结构化摘要 (StructuredSummary)

```python
from deepsea_nexus import StructuredSummary

summary = StructuredSummary(
    core_output="解决装饰器内存泄漏问题",
    tech_points=["闭包", "WeakRef", "装饰器"],
    code_pattern="def decorator():...",
    decision_context="因为调用时机不可控",
    pitfall_record="不要持有大对象引用",
    applicable_scene="装饰器需要缓存时",
    search_keywords=["python", "内存", "装饰器"],
    project关联="OpenClaw 优化",
    confidence="high"
)
```

### 2. 摘要解析 (SummaryParser)

```python
from deepsea_nexus import SummaryParser, parse_summary

reply, summary = parse_summary(llm_response)
# 支持 JSON 格式和旧格式
```

### 3. 上下文注入

```python
from deepsea_nexus import ContextEnginePlugin

# 检测触发词
result = engine.detect_trigger("还记得上次说的X吗?")
if result:
    # 检索相关历史
    history = engine.resolve_reference(result['query'])
```

### 4. 关键词注入

```python
# 自动提取关键词并检索
keywords = engine.extract_keywords(conversation)
related = engine.inject_keywords(conversation)
```

## 向后兼容

| 旧模块 | 新位置 | 状态 |
|--------|--------|------|
| `auto_summary.py` | → `plugins/context_engine.py` | ✅ 保留 |
| `context_injector.py` | → `plugins/context_engine.py` | ✅ 保留（含 compat 回退） |
| `layered_storage.py` | 保持独立 | ✅ 保留 |

## 使用方式

### 新 API (推荐)
```python
from deepsea_nexus import create_app, ContextEnginePlugin

app = create_app()
await app.initialize()

# 注册上下文引擎
app.registry.register(ContextEnginePlugin())
```

### 便捷函数
```python
from deepsea_nexus import (
    parse_summary,      # 解析摘要
    create_summary_prompt,  # 生成提示词
    StructuredSummary,   # 数据类
)
```

## 与现有代码的关系

```
ContextEnginePlugin (plugins/context_engine.py)
    ├── StructuredSummary  ← auto_summary.py
    ├── SummaryParser    ← auto_summary.py
    ├── detect_trigger() ← context_injector.py
    ├── resolve_reference() ← context_injector.py
    ├── extract_keywords()  ← context_injector.py
    └── inject_keywords() ← context_injector.py
```

## 集成到插件系统

```python
# 在 app.py 中注册
plugins = [
    ContextEnginePlugin(),  # 智能上下文
    NexusCorePlugin(),     # 语义搜索
    SessionManagerPlugin(), # 会话管理
    FlushManagerPlugin(),  # 自动清理
]
```

---

*版本: 3.1.0 | 整合日期: 2026-02-13*
