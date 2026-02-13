# Summary Generation Rules - 智能摘要详细规则
# 按需层 - 生成对话摘要时加载

## 工作原理

```
用户输入 → LLM 生成回复 → 解析摘要格式 → 混合存储 → 向量检索
```

## 摘要格式 v3.0

### 结构化摘要（推荐）

```json
{
  "本次核心产出": "一句话说明这次解决了什么问题",
  "技术要点": ["关键点1", "关键点2"],
  "代码模式": "提取的可复用代码片段（如果有）",
  "决策上下文": "为什么选择这个方案",
  "避坑记录": "应避免的错误/弯路",
  "适用场景": "这个方案适用的场景",
  "搜索关键词": ["标签1", "标签2"],
  "项目关联": "所属项目（可选）",
  "置信度": "high/medium/low"
}
```

### 简洁摘要（兼容旧版）

```markdown
[你的完整回复]

---SUMMARY---
[1-2句话总结核心要点]
---END---
```

## 字段填写指南

| 字段 | 要求 | 示例 |
|------|------|------|
| `本次核心产出` | 具体可操作 | "解决了 Python 装饰器循环引用导致的内存泄漏" |
| `技术要点` | 3-5 个关键词 | `["__closure__", "弱引用", "装饰器执行顺序"]` |
| `代码模式` | 可复用的代码片段 | `def decorator(func): ...` |
| `决策上下文` | 为什么选这个方案 | "选择 WeakValueDictionary 而非手动清理..." |
| `避坑记录` | 必须避免的错误 | "装饰器不要在闭包中持有大对象引用" |
| `适用场景` | 什么时候能用 | "装饰器需要缓存且生命周期不确定时" |
| `搜索关键词` | 便于检索的标签 | `["python", "装饰器", "内存泄漏", "闭包"]` |
| `项目关联` | 所属项目 | "OpenClaw 内存优化" |
| `置信度` | 对摘要质量的评估 | `high` / `medium` / `low` |

## API 使用

### 处理并存储

```python
from auto_summary import HybridStorage
from nexus_core import nexus_init

nexus_init()
storage = HybridStorage(nexus)

result = storage.process_and_store(
    conversation_id='session_001',
    response="""
    今天我们讨论了 OpenClaw 的配置问题。
    主要是 Telegram bot token 的配置方法。
    
    ```json
    {
      "本次核心产出": "讨论了 Telegram bot 配置方法",
      "技术要点": ["botToken", "channels.telegram"],
      "搜索关键词": ["openclaw", "telegram", "配置"],
      "置信度": "high"
    }
    ```
    """,
    user_query="如何配置 Telegram bot？"
)
print(f"存储了 {result['stored_count']} 条")
```

### 添加结构化摘要

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

## 存储结构

| 类型 | 存储位置 | 用途 |
|------|---------|------|
| **摘要** | 向量库 (ChromaDB) | 语义检索 |
| **原文** | sessions.db | 完整回溯 |
| **关联** | metadata | 会话链接 |

## 质量检查清单

在生成摘要前，问自己：

1. ✅ **核心产出** - 这段对话解决了什么具体问题？
2. ✅ **可复用** - 这个信息未来什么时候能用上？
3. ✅ **避免重复** - 如果不说这段，未来会踩什么坑？
4. ✅ **精准检索** - 用什么关键词能精准搜到这个信息？

## 好 vs 不好的摘要

### ✅ 好的示例

```json
{
  "本次核心产出": "解决了 Python 装饰器循环引用导致的内存泄漏问题",
  "技术要点": ["__closure__ 闭包机制", "弱引用", "装饰器执行顺序"],
  "代码模式": "def create_decorator():\n    cache = {}\n    def decorator(func): ...",
  "决策上下文": "选择 WeakValueDictionary 而非手动清理，是因为装饰器调用时机不可控",
  "避坑记录": "装饰器不要在闭包中持有大对象引用，会导致内存泄漏",
  "适用场景": "装饰器需要缓存且装饰对象生命周期不确定时",
  "搜索关键词": ["python", "装饰器", "内存泄漏", "闭包", "WeakRef"],
  "项目关联": "OpenClaw 内存优化",
  "置信度": "high"
}
```

### ❌ 不好的示例

```json
{
  "本次核心产出": "学习了 Python 装饰器",
  "技术要点": ["装饰器是 Python 的特性"],
  "代码模式": "无",
  "决策上下文": "无",
  "避坑记录": "无",
  "适用场景": "使用装饰器时",
  "搜索关键词": ["python", "装饰器"],
  "项目关联": "",
  "置信度": "low"
}
```

## 自动触发

以下情况自动保存摘要：

1. 收到"切换话题"指令时
2. 每50条消息时主动检查
3. 上下文快满4000 tokens前
4. 检测到 #GOLD 标记时
5. 收到"记住..."指令时
