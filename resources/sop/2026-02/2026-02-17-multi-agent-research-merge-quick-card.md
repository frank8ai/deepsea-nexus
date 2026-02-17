# 一页执行卡：多代理并行研究与合并

## 何时触发
- 问题存在 >=2 个可行方案，或不确定性高。
- 决策影响 >= 1 周工作量，或成本影响显著。

## 输入
- 问题定义（目标/约束/成功标准）
- 时间盒（默认 45-90 分钟）

## 8 步执行
1. 冻结问题陈述与成功标准。
2. 并行分配 3 角色：Researcher / Critic / Builder。
3. 统一收口格式（结论/证据/不确定性/下一步）。
4. Synthesizer 生成冲突表（Claim A/B/Evidence/Decision）。
5. 产出选项矩阵（成本/风险/维护/迁移）。
6. 写决策卡（1-3 个下一步 + 停止条件 + owner）。
7. 路由到复盘写回 SOP，提取 1-3 条规则。
8. 记录迭代日志（时长/冲突数/来源数/结果）。

## 硬门禁
- 关键主张单源时必须标记 `needs-second-source`。
- 冲突未收敛 >=2 条时，追加 15 分钟定向补证。
- 时间用到 80% 仍未决策时，强制停止扩源并输出决策卡。

## 输出
- 研究包：`resources/research-packs/YYYY-MM/*.md`
- 决策卡：`resources/decisions/YYYY-MM/*.md`
- 迭代日志：`resources/sop/2026-02/2026-02-17-multi-agent-research-merge-iteration-log.md`

## SLA
- 单次周期：<= 90 分钟
- 首次决策卡产出率：>= 80%
- 二次合并率：<= 20%

## 校验命令
```bash
python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-17-multi-agent-research-merge-sop.md --strict
```
