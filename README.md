# Deep-Sea Nexus v2.3

> AI Agent 长期记忆系统 | 向量存储 | 智能摘要 | RAG 召回

## 📦 GitHub 仓库
**https://github.com/frank8ai/deepsea-nexus**

## 核心特性

| 特性 | 指标 | 说明 |
|------|------|------|
| 向量存储 | 2,200+ 条 | ChromaDB 本地持久化 |
| 智能摘要 | 自动提取 | `## 📋 总结` 格式 |
| RAG 召回 | < 100ms | 语义搜索 |
| 启动加载 | < 300 tokens | 轻量启动 |

## 目录结构

```
deepsea-nexus/
├── nexus_core.py          # 核心引擎
├── auto_summary.py        # 智能摘要模块
├── session_manager.py     # 会话管理
├── flush_manager.py       # 自动Flush
├── hooks/                 # Hooks 系统
│   ├── hooks_system.py
│   ├── pre-prompt/
│   ├── post-response/
│   └── tool-call/
├── scripts/              # 工具脚本
│   ├── save_summary.sh    # 手动保存摘要
│   └── nexus_auto_save.py # 自动保存脚本
├── config.yaml           # 配置文件
└── memory/               # 向量库
    └── .vector_db_final/  # 持久化存储
```

## 快速开始

### 初始化

```bash
cd ~/workspace/skills/deepsea-nexus
source ../.venv-nexus/bin/activate
python3 -c "from nexus_core import nexus_init; nexus_init()"
```

### 基本使用

```bash
# 初始化
python3 -c "from nexus_core import nexus_init; nexus_init(blocking=True)"

# 保存内容
python3 -c "from nexus_core import nexus_add; nexus_add('内容', '标题', '标签')"

# 搜索记忆
python3 -c "from nexus_core import nexus_recall; nexus_recall('关键词', 5)"
```

### 手动保存摘要

```bash
cd ~/workspace/skills/deepsea-nexus
./save_summary.sh "摘要内容"
```

## Python API

```python
from nexus_core import nexus_init, nexus_add, nexus_recall

# 初始化
nexus_init(blocking=True)

# 添加记忆
nexus_add(
    content="学习 Python 列表推导式",
    title="Python学习",
    tags="python,learning"
)

# 召回记忆
results = nexus_recall("Python", 5)
for r in results:
    print(f"[{r.relevance:.2f}] {r.content[:100]}...")
```

## 智能摘要

### 摘要格式（必须遵守）

```markdown
[回复内容]

## 📋 总结
- 要点1
- 要点2
- 要点3
```

### 配置文件

```yaml
vector_store:
  persist_directory: "~/.openclaw/workspace/memory/.vector_db_final"
  collection_name: "deepsea_nexus_full"
  distance_metric: "cosine"

embedding:
  model_name: "sentence-transformers/all-MiniLM-L6-v2"
  dimension: 384
```

## 集成到 OpenClaw

### AGENTS.md 规则

```markdown
## 🧠 VII. Auto-Summary Protocol (智能摘要)

### Summary Output Format (MANDATORY)

**EVERY response MUST end with a summary** in this exact format:

```markdown
[Your complete response content]

## 📋 总结
- Key point 1
- Key point 2
- Key point 3
```

**Format Rules (STRICTLY ENFORCED):**
1. Use `## 📋 总结` as the header (with 📋 emoji)
2. Use `- ` list format
3. Summary length: 3-5 bullet points
4. **EMPTY LINE required** between content and summary
```

### SOUL.md 规则

```markdown
### 📝 摘要生成规则 (强制执行)

**每次回复后必须在末尾添加摘要**，格式固定如下：

```markdown
[你的完整回复内容]

## 📋 总结
- 要点1
- 要点2
```
```

## 自动保存

### Cron Job（每小时）

```bash
0 * * * * /Users/yizhi/.openclaw/workspace/.venv-nexus/bin/python /Users/yizhi/.openclaw/workspace/skills/deepsea-nexus/scripts/nexus_auto_save.py >> ~/.openclaw/logs/nexus-auto-save.log 2>&1
```

### 手动保存

```bash
cd ~/workspace/skills/deepsea-nexus
./save_summary.sh "对话摘要内容"
```

## 向量库管理

### 查看状态

```bash
python3 -c "
from nexus_core import nexus_init, nexus_stats
nexus_init(blocking=True)
stats = nexus_stats()
print(f'文档数: {stats[\"total_documents\"]}')
"
```

### 备份向量库

```bash
cp -r ~/.openclaw/workspace/memory/.vector_db_final ~/.openclaw/workspace/memory/.vector_db_backup
```

## 故障排查

### 问题1: 向量库损坏

```bash
# 检查
python3 -c "
import chromadb
client = chromadb.PersistentClient(path='~/.openclaw/workspace/memory/.vector_db')
for c in client.list_collections():
    print(f'{c.name}: {c.count()}')
"

# 修复：使用备份
cp -r ~/.openclaw/workspace/memory/.vector_db_backup ~/.openclaw/workspace/memory/.vector_db
```

### 问题2: 摘要未保存

1. 检查 AI 回复是否包含 `## 📋 总结` 格式
2. 手动运行保存脚本
3. 查看日志: `tail -f ~/.openclaw/logs/nexus-auto-save.log`

## 更新日志

### v2.3 (2026-02-13)
- ✅ 恢复向量库数据 (2,200+ 条)
- ✅ 统一摘要格式为 `## 📋 总结`
- ✅ 添加自动保存脚本
- ✅ 配置 Cron 每小时备份
- ⚠️ OpenClaw 不支持 post-response 事件（使用 workaround）

### v2.0 (2026-02-07)
- 初始版本
- 向量存储
- RAG 召回
- Session 管理

## 许可证

MIT
