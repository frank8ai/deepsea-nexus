# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-14
- SOP ID: SOP-20260217-14
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 保持应急计划长期可用且可演练

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 仅保留纸面清单 | 失效率高 |
| B | 月检+即修+季度演练 | 可靠性最高 |
| C | 年度集中检查 | 间隔过长风险大 |

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
| 应急计划框架 | https://www.redcross.org/get-help/how-to-prepare-for-emergencies/make-a-plan.html | external guidance | 明确应急动作 | 长期不更新 |
| 联系与路线准备 | https://www.cdc.gov/disability-emergency-preparedness/people-with-disabilities/make-a-plan.html | external guidance | 减少响应混乱 | 信息过期 |
| 闭环更新 | agent/patterns/sop-factory.md | process | 持续可用 | 只检查不修复 |

## Best Method Decision
- Selected method: Option B 月检+即修+季度演练
- Why this method is best under current constraints: 在可承受成本内保持长期可用性
- Rejected alternatives and reasons:
  - Option A: 纸面计划无法验证执行
  - Option C: 检查周期过长导致过期风险

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 应急清单 | 状态盘点 | 缺项发现率提升 >=30% | 清单老化 | 季度更新 |
| 联系树 | 通讯保障 | 响应效率提升 >=25% | 联系失效 | 双渠道备份 |
| 演练记录 | 可执行验证 | 可用性提升 >=20% | 演练拖延 | 固定演练日 |

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
