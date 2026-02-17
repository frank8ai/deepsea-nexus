# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-12
- SOP ID: SOP-20260217-12
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 在低管理成本下稳定健康行为

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 随机执行健康行为 | 不稳定 |
| B | 基线目标+日追踪+纠偏 | 稳定性最高 |
| C | 一次性高强度计划 | 易中断 |

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
| 运动基线 | https://www.cdc.gov/physical-activity-basics/guidelines/index.html | external guidance | 建立运动底线 | 目标过高中断 |
| 睡眠基线 | https://www.cdc.gov/sleep/about/index.html | external guidance | 提升恢复质量 | 作息不可持续 |
| 结果闭环 | SOP_PRINCIPLES.md | policy | 提升长期执行率 | 只打卡不调整 |

## Best Method Decision
- Selected method: Option B 基线目标+日追踪+纠偏
- Why this method is best under current constraints: 可持续、可监控、可快速纠偏
- Rejected alternatives and reasons:
  - Option A: 难形成稳定习惯
  - Option C: 波动大且复发率高

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 基线目标表 | 目标定义 | 清晰度提升 >=30% | 设定失真 | 每周校准 |
| 日追踪打卡 | 执行监控 | 连续执行率提升 >=25% | 打卡疲劳 | 仅跟踪关键项 |
| 周复盘模板 | 调整闭环 | 恢复速度提升 >=20% | 流于形式 | 强制1-3规则 |

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
