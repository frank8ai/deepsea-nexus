# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-21
- SOP ID: SOP-20260217-21
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 减少家庭协调摩擦，保障关键家庭任务按期完成

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 临时口头分工 | 易遗忘和冲突 |
| B | 固定分工+共享日历+周沟通 | 协同性最稳定 |
| C | 单人集中处理 | 短期省沟通长期不可持续 |

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
| 结果优先于忙碌 | SOP_PRINCIPLES.md | policy | 聚焦关键家庭结果 | 只沟通不执行 |
| 小步闭环 | agent/patterns/sop-factory.md | process | 降低分工冲突 | 规则不更新 |
| 门禁检查 | scripts/validate_sop_factory.py | executable | 记录完整 | 跳过执行 |

## Best Method Decision
- Selected method: Option B 固定分工+共享日历+周沟通
- Why this method is best under current constraints: 低沟通成本下实现稳定协同
- Rejected alternatives and reasons:
  - Option A: 任务丢失率高
  - Option C: 负载不均衡且不可持续

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 家庭分工表 | 责任明确 | 漏办率下降 >=30% | 初期维护成本 | 周更新一次 |
| 共享日历 | 时间协同 | 冲突减少 >=25% | 日历不同步 | 固定同步时点 |
| 周沟通清单 | 对齐机制 | 执行一致性提升 >=20% | 流于形式 | 限制议题数 |

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
