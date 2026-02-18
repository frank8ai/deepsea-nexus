# Deep-Sea Nexus v4.3 本地部署

## 目标
将当前仓库版本部署到本地 OpenClaw 工作区，并确保门禁与运行态可用。

## 前置条件
- 路径：`~/.openclaw/workspace/skills/deepsea-nexus`
- Python：`3.8+`
- 可选依赖：`chromadb`、`sentence-transformers`（缺失时自动降级，不阻塞启动）

## 一键部署
在仓库根目录执行：

```bash
bash scripts/deploy_local_v4.sh --full
```

说明：
- `--full`：执行 `run_tests.py` 全量门禁 + 运行态 smoke 检查
- `--quick`：仅执行 `tests/test_units.py` + 运行态 smoke 检查

## 成功判定
- `run_tests.py` 结尾输出 `ALL TESTS PASSED`
- 脚本输出 JSON 状态，至少满足：
  - `available: true`
  - `initialized: true`
  - `plugin_version: "3.0.0"`（插件协议版本）
  - `package_version: "4.3.0"`（发布版本）

## 常见问题
- `chromadb` 未安装：
  - 现版本会自动进入 degraded mode（lexical fallback），可继续运行。
- `deepsea_nexus` 导入失败：
  - 确认脚本在仓库根目录执行，或显式设置 `PYTHONPATH=~/.openclaw/workspace/skills`。
