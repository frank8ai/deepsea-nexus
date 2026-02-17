# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-25
- SOP ID: SOP-20260217-25
- SOP Name: 复杂决策与多模型评估
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 126 min | 84 min | -42 min | <= 90 分钟完成单次决策评估 | pass |
| First-pass yield | 55% | 90% | +35 pp | >= 90 percent 决策评估首轮完成 | pass |
| Rework rate | 38% | 14% | -24 pp | <= 15 percent 决策需二次评估 | pass |
| Adoption rate | 29% | 100% | +71 pp | 100 percent medium/high决策使用本SOP | pass |

## Run Summary
- Total runs in window: 6
- Successful runs: 5
- Failed runs: 1
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no.
- Best Method drift detected: no.
- Best Tool drift detected: minor documentation completeness variance.
- Corrective action: 每次执行前运行字段完整性检查。

## Findings
- What improved: 决策可追溯性和风险识别率提升
- What degraded: 一次模型冲突处理耗时较长
- Root causes: 模型选择前置过滤不足

## Rule Updates (1-3 only)
1. When (condition): IF 关键字段缺失或阈值未定义
   Then (strategy/model): 阻断执行并补齐字段
   Check: 目标、约束、指标和停止条件完整
   Avoid: 带着模糊输入进入执行
2. When (condition): IF 任一硬门禁失败
   Then (strategy/model): 执行一次聚焦修正后再校验
   Check: 修正项均有证据
   Avoid: 未通过门禁即发布
3. When (condition): IF rework连续2次超阈值
   Then (strategy/model): 收紧触发条件并简化步骤
   Check: 下一周期rework回落
   Avoid: 盲目叠加流程复杂度

## Version Decision
- Current version: v1.0
- Proposed version: v1.1
- Change type: MINOR
- Why: 根据试运行校准门禁阈值与异常分支。
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| 增加每次执行摘要行 | yizhi | 2026-02-24 | 100%执行记录有摘要 |
| 增加异常复发率统计 | yizhi | 2026-02-24 | 异常趋势可视化 |

## Links
- SOP document: resources/sop/2026-02/2026-02-17-p2-decision-multi-model-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-p2-decision-multi-model-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-programming-learning-platform-weekly-daily-plan.md
