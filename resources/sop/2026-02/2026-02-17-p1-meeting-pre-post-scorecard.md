# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-16
- SOP ID: SOP-20260217-16
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 确保会议有目标、有结论、有行动闭环

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 仅会中讨论 | 准备不足且会后易失焦 |
| B | 会前目标+会中控时+会后行动闭环 | 质量与效率平衡最佳 |
| C | 全靠会后补记录 | 责任不清、追踪困难 |

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
| 会前目标定义 | SOP_PRINCIPLES.md | policy | 提升决策效率 | 目标过宽 |
| 行动项闭环 | agent/patterns/sop-factory.md | process | 降低会议空转 | 责任人不明确 |
| strict gate | scripts/validate_sop_factory.py | executable | 防止漏项发布 | 跳过校验 |

## Best Method Decision
- Selected method: Option B 会前目标+会中控时+会后行动闭环
- Why this method is best under current constraints: 在不增加太多准备成本下显著提升会议产出质量
- Rejected alternatives and reasons:
  - Option A: 会后返工和分歧增加
  - Option C: 缺乏实时决策约束

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 会议议程模板 | 会前对齐 | 议程偏移下降 >=30% | 准备不足 | 固定最小模板 |
| 计时器 | 会中控时 | 超时率下降 >=25% | 讨论被截断 | 关键议题延时机制 |
| 行动项看板 | 会后追踪 | 完成率提升 >=30% | 更新不及时 | 每日收盘更新 |

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
