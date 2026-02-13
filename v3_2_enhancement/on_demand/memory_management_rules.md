# Memory Management Rules - 记忆管理详细规则
# 按需层 - 添加/更新记忆时加载

## 核心功能

添加新记忆到向量库，支持多种格式和标签系统。

## API 使用

### 添加单条记忆

```python
from nexus_core import nexus_add

nexus_add(
    content="今天学习了 Python 的装饰器用法",
    title="Python 装饰器学习",
    tags="python, learning"
)
```

### 批量添加文档

```python
from nexus_core import nexus_add_documents

docs = [
    {"content": "...", "title": "...", "tags": "..."},
    {"content": "...", "title": "...", "tags": "..."},
]
nexus_add_documents(docs, batch_size=100)
```

### 添加结构化摘要 (v3.0)

```python
from nexus_core import nexus_add_structured_summary

nexus_add_structured_summary(
    core_output="解决了内存泄漏问题",
    tech_points=["弱引用", "闭包"],
    code_pattern="WeakValueDictionary()",
    decision_context="装饰器调用时机不可控",
    pitfalls="不要持有大对象引用",
    applicable_scenes="装饰器缓存场景",
    keywords=["python", "内存泄漏"],
    project="OpenClaw",
    confidence="high"
)
```

## 标签系统

### 标签格式

```python
# ✅ 正确：逗号分隔的字符串
tags="python, learning, decorator"

# ❌ 错误：列表
tags=["python", "learning"]
```

### 推荐标签

| 场景 | 标签 |
|------|------|
| 编程学习 | python, learning, cs50 |
| 项目配置 | project, config, openclaw |
| 错误排查 | bug, fix, debug |
| 架构设计 | architecture, design |

## 优先级标记

在内容中使用优先级标签：

```markdown
#GOLD 这是关键洞察 - 永久保留，检索权重提升
#P0 核心信息 - 90天保留
#P1 项目信息 - 30天保留
#P2 临时信息 - 7天保留
```

## 注意事项

1. **内容长度**: 建议控制在 500-2000 字符
2. **标题清晰**: 便于后续检索识别
3. **标签准确**: 影响过滤效果
4. **避免重复**: 检索后再添加，防止重复

## 故障排查

### 添加失败

- 检查标签格式（字符串而非列表）
- 确认向量库连接正常
- 检查内容是否为空

### 重复添加

```python
# 先检索检查
existing = nexus_recall(content[:100], limit=3)
if not existing or existing[0].relevance < 0.95:
    nexus_add(content, title, tags)
```
