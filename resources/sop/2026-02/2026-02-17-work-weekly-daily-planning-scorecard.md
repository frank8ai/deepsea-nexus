# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-04
- SOP ID: SOP-20260217-04
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 在有限工时下提高按周交付稳定性

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 仅待办清单驱动 | 优先级漂移大 |
| B | 周-日双层 + WIP控制 | 平衡执行率与灵活性 |
| C | 实时插队式计划 | 响应快但稳定性差 |

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
| 结果价值优先 | SOP_PRINCIPLES.md | policy | 聚焦高价值输出 | 目标定义不清 |
| WIP限制 | agent/patterns/sop-factory.md | process | 降低切换损耗 | 阈值设置不当 |
| strict校验 | scripts/validate_sop_factory.py | executable | 提升执行一致性 | 数据不完整 |

## Best Method Decision
- Selected method: Option B 周-日双层 + WIP控制
- Why this method is best under current constraints: 同时保证中期方向一致与日常执行稳定
- Rejected alternatives and reasons:
  - Option A: 无法抑制临时任务侵蚀
  - Option C: 不可预测性高，复盘价值低

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 周计划看板 | 周目标管理 | 完成率提升 >=20% | 维护成本 | 缩减字段 |
| 日历时间块 | 执行落地 | 延误率下降 >=25% | 计划过满 | 预留20%缓冲 |
| strict validator | 质量门禁 | 漏项率下降 >=30% | 严格度高 | 草稿迭代后激活 |

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
