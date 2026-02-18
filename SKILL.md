# Deep-Sea Nexus Skill

AI Agent 长期记忆系统 - 语义检索、RAG 召回、会话管理、自动压缩。

## 描述
热插拔架构的长期记忆系统，提供语义搜索、会话生命周期管理、自动 Flush/压缩。100% 向后兼容 v2.x API，支持分层加载（v3.2）与混合向量召回（v4.x）。

## 状态
✅ 生产就绪 (v4.4.0, 2026-02-18)

## 核心功能
- 语义搜索与 RAG 召回
- 会话创建/关闭/归档
- 自动压缩与清理
- 事件驱动通信
- 配置热重载
- 上下文预算化注入

## 安装与集成
该技能已存在于 `skills/deepsea-nexus/`。OpenClaw 已通过 `MEMORY.md` 协议集成；也可使用脚本 `local_memory_search.py` 或 `recall.sh` 作为独立搜索入口。

## Python API (推荐)
```python
from deepsea_nexus import nexus_init, nexus_recall, nexus_add

nexus_init()
results = nexus_recall("查询关键词", n=5)
doc_id = nexus_add("内容片段", "标题", "标签列表")
```

## 异步 API (v4.x)
```python
from deepsea_nexus import create_app
import asyncio

async def main():
    app = create_app()
    await app.initialize()
    await app.start()

    nexus = app.plugins["nexus_core"]
    results = await nexus.search_recall("查询", n=5)

    await app.stop()

asyncio.run(main())
```

## 命令行快速搜索
```bash
cd /Users/yizhi/.openclaw/workspace/skills/deepsea-nexus
./venv-nexus/bin/python3 local_memory_search.py "搜索关键词" --max-results 5 --json
```

## 配置
编辑 `skills/deepsea-nexus/config.yaml` 或 `config.json`。支持热重载，可监听变更。

## 兼容性
- 向后兼容 v2.x 调用（`nexus_init`、`nexus_recall`、`nexus_add`）
- v3.2 分层加载可选，降低启动 Token 89%
- v4.x 混合召回与自适应注入调参

## 日志与自观测
运行指标日志: `~/workspace/logs/smart_context_metrics.log`
`~/workspace/logs/context_engine_metrics.log`

## 注意
首次运行会加载本地模型（~20秒），后续有缓存。向量库路径在 `skills/deepsea-nexus/memory/.vector_db`（请勿手动删除）。
