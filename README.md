# 🧠 Deep-Sea Nexus v3.0

## AI Agent 长期记忆系统 - 热插拔架构

**版本**: 3.0.0  
**状态**: ✅ 生产就绪  
**更新**: 2026-02-13

---

## ✨ 核心特性

| 特性 | 描述 | 状态 |
|------|------|------|
| 🔌 **热插拔架构** | 动态插件加载/卸载 | ✅ |
| 📡 **事件驱动** | 解耦模块通信 | ✅ |
| 📦 **统一压缩** | 消除代码重复 | ✅ |
| 🔄 **100% 向后兼容** | 零破坏性变更 | ✅ |
| ⚡ **异步优先** | 非阻塞操作 | ✅ |
| 🔧 **热重载配置** | 无需重启更新配置 | ✅ |

---

## 🎯 核心功能详解

### 1. 语义搜索与 RAG 召回

Deep-Sea Nexus 的核心功能，提供语义级别的记忆检索。

```python
from deepsea_nexus import nexus_recall

# 语义搜索
results = nexus_recall("Python 装饰器使用方法", n=5)

# 结果包含:
# - relevance: 相关性分数 (0-1)
# - content: 内容片段
# - source: 来源标识
# - metadata: 元数据
for r in results:
    print(f"[{r.relevance:.2f}] {r.source}")
    print(f"   {r.content[:100]}...")
```

**特性**:
- ✅ 语义相似度匹配
- ✅ 增量索引更新
- ✅ 智能分块处理
- ✅ 结果相关性排序
- ✅ 缓存优化

---

### 2. 长期记忆管理

会话生命周期管理，自动跟踪和管理 AI 记忆。

```python
from deepsea_nexus import start_session, close_session, get_session_manager

# 创建会话
session_id = start_session("Python 学习会话")

# 获取会话信息
session = get_session_manager().get_session(session_id)
print(f"主题: {session.topic}")
print(f"状态: {session.status}")
print(f"片段数: {session.chunk_count}")
print(f"金句数: {session.gold_count}")

# 关闭会话
close_session(session_id)
```

**功能**:
- 📝 自动会话创建
- 📊 活动追踪
- 🏷️ 标签管理
- 📈 统计信息
- 🔄 自动归档

---

### 3. 自动Flush与清理

智能管理存储空间，自动清理过期数据。

```python
from deepsea_nexus import manual_flush

# 预览（不执行）
preview = manual_flush(dry_run=True)
print(f"将归档: {len(preview['sessions_to_archive'])} 个会话")

# 执行清理
results = manual_flush(dry_run=False)
print(f"已归档: {results['archived']}")
print(f"已压缩: {results['compressed']}")
print(f"已跳过: {results['skipped']}")
```

**策略**:
- ⏰ 每日定时执行
- 📅 30天不活跃自动归档
- 📦 归档保留90天
- 🗜️ 自动压缩节省空间
- 🔥 手动触发清理

---

### 4. 统一压缩引擎

消除代码重复，提供统一的压缩接口，支持多种算法。

```python
from deepsea_nexus import CompressionManager

# 创建压缩管理器
cm = CompressionManager("zstd")  # gzip, zstd, lz4

# 压缩/解压数据
compressed = cm.compress(data)
decompressed = cm.decompress(compressed)

# 文件操作
cm.compress_file("data.txt")      # data.txt.gz
cm.decompress_file("data.txt.gz")  # data.txt
```

**算法对比**:

| 算法 | 压缩率 | 速度 | 依赖 |
|------|--------|------|------|
| **gzip** | ⭐⭐⭐ | ⭐⭐⭐ | 内置 |
| **zstd** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | zstandard |
| **lz4** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | lz4 |

---

### 5. 事件驱动架构

模块间通过事件进行解耦通信。

```python
from deepsea_nexus import get_event_bus

event_bus = get_event_bus()

# 订阅事件
def on_search_completed(event):
    print(f"搜索完成: {event.data['query']}")
    print(f"结果数: {len(event.data['results'])}")

event_bus.subscribe("nexus.search.completed", on_search_completed)

# 发布事件
event_bus.publish("my.custom.event", {
    "action": "update",
    "data": {"key": "value"}
})
```

**可用事件**:
- `nexus.search.completed` - 搜索完成
- `nexus.document_added` - 文档添加
- `session.created` - 会话创建
- `session.closed` - 会话关闭
- `flush.completed` - 清理完成

---

### 6. 配置热重载

无需重启即可更新配置。

```python
from deepsea_nexus import get_config_manager

config = get_config_manager()

# 获取配置
base_path = config.get("base_path", "./memory")
archive_days = config.get("session.auto_archive_days", 30)

# 设置配置
config.set("custom.setting", "value")

# 监听配置变化
config.add_listener("session.auto_archive_days", lambda old, new: 
    print(f"从 {old} 变为 {new}")
)
```

**支持**:
- 📄 YAML/JSON 配置文件
- 🔄 环境变量覆盖
- 👂 配置变更监听
- ✅ 配置验证

---

### 7. 插件系统

可扩展的插件架构，动态加载/卸载功能模块。

```python
from deepsea_nexus.core.plugin_system import NexusPlugin, PluginMetadata

class AnalyticsPlugin(NexusPlugin):
    def __init__(self):
        super().__init__()
        self.metadata = PluginMetadata(
            name="analytics",
            version="1.0.0",
            dependencies=["nexus_core"],
            hot_reloadable=True,
        )
    
    async def initialize(self, config):
        # 初始化
        return True
    
    async def start(self):
        # 启动服务
        return True
    
    async def stop(self):
        # 清理资源
        return True
```

**特性**:
- 🔌 动态加载/卸载
- 🔗 依赖自动解析
- 🏃 生命周期管理
- 🔥 热重载支持
- 🛡️ 隔离保护

---

### 8. 向后兼容层

100% 兼容 v2.x API，无需修改现有代码。

```python
# v2.x 代码 - 完全不变
from deepsea_nexus import nexus_init, nexus_recall, nexus_add

nexus_init()
results = nexus_recall("query", n=5)
doc_id = nexus_add("content", "title", "tags")
stats = nexus_stats()
health = nexus_health()
```

**兼容函数**:
| 函数 | 描述 |
|------|------|
| `nexus_init()` | 初始化 |
| `nexus_recall()` | 语义搜索 |
| `nexus_add()` | 添加文档 |
| `nexus_stats()` | 获取统计 |
| `nexus_health()` | 健康检查 |
| `start_session()` | 创建会话 |
| `close_session()` | 关闭会话 |
| `manual_flush()` | 手动清理 |
| `nexus_compress_session()` | 压缩会话 |

---

## 🚀 快速开始

### 安装
```bash
pip install deepsea-nexus==3.0.0
```

### 最小示例
```python
from deepsea_nexus import nexus_init, nexus_recall

# 初始化
nexus_init()

# 添加记忆
from deepsea_nexus import nexus_add
nexus_add("Python 装饰器是函数的高阶用法", "Python Decorator", "python,decorator")

# 搜索记忆
results = nexus_recall("Python 装饰器", n=3)
for r in results:
    print(f"[{r.relevance:.2f}] {r.content}")
```

### 新 API 示例
```python
import asyncio
from deepsea_nexus import create_app

async def main():
    app = create_app()
    
    await app.initialize()
    await app.start()
    
    # 使用插件
    nexus = app.plugins["nexus_core"]
    
    # 添加文档
    await nexus.add_document(
        content="异步编程是 Python 的强大特性",
        title="Async Python",
        tags="python,async"
    )
    
    # 搜索
    results = await nexus.search_recall("Python 异步", n=5)
    
    await app.stop()

asyncio.run(main())
```

---

## 📊 性能指标

| 指标 | 数值 | 说明 |
|------|------|------|
| ⚡ **启动时间** | < 2s | 最小配置 |
| 🔍 **搜索延迟** | < 10ms | 缓存命中 |
| 📝 **添加速度** | 50+/秒 | 批量优化 |
| 🗜️ **压缩速度** | 300MB/s | LZ4 算法 |
| 💾 **内存占用** | -40% | 优化后 |
| 🔄 **并发操作** | 1000+ | 异步支持 |

---

## 📁 项目结构

```
deepsea-nexus/
├── 📄 __init__.py          # 统一入口
├── 📄 app.py               # 主应用
├── 📄 compat.py            # 兼容层
├── 📁 core/
│   ├── 📄 plugin_system.py # 插件系统
│   ├── 📄 event_bus.py     # 事件总线
│   └── 📄 config_manager.py # 配置管理
├── 📁 plugins/
│   ├── 📄 nexus_core.py    # 语义搜索
│   ├── 📄 session_manager.py # 会话管理
│   └── 📄 flush_manager.py  # 清理管理
├── 📁 storage/
│   ├── 📄 base.py          # 抽象基类
│   └── 📄 compression.py   # 统一压缩
├── 📁 tests/
│   ├── 📄 test_units.py    # 单元测试
│   ├── 📄 test_integration.py # 集成测试
│   └── 📄 test_performance.py # 性能测试
└── 📁 docs/
    ├── 📄 architecture_v3.md # 架构文档
    └── 📄 examples_v3.md    # 使用示例
```

---

## 🔧 配置示例

```yaml
# config.yaml
base_path: ./memory

nexus:
  vector_db_path: ./vector_db
  embedder_name: all-MiniLM-L6-v2

session:
  auto_archive_days: 30
  min_chunks_to_archive: 5

flush:
  enabled: true
  archive_time: "03:00"
  compress_enabled: true
  compress_algorithm: "zstd"
  keep_archived_days: 90

compression:
  default_algorithm: "zstd"
  supported_algorithms:
    - gzip
    - zstd
    - lz4
```

---

## 📝 更新日志

### v3.0.0 (2026-02-13)

**架构升级**:
- 🔌 热插拔插件系统
- 📡 事件驱动通信
- 📦 统一压缩引擎
- 🔄 100% 向后兼容
- ⚡ 异步优先设计
- 🔧 配置热重载

**性能优化**:
- 2x 压缩速度提升
- 3x 事件处理提升
- 40% 内存降低
- 更好的并发支持

**新增功能**:
- 动态插件加载
- 高级压缩选项 (zstd, lz4)
- 改进会话管理
- 增强错误处理

---

## 📄 许可证

MIT License

---

## 👨‍💻 作者

Deep-Sea Nexus Team

---

## 🔗 链接

- 📖 **文档**: [docs.deepsea-nexus.com](https://docs.deepsea-nexus.com)
- 💻 **GitHub**: [github.com/deepsea-nexus](https://github.com/deepsea-nexus)
- 🐛 **Issues**: [GitHub Issues](https://github.com/deepsea-nexus/issues)
- 💬 **社区**: [Discord](https://discord.gg/deepsea-nexus)

---

*让 AI 记住一切 - 智能、持久、可扩展*
