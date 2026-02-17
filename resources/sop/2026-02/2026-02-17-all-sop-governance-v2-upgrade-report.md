# 全量SOP治理V2升级报告

- Date: 2026-02-17
- Scope: `resources/sop/2026-02/*-sop.md` (31 SOP)
- Goal: 按最高标准（不可互相抵消）重构全量SOP，并落地4项硬机制 + 检索友好层

## 最高标准（自上而下）
1. 非可协商约束（合规/安全/数据完整性）
2. 结果价值优先
3. 证据强度随风险升级
4. 可逆性决定速度
5. 三佳执行层（最佳实践 -> 最佳方法 -> 最佳工具）
6. 简洁可维护
7. 闭环写回与规则更新

## 硬机制落地
1. 生命周期字段
   - Metadata新增：`Effective condition` / `Review cycle` / `Retirement condition`
2. Kill Switch
   - 每份SOP新增 `## Kill Switch` 表（触发阈值 -> 立即停止 -> 回滚动作）
3. 双轨指标
   - `SLA and Metrics` 新增：
     - `Result metric (primary)`
     - `Process metric (secondary)`
     - `Replacement rule`
4. 自动降级门禁
   - `Release Readiness` 新增 `Auto-downgrade gate`
   - 规则：主结果指标连续2个周期退化，`active -> draft`

## 检索友好层（Second Brain）
- Metadata新增：
  - `Tags`
  - `Primary triggers`
  - `Primary outputs`
- 每份SOP生成：
  - `*.abstract.md` (L0)
  - `*.overview.md` (L1)

## 涉及文件
- Standard stack:
  - `agent/patterns/sop-factory.md`
- Templates:
  - `resources/sop/TEMPLATE.sop.md`
  - `resources/sop/TEMPLATE.sop-iteration-log.md`
- Validator:
  - `scripts/validate_sop_factory.py`
- Batch upgrader:
  - `scripts/upgrade_sop_governance_v2.py`

## 执行与验收
- 批量升级命令：
  - `python3 scripts/upgrade_sop_governance_v2.py`
- 严格校验：
  - `for f in resources/sop/2026-02/*-sop.md; do python3 scripts/validate_sop_factory.py --sop "$f" --strict; done`
- Result:
  - `strict_ok=31`
  - `strict_fail=0`
