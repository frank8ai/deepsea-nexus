# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-33
- SOP ID: SOP-20260217-33
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 用主指标+护栏指标+停止条件提高实验决策质量，避免伪改进。

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 假设 -> 干预 -> 指标 -> 幅度 -> 停止条件五段法。 | 在质量与效率间平衡 |
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
| 实验评审必须明确主指标、护栏指标和停止条件。 | Microsoft Experimentation Platform:https://www.microsoft.com/en-us/research/group/experimentation-platform-exp/ | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |
| 实验评审必须明确主指标、护栏指标和停止条件。 | DORA:https://dora.dev/ | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |

## Best Method Decision
- Selected method: Option A (假设 -> 干预 -> 指标 -> 幅度 -> 停止条件五段法。)
- Why this method is best under current constraints: 在硬门禁约束下同时保证结果质量与执行效率。
- Rejected alternatives and reasons:
  - Option B: 关键风险识别不足，容易漏掉不可协商约束。
  - Option C: 过程过重，不适合高频执行。

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 实验模板 | 核心执行 | 无效实验比例下降 >=25%；决策速度提升 >=20% | 工具依赖增加 | 回退实验开关并恢复基线策略 |
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
