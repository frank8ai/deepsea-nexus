# Semantic Search Rules - 语义搜索详细规则
# 按需层 - 执行语义检索时加载

## 工作原理

使用 all-MiniLM-L6-v2 嵌入模型 (384维)，将文本转换为向量存储在 ChromaDB 中。
检索时计算查询向量与文档向量的余弦相似度，返回最相关的结果。

## API 使用

### 基本检索

```python
from nexus_core import nexus_recall

results = nexus_recall("如何配置 Telegram bot", limit=5)

for r in results:
    print(f"[{r.relevance:.2f}] {r.source}")
    print(f"{r.content[:200]}...")
```

### 高级检索

```python
from nexus_core import nexus_advanced_recall

results = nexus_advanced_recall(
    query="项目配置",
    filters={"tags": ["project", "config"]},
    limit=5,
    min_relevance=0.7
)
```

## 结果解读

| 相关性分数 | 含义 | 建议 |
|-----------|------|------|
| 0.8+ | 高度相关 | 优先使用 |
| 0.6-0.8 | 相关 | 结合上下文判断 |
| 0.4-0.6 | 弱相关 | 仅供参考 |
| <0.4 | 不相关 | 忽略 |

## 最佳实践

1. **查询要具体**: "Python 列表推导式" 比 "Python" 效果好
2. **使用标签过滤**: 减少无关结果
3. **合理设置 limit**: 通常 3-5 条足够
4. **检查相关性**: 不要盲目相信低分结果

## 故障排查

### 检索无结果

```python
# 检查向量库状态
from nexus_core import nexus_stats
print(nexus_stats())

# 重建索引
from vector_store import rebuild_index
rebuild_index()
```

### 结果不相关

- 尝试更具体的查询
- 检查文档是否已索引
- 考虑调整 min_relevance 阈值
