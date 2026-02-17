# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-20
- SOP ID: SOP-20260217-20
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 学习成果必须迁移到真实题目或项目任务

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 只做理论学习 | 迁移率低 |
| B | 学后72小时内应用实践 | 迁移效果最佳 |
| C | 月末集中迁移 | 遗忘导致效率低 |

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
| 检索与应用结合 | https://pubmed.ncbi.nlm.nih.gov/26173288/ | external research | 提升迁移能力 | 练习脱离场景 |
| 结果导向 | SOP_PRINCIPLES.md | policy | 强化产出质量 | 只学不做 |
| 闭环回写 | agent/patterns/sop-factory.md | process | 可持续迭代 | 复盘中断 |

## Best Method Decision
- Selected method: Option B 学后72小时内应用实践
- Why this method is best under current constraints: 利用短时记忆窗口最大化迁移效率
- Rejected alternatives and reasons:
  - Option A: 缺乏可验证产出
  - Option C: 迁移窗口过晚

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 迁移任务清单 | 应用计划 | 迁移率提升 >=30% | 任务过重 | 拆小任务 |
| 实战练习仓库 | 证据沉淀 | 复盘质量提升 >=25% | 维护负担 | 周归档 |
| 迁移日志 | 指标跟踪 | 闭环速度提升 >=20% | 记录遗漏 | 最小字段强制 |

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
