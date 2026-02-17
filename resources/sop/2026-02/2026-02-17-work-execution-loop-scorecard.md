# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-05
- SOP ID: SOP-20260217-05
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 降低阻塞停滞并提升回路完成率

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 长时段批处理执行 | 深度高但反馈慢 |
| B | 短回路执行 + 状态闭环 | 反馈快且可控 |
| C | 完全按中断驱动 | 反应快但产出不稳定 |

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
| 状态可见化 | agent/patterns/sop-factory.md | process | 缩短停滞时间 | 状态更新不及时 |
| 结果优先于忙碌 | SOP_PRINCIPLES.md | policy | 提升有效产出比 | 指标偏差 |
| strict校验 | scripts/validate_sop_factory.py | executable | 减少发布前漏项 | 形式合规 |

## Best Method Decision
- Selected method: Option B 短回路执行 + 状态闭环
- Why this method is best under current constraints: 在保持节奏的同时最小化阻塞放大
- Rejected alternatives and reasons:
  - Option A: 问题暴露延迟
  - Option C: 容易被外部噪声驱动

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 状态看板 | 状态一致性 | 阻塞可见性提升 >=30% | 维护延迟 | 每日两次刷新 |
| 阻塞升级清单 | 风险止损 | 阻塞时长下降 >=25% | 过度升级 | 设升级阈值 |
| strict validator | 门禁 | 变更质量稳定 | 额外开销 | 批量校验 |

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
