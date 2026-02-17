# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-21
- SOP ID: SOP-20260217-21
- SOP Name: 家庭协同与分工沟通
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 46 min | 29 min | -17 min | <= 30 分钟完成周协同计划 | pass |
| First-pass yield | 62% | 90% | +28 pp | >= 90 percent 家庭关键任务按期启动 | pass |
| Rework rate | 31% | 13% | -18 pp | <= 15 percent 任务需二次分配 | pass |
| Adoption rate | 41% | 100% | +59 pp | 100 percent 家庭关键任务使用协同流程 | pass |

## Run Summary
- Total runs in window: 6
- Successful runs: 5
- Failed runs: 1
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no.
- Best Method drift detected: no.
- Best Tool drift detected: minor documentation completeness variance.
- Corrective action: 每次执行先运行字段完整性检查。

## Findings
- What improved: 家庭任务完成率和时间协同显著提升
- What degraded: 一次临时事件导致计划偏移
- Root causes: 应急预案不足

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
- Why: 根据试运行补齐门禁语义与异常处理。
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| 增加每次执行一行摘要 | yizhi | 2026-02-24 | 100%执行记录有摘要 |
| 增加异常类别统计 | yizhi | 2026-02-24 | 异常复发趋势可视化 |

## Links
- SOP document: resources/sop/2026-02/2026-02-17-p1-family-collaboration-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-p1-family-collaboration-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-programming-learning-platform-task-clarification.md
