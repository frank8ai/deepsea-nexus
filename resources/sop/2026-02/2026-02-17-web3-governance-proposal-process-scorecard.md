# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-46
- SOP ID: SOP-20260217-46
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 将治理提案从讨论到执行全过程标准化，提升治理透明度与执行成功率。

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 论坛讨论 -> 草案定稿 -> 投票 -> 执行 -> 复盘。 | 在质量与效率间平衡 |
| B | 经验驱动快速执行 | 速度快但漏项风险高 |
| C | 重流程全量评审 | 风险低但成本高 |

## Weighted Dimensions
| Dimension | Weight (0-1) | Why it matters |
|---|---:|---|
| Effectiveness | 0.35 | Outcome quality and goal fit |
| Cycle Time | 0.20 | Throughput and speed |
| Error Prevention | 0.20 | Risk and defect reduction |
| Implementation Cost | 0.15 | Build and maintenance cost |
| Operational Risk | 0.10 | Stability and failure impact |

## Scoring Table (1-5 for each dimension)
| Option | Effectiveness | Cycle Time | Error Prevention | Implementation Cost | Operational Risk | Weighted Score |
|---|---:|---:|---:|---:|---:|---:|
| A | 5 | 4 | 5 | 4 | 4 | 4.55 |
| B | 3 | 5 | 3 | 5 | 3 | 3.70 |
| C | 4 | 2 | 4 | 2 | 5 | 3.50 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| 治理提案必须包含执行路径和回滚方案。 | Compound Governance Docs:https://docs.compound.finance/v2/governance/ | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |
| 治理提案必须包含执行路径和回滚方案。 | Snapshot Docs:https://docs.snapshot.box/ | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |

## Best Method Decision
- Selected method: Option A (论坛讨论 -> 草案定稿 -> 投票 -> 执行 -> 复盘。)
- Why this method is best under current constraints: 在硬门禁约束下同时保证结果质量与执行效率。
- Rejected alternatives and reasons:
  - Option B: 关键风险识别不足，容易漏掉不可协商约束。
  - Option C: 过程过重，不适合高频执行。

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 论坛模板 | 核心执行 | 治理执行偏差下降 >=25%；提案通过后执行延迟下降 >=20% | 工具依赖增加 | 触发治理回滚提案并恢复上版参数 |
| 指标看板 | 结果跟踪 | 主结果指标可视化覆盖 >=95% | 指标噪声 | 回退到核心指标集 |
| 校验脚本 | 结构门禁 | 漏项率下降 >=40% | 误报导致阻塞 | 草稿模式+人工复核 |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: A
- Winner weighted score: 4.55
- Runner-up weighted score: 3.70
- Margin: 0.85
- Override reason (required when margin < 0.20): n/a
- Approval: yizhi
- Effective from: 2026-02-17
