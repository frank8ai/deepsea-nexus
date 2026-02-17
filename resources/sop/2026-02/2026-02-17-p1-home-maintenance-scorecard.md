# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-22
- SOP ID: SOP-20260217-22
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 周期性家务和维护任务要可持续执行，不依赖临时记忆

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 想到再做 | 容易遗漏 |
| B | 周期清单+固定窗口执行 | 稳定且可持续 |
| C | 一次性集中大扫除 | 峰值成本高、间隔长 |

## Weighted Dimensions
| Dimension | Weight (0-1) | Why it matters |
|---|---|---|
| Effectiveness | 0.35 | Outcome quality and goal fit |
| Cycle Time | 0.20 | Throughput and speed |
| Error Prevention | 0.20 | Risk and defect reduction |
| Implementation Cost | 0.15 | Build and maintenance cost |
| Operational Risk | 0.10 | Stability and failure impact |

## Scoring Table (1-5 for each dimension)
| Option | Effectiveness | Cycle Time | Error Prevention | Implementation Cost | Operational Risk | Weighted Score |
|---|---|---|---|---|---|---|
| A | 3 | 5 | 3 | 5 | 4 | 3.80 |
| B | 5 | 4 | 5 | 3 | 4 | 4.40 |
| C | 4 | 3 | 4 | 4 | 3 | 3.70 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| 简洁可维护原则 | SOP_PRINCIPLES.md | policy | 长期可执行 | 过度复杂 |
| 周期任务机制 | agent/patterns/sop-factory.md | process | 降低遗漏 | 清单老化 |
| 严格校验 | scripts/validate_sop_factory.py | executable | 结构完整 | 执行遗漏 |

## Best Method Decision
- Selected method: Option B 周期清单+固定窗口执行
- Why this method is best under current constraints: 以最低认知负担维持稳定完成率
- Rejected alternatives and reasons:
  - Option A: 遗漏不可预测
  - Option C: 执行压力集中且中断风险高

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 周期清单 | 任务覆盖 | 漏项率下降 >=30% | 清单过时 | 月度刷新 |
| 固定窗口日历 | 时间保障 | 完成率提升 >=25% | 被临时占用 | 预留备选窗口 |
| 维护记录表 | 证据追踪 | 复发问题下降 >=20% | 记录缺失 | 最小字段强制 |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: B
- Winner weighted score: 4.40
- Runner-up weighted score: 3.80
- Margin: 0.60
- Override reason (required when margin < 0.20): n/a
- Approval: owner approved on 2026-02-17
- Effective from: 2026-02-17
