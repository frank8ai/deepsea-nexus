# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-11
- SOP ID: SOP-20260217-11
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 降低重复错误并形成可复用纠错规则

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 逐题修正不分类 | 难复用 |
| B | 根因分桶+定向修复 | 闭环效果最好 |
| C | 只重复刷题 | 可能掩盖根因 |

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
| 根因联动 | SOP_PRINCIPLES.md | policy | 降低复发率 | 根因误判 |
| 错误闭环记录 | agent/patterns/sop-factory.md | process | 可复盘可迭代 | 日志缺失 |
| 学习技术证据 | https://pubmed.ncbi.nlm.nih.gov/26173288/ | external research | 纠错效率更高 | 缺少复测 |

## Best Method Decision
- Selected method: Option B 根因分桶+定向修复
- Why this method is best under current constraints: 能稳定降低重复错误并沉淀规则
- Rejected alternatives and reasons:
  - Option A: 难定位系统性问题
  - Option C: 问题被推迟而非解决

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 错题本模板 | 错误记录 | 漏记率下降 >=30% | 记录负担 | 最小字段 |
| 根因标签 | 分类诊断 | 复发率下降 >=20% | 标签不一致 | 每周校准 |
| 复测清单 | 闭环验证 | 修复率提升 >=25% | 复测拖延 | 固定窗口 |

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
