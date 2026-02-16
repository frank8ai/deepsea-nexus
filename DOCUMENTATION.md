# Deep-Sea Nexus v2.3 详细技术文档

> AI Agent 长期记忆系统 | 向量存储 | 智能上下文 | RAG 召回

## 目录

1. [系统架构](#系统架构)
2. [核心模块](#核心模块)
3. [依赖关系](#依赖关系)
4. [API 参考](#api-参考)
5. [使用示例](#使用示例)
6. [故障排查](#故障排查)
7. [更新日志](#更新日志)

---

## 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                  Deep-Sea Nexus v2.3                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                   对话层                              │ │
│  │  • context_injector.py (上下文注入)                  │ │
│  │  • nexus_autoinject.py (智能注入)                   │ │
│  │  • auto_summary.py (智能摘要)                       │ │
│  └─────────────────────────────────────────────────────┘ │
│                              ↓                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                   核心层                            │ │
│  │  • nexus_core.py (核心引擎)                       │ │
│  │  • auto_recall.py (自动召回)                       │ │
│  │  • session_manager.py (会话管理)                   │ │
│  │  • flush_manager.py (自动Flush)                   │ │
│  └─────────────────────────────────────────────────────┘ │
│                              ↓                            │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                   存储层                            │ │
│  │  • vector_store.py (向量存储)                      │ │
│  │  • .vector_db_final/ (ChromaDB)                   │ │
│  │  • memory/ (文件存储)                             │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 数据流

```
用户输入 → 触发词检测 → 关键词提取 → 向量搜索 → 上下文注入 → AI 回复
                                                    ↓
                                             摘要生成 → 向量存储
```

---

## 核心模块

### 1. nexus_core.py ⭐ 核心引擎

**功能**: 向量检索和 RAG 召回

**状态**: ✅ 正常

**主要类**:

```python
class NexusCore:
    """Deep-Sea Nexus 核心类"""
    
    def __init__(self):
        self.recall = None      # 语义检索
        self.manager = None     # 向量管理
        self.store = None      # 向量存储
    
    def recall(self, query: str, n: int = 5) -> List[RecallResult]:
        """语义搜索"""
        
    def add(self, content: str, title: str, tags: str):
        """添加记忆"""
```

**导出函数**:

```python
def nexus_init(blocking: bool = False):
    """初始化系统"""
    
def nexus_add(content: str, title: str, tags: str) -> str:
    """添加记忆"""
    
def nexus_recall(query: str, n: int = 5) -> List[RecallResult]:
    """语义搜索"""
    
def nexus_stats() -> Dict:
    """获取统计"""
```

**使用示例**:

```python
from nexus_core import nexus_init, nexus_add, nexus_recall

# 初始化
nexus_init(blocking=True)

# 添加记忆
result = nexus_add(
    content="学习 Python 列表推导式",
    title="Python学习",
    tags="python,learning"
)
print(f"添加成功: {result}")

# 搜索
results = nexus_recall("Python", 5)
for r in results:
    print(f"[{r.relevance:.2f}] {r.content[:100]}...")
```

---

### 2. auto_summary.py ⭐ 智能摘要

**功能**: 从 AI 回复中解析和提取摘要

**状态**: ✅ 正常

**主要类**:

```python
class SummaryParser:
    """摘要解析器"""
    
    # 支持的格式
    SUMMARY_PATTERNS = [
        r'## 📋 总结[^\n]*\n([\s\S]*?)(?=\n\n|$)',  # ## 📋 总结 格式
        r'---SUMMARY---\s*(.+?)\s*---END---',           # 旧格式
    ]
    
    @classmethod
    def parse(cls, response: str) -> tuple:
        """解析回复，提取摘要"""
        # Returns: (reply, summary)
        
    @classmethod
    def create_summary_prompt(cls, history: str) -> str:
        """生成摘要提示词"""


class HybridStorage:
    """混合存储管理器"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.parser = SummaryParser()
    
    def process_and_store(self, conversation_id: str, response: str) -> Dict:
        """处理并存储"""
```

**摘要格式**:

```markdown
[AI 回复内容]

## 📋 总结
- 要点1
- 要点2
- 要点3
```

**使用示例**:

```python
from auto_summary import SummaryParser, HybridStorage

# 解析摘要
response = """
这是 AI 的回复内容...

## 📋 总结
- 学习 Python 列表推导式
- 理解基本语法
- 实践应用示例
"""

reply, summary = SummaryParser.parse(response)
print("摘要:", summary)
```

---

### 3. context_injector.py ✅ 可用（已兼容）

**功能**: 上下文自动注入、触发词检测

**状态**: ✅ 可用（优先走 compat/插件链路，缺省回退 layered_storage）

**预期功能**:

```python
class ContextInjector:
    """上下文自动注入器"""
    
    TRIGGER_PATTERNS = [
        r'还记得(.+?)[吗?？]',      # 还记得X吗
        r'上次.*提到(.+)',         # 上次提到X
        r'之前.*讨论(.+)',         # 之前讨论X
        r'之前.*决定(.+)',         # 之前决定X
    ]
    
    def inject_on_resume(self, topic: str) -> ContextBundle:
        """会话恢复时注入上下文"""
        
    def detect_trigger(self, user_input: str) -> Optional[Dict]:
        """检测触发词"""
```

**问题**: 依赖 `layered_storage.py` 模块不存在

**解决方案**: 可直接使用 `context_injector.py`，也可用 `nexus_autoinject.py`

---

### 4. nexus_autoinject.py ✅ 可用（含兼容回退）

**功能**: 通过 socket 连接实现智能记忆注入

**状态**: ⚠️ 需要 nexus_warmup.sock 服务

**主要函数**:

```python
def smart_search(user_input: str, n: int = 3) -> Dict:
    """
    智能搜索
    
    Returns:
        {
            "triggered": bool,
            "trigger_pattern": str,
            "query": str,
            "keywords": List[str],
            "context": str,
            "results": List[Dict]
        }
    """

def detect_trigger(user_input: str) -> Optional[Dict]:
    """检测触发词"""

def extract_keywords(text: str, max_kw: int = 5) -> List[str]:
    """提取关键词"""
```

**触发词模式**:

```python
TRIGGER_PATTERNS = [
    (r'还记得(.+?)[吗?？]', "还记得...吗"),
    (r'上次.*提到(.+)', "上次提到"),
    (r'之前.*说过(.+)', "之前说过"),
    (r'之前.*讨论(.+)', "之前讨论"),
    (r'之前.*决定(.+)', "之前决定"),
    (r'前面.*内容(.+)', "前面内容"),
    (r'之前.*项目(.+)', "之前项目"),
    (r'上次.*对话(.+)', "上次对话"),
    (r'之前.*聊天(.+)', "之前聊天"),
]
```

**使用示例**:

```python
from nexus_autoinject import smart_search, detect_trigger

# 检测触发词
result = detect_trigger("还记得上次说的Python吗?")
if result:
    print(f"触发: {result['pattern']}")
    print(f"查询: {result['query']}")

# 智能搜索
result = smart_search("之前讨论的项目进度")
print(f"触发: {result['triggered']}")
print(f"上下文: {result['context']}")
```

---

### 5. auto_recall.py

**功能**: 自动检索相关记忆

**状态**: ✅ 正常

**主要函数**:

```python
def auto_recall(query: str, n: int = 5) -> List[Dict]:
    """
    自动检索
    
    Returns:
        List[{
            "content": str,
            "source": str,
            "relevance": float,
            "metadata": Dict
        }]
    """
```

---

### 6. session_manager.py

**功能**: 会话管理

**状态**: ✅ 正常

**主要类**:

```python
class SessionManager:
    """会话管理器"""
    
    def start_session(self, topic: str) -> str:
        """创建会话"""
        
    def get_session(self, session_id: str) -> Dict:
        """获取会话"""
        
    def close_session(self, session_id: str):
        """关闭会话"""
        
    def archive_session(self, session_id: str):
        """归档会话"""
```

---

### 7. flush_manager.py

**功能**: 自动 Flush 和归档

**状态**: ✅ 正常

**主要类**:

```python
class FlushManager:
    """Flush 管理器"""
    
    def daily_flush(self) -> Dict:
        """每日 Flush"""
        
    def flush_session(self, session_id: str) -> bool:
        """Flush 单个会话"""
```

---

### 8. hooks/hooks_system.py

**功能**: 事件驱动的 Hook 系统

**状态**: ✅ 存在（但 OpenClaw 不支持）

**Hook 类型**:

| 类型 | 触发时机 | 目录 |
|------|---------|------|
| pre-prompt | 用户提问前 | `pre-prompt/` |
| post-response | AI 回复后 | `post-response/` |
| tool-call | 工具调用时 | `tool-call/` |

**使用示例**:

```python
from hooks.hooks_system import HooksSystem

hooks = HooksSystem()
result = hooks.run_hooks("post-response", {"response": "AI 回复"})
print(result)
```

**注意**: OpenClaw 当前版本只支持 `command` 事件，`post-response` 事件不受支持。

---

## 依赖关系

```
                    ┌─────────────────┐
                    │   用户输入      │
                    └────────┬────────┘
                             ↓
            ┌────────────────┴────────────────┐
            ↓                                 ↓
    context_injector.py              nexus_autoinject.py
    (⚠️ 损坏)                        (⚠️ 需要 socket)
            ↓                                 ↓
    layered_storage.py              nexus_core.py ⭐
    (❌ 不存在)                           ↓
                                    vector_store.py
                                         ↓
                              .vector_db_final/
                              (ChromaDB)
```

---

## API 参考

### 快速 API（推荐）

```python
from nexus_core import nexus_init, nexus_add, nexus_recall

# 初始化
nexus_init(blocking=True)

# 添加
nexus_add(content, title, tags)

# 搜索
nexus_recall(query, n)

# 统计
nexus_stats()
```

### 高级 API

```python
# 摘要
from auto_summary import SummaryParser, HybridStorage
reply, summary = SummaryParser.parse(response)

# 触发词检测
from nexus_autoinject import detect_trigger, smart_search
result = detect_trigger(user_input)

# 会话管理
from session_manager import SessionManager
session_id = manager.start_session("话题")
```

---

## 使用示例

### 示例1: 保存对话摘要

```python
from nexus_core import nexus_add, nexus_init

nexus_init(blocking=True)

# 保存对话
nexus_add(
    content="今天学习了Python列表推导式。\
             列表推导式是创建列表的简洁方式。\
             例如：[x for x in range(10) if x % 2 == 0]",
    title="Python学习-列表推导式",
    tags="python,列表推导式,学习"
)
```

### 示例2: 检索相关记忆

```python
from nexus_core import nexus_recall

# 搜索
results = nexus_recall("Python 列表", 5)

for r in results:
    print(f"[{r.relevance:.2f}] {r.content[:100]}...")
    print(f"来源: {r.source}")
```

### 示例3: 检测触发词

```python
from nexus_autoinject import detect_trigger

# 检测
result = detect_trigger("还记得上次说的Python吗?")

if result:
    print(f"✅ 触发: {result['pattern']}")
    print(f"📝 查询: {result['query']}")
else:
    print("ℹ️ 普通输入")
```

---

## 故障排查

### 问题1: context_injector.py 导入错误

**错误**:
```
ImportError: cannot import 'layered_storage' from 'deepsea_nexus'
```

**原因**: 旧版本依赖的 `layered_storage.py` 缺失或路径不一致

**解决方案**: 已加入 compat 回退与可选 layered_storage，直接可用

```python
# ❌ 错误
from context_injector import ContextInjector

# ✅ 正确
from nexus_autoinject import smart_search
```

---

### 问题2: nexus_autoinject.py socket 连接失败

**错误**:
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**原因**: `nexus_warmup.sock` 服务未启动

**解决方案**: 已加入 compat 回退（无 socket 也可正常召回）

```python
# ❌ 错误
from nexus_autoinject import smart_search

# ✅ 正确
from nexus_core import nexus_recall
results = nexus_recall(query, 5)
```

---

### 问题3: 向量库损坏

**错误**:
```
Error executing plan: Failed to apply logs to the metadata segment
```

**原因**: metadata segment 目录丢失

**解决方案**: 使用备份恢复

```bash
# 检查
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='~/.openclaw/workspace/memory/.vector_db')
for c in client.list_collections():
    print(f'{c.name}: {c.count()}')"

# 恢复
cp -r ~/.openclaw/workspace/memory/.vector_db_backup ~/.openclaw/workspace/memory/.vector_db
```

---

### 问题4: OpenClaw Hook 不工作

**错误**: Hook 未触发

**原因**: OpenClaw 只支持 `command` 事件

**解决方案**: 使用 cron job 定时保存

```bash
# 添加 cron job
0 * * * * /Users/yizhi/.openclaw/workspace/.venv-nexus/bin/python \
  /Users/yizhi/.openclaw/workspace/skills/deepsea-nexus/scripts/nexus_auto_save.py
```

---

## 更新日志

### v2.3 (2026-02-13)

| 模块 | 状态 | 变更 |
|------|------|------|
| nexus_core.py | ✅ | 恢复向量库 (2,200+ 条) |
| auto_summary.py | ✅ | 统一摘要格式 |
| context_injector.py | ✅ | 兼容回退可用 |
| nexus_autoinject.py | ✅ | 无 socket 也可用 |
| hooks_system.py | ⚠️ | OpenClaw 不支持 |

### v2.0 (2026-02-07)

- 初始版本
- 向量存储
- RAG 召回
- Session 管理

---

## 相关文件

| 文件 | 功能 | 状态 |
|------|------|------|
| `nexus_core.py` | 核心引擎 | ✅ |
| `auto_summary.py` | 智能摘要 | ✅ |
| `nexus_autoinject.py` | 智能注入 | ✅ |
| `context_injector.py` | 上下文注入 | ✅ |
| `auto_recall.py` | 自动召回 | ✅ |
| `session_manager.py` | 会话管理 | ✅ |
| `flush_manager.py` | 自动Flush | ✅ |
| `hooks_system.py` | Hook 系统 | ⚠️ |

---

## 许可证

MIT
