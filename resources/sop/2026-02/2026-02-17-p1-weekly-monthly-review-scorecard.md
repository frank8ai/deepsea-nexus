# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-19
- SOP ID: SOP-20260217-19
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 复盘输出必须转化为规则更新，避免空复盘

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 只写总结不改规则 | 可读但不可执行 |
| B | 指标复盘+1-3条规则更新 | 闭环最完整 |
| C | 全量规则重写 | 变更过大不稳定 |

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
| 闭环学习原则 | SOP_PRINCIPLES.md | policy | 避免口号化复盘 | 无规则沉淀 |
| 1-3规则限制 | agent/patterns/sop-factory.md | process | 控制变更风险 | 改动过少 |
| strict校验 | scripts/validate_sop_factory.py | executable | 保障结构完整 | 指标采集缺失 |

## Best Method Decision
- Selected method: Option B 指标复盘+1-3条规则更新
- Why this method is best under current constraints: 在可控变更范围内保持持续优化
- Rejected alternatives and reasons:
  - Option A: 无法驱动行为变化
  - Option C: 破坏系统稳定性

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 复盘模板 | 结构化复盘 | 复盘质量提升 >=30% | 形式化风险 | 强制偏差分析 |
| 指标看板 | 事实依据 | 偏差定位速度提升 >=25% | 指标噪声 | 指标分层 |
| 规则库 | 规则回写 | 复用率提升 >=20% | 规则膨胀 | 定期清理 |

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
