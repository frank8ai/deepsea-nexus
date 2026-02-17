# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-26
- SOP ID: SOP-20260217-26
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 季度重构要在不破坏稳定性的前提下提升系统效能

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 持续小修不做重构 | 风险低但技术债累积 |
| B | 季度审计+分批重构 | 稳定性与收益最佳 |
| C | 一次性大重构 | 风险和停机成本高 |

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
| 简洁可维护优先 | SOP_PRINCIPLES.md | policy | 控制复杂度 | 改造不足 |
| 小步迭代门禁 | agent/patterns/sop-factory.md | process | 降低回归风险 | 节奏过慢 |
| strict校验 | scripts/validate_sop_factory.py | executable | 发布一致性 | 仅结构合规 |

## Best Method Decision
- Selected method: Option B 季度审计+分批重构
- Why this method is best under current constraints: 兼顾技术债清理和生产稳定
- Rejected alternatives and reasons:
  - Option A: 性能和可维护性持续下降
  - Option C: 短期风险不可控

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 系统审计清单 | 问题定位 | 问题发现率提升 >=30% | 指标噪声 | 指标分层 |
| 分批发布计划 | 风险控制 | 回归事故下降 >=25% | 节点复杂 | 每批限范围 |
| 回归检查表 | 质量保障 | 漏测下降 >=20% | 检查项膨胀 | 核心项优先 |

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
