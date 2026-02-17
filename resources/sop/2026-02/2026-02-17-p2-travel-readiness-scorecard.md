# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-27
- SOP ID: SOP-20260217-27
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 行前准备必须覆盖证件、行程、预算和应急

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 临行前临时准备 | 风险高且易遗漏 |
| B | 清单化分阶段准备 | 稳定且高覆盖 |
| C | 完全依赖第三方安排 | 透明度不足 |

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
| 非可协商约束优先 | SOP_PRINCIPLES.md | policy | 降低出行中断风险 | 准备过度 |
| 清单门禁机制 | agent/patterns/sop-factory.md | process | 降低遗漏 | 清单维护不足 |
| strict校验 | scripts/validate_sop_factory.py | executable | 结构可审计 | 执行遗漏 |

## Best Method Decision
- Selected method: Option B 清单化分阶段准备
- Why this method is best under current constraints: 在有限准备时间下覆盖关键风险点
- Rejected alternatives and reasons:
  - Option A: 漏项导致临场成本高
  - Option C: 对行程异常响应慢

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 行前清单 | 覆盖保证 | 漏项下降 >=30% | 清单过时 | 出行后复盘更新 |
| 行程板 | 节点管理 | 延误应对速度提升 >=25% | 信息分散 | 单一来源维护 |
| 应急卡片 | 风险应对 | 应急响应提升 >=20% | 更新滞后 | 出发前复核 |

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
