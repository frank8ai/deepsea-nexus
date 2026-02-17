# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-10
- SOP ID: SOP-20260217-10
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 固定学习时长下最大化长期保持

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 随机复习 | 覆盖与时机不稳 |
| B | 间隔规则+自适应调整 | 记忆收益最高 |
| C | 临考突击 | 短期有效长期差 |

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
| Spacing effect | https://pubmed.ncbi.nlm.nih.gov/16507066/ | external research | 提升长期保持 | 间隔设置不合理 |
| 阈值化调整 | SOP_PRINCIPLES.md | policy | 提高计划可控性 | 指标漂移 |
| 规则回写 | agent/patterns/sop-factory.md | process | 持续优化 | 复盘缺失 |

## Best Method Decision
- Selected method: Option B 间隔规则+自适应调整
- Why this method is best under current constraints: 在固定投入下提升长期记忆效率
- Rejected alternatives and reasons:
  - Option A: 难以保证覆盖与时机
  - Option C: 仅适合短期应急

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 复习队列 | 任务管理 | 漏复习率下降 >=30% | 队列膨胀 | 每周清理 |
| 间隔规则表 | 调度核心 | 保持率提升 >=20% | 规则过复杂 | 退回基础间隔 |
| 结果日志 | 反馈闭环 | 调参速度提升 >=25% | 记录不全 | 最小字段强制 |

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
