# Second Brain PARA (vNext)

目标：把 Deep-Sea Nexus 的结构化摘要、向量检索与 Obsidian PARA 体系结合，形成“可执行第二大脑”。

## 目录结构（默认）
- `Obsidian/10_Projects/`
- `Obsidian/20_Knowledge/Areas/`
- `Obsidian/20_Knowledge/Resources/`
- `Obsidian/20_Knowledge/Archive/`
- `Obsidian/90_Memory/`

## L0/L1/L2 层级
- L0: `.abstract.md`（超短摘要）
- L1: `.overview.md`（项目概览）
- L2: `Warm.md` + `Blueprint.md`（完整可执行信息）

## 初始化 PARA
```bash
python scripts/para_init.py --obsidian ~/Obsidian
```

## 自动写 Warm（从结构化摘要）
```bash
python scripts/warm_writer.py --from ~/.openclaw/logs/summaries/xxxx.json
```

## 目录递归检索（项目优先）
```bash
python scripts/para_recall.py --query "故障转移系统" --top-projects 3
```

## Warm 就绪验收（<=2 分钟重启）
```bash
python scripts/para_validate.py --project "YourProject" --max-age-minutes 120
```

## 自动接入（建议）
将 `scripts/flush_summaries.py` 作为 cron 运行：
- 自动存入向量库
- 若 `project关联` 存在，自动更新 Warm
