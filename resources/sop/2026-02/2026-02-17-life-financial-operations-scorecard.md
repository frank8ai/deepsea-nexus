# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-13
- SOP ID: SOP-20260217-13
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 减少现金流突发风险并控制超支

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 月末一次性核算 | 发现问题过晚 |
| B | 周度检查+阈值触发 | 可提前预警 |
| C | 完全自动化依赖工具 | 便利但解释性弱 |

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
| 预算与现金流管理 | https://www.consumerfinance.gov/consumer-tools/educator-tools/your-money-your-goals/toolkit/ | external guidance | 降低财务突发风险 | 仅记账不决策 |
| 记录留存 | https://www.irs.gov/tax-professionals/eitc-central/recordkeeping | external guidance | 提升可追溯性 | 记录缺失 |
| 阈值触发纠偏 | SOP_PRINCIPLES.md | policy | 快速止损 | 阈值失真 |

## Best Method Decision
- Selected method: Option B 周度检查+阈值触发
- Why this method is best under current constraints: 低管理成本下实现早预警与及时纠偏
- Rejected alternatives and reasons:
  - Option A: 问题发现过晚
  - Option C: 自动化错误难及时发现

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 预算表 | 偏差对比 | 超支率下降 >=20% | 分类不一致 | 固定分类字典 |
| 账单日历 | 到期管理 | 逾期率下降 >=30% | 更新延迟 | 周固定更新 |
| 异常清单 | 纠偏执行 | 响应速度提升 >=25% | 任务堆积 | 限制Top3异常 |

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
