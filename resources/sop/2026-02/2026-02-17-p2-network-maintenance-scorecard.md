# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-28
- SOP ID: SOP-20260217-28
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 维护节奏要稳定且可持续，避免关系管理形式化

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 随缘联系 | 成本低但稳定性差 |
| B | 分层名单+周期触达+记录 | 可持续性最佳 |
| C | 高频触达全部对象 | 负担高且质量下降 |

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
| 结果价值优先 | SOP_PRINCIPLES.md | policy | 聚焦高价值关系 | 过度功利 |
| 小步迭代 | agent/patterns/sop-factory.md | process | 节奏稳定 | 记录流失 |
| strict校验 | scripts/validate_sop_factory.py | executable | 结构完整 | 执行遗漏 |

## Best Method Decision
- Selected method: Option B 分层名单+周期触达+记录
- Why this method is best under current constraints: 在有限时间下保持关系质量和连续性
- Rejected alternatives and reasons:
  - Option A: 触达随机性高不可复盘
  - Option C: 触达质量和可持续性下降

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 关系分层清单 | 优先级管理 | 触达命中率提升 >=30% | 分层主观 | 季度复核分层 |
| 触达节奏表 | 周期控制 | 漏触达率下降 >=25% | 节奏僵化 | 允许弹性窗口 |
| 触达记录卡 | 关系上下文 | 跟进质量提升 >=20% | 记录负担 | 最小字段记录 |

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
