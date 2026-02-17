# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-23
- SOP ID: SOP-20260217-23
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 在不明显增加日常成本下，降低数据丢失和账户风险

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 仅发生问题后处理 | 风险暴露高 |
| B | 定期备份+权限审计+密码策略 | 风险和成本平衡最佳 |
| C | 过度安全策略 | 安全高但可用性差 |

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
| 非可协商安全优先 | SOP_PRINCIPLES.md | policy | 控制高风险事件 | 执行阻力大 |
| 备份与恢复闭环 | agent/patterns/sop-factory.md | process | 提升可恢复性 | 备份不可恢复 |
| 严格校验门禁 | scripts/validate_sop_factory.py | executable | 结构可审计 | 运行遗漏 |

## Best Method Decision
- Selected method: Option B 定期备份+权限审计+密码策略
- Why this method is best under current constraints: 在可接受成本下显著降低安全与数据风险
- Rejected alternatives and reasons:
  - Option A: 问题发现滞后、损失不可控
  - Option C: 可用性下降导致执行失败

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 备份任务计划 | 数据保护 | 数据丢失风险下降 >=30% | 备份失效 | 月度恢复演练 |
| 权限审计清单 | 访问控制 | 过权风险下降 >=25% | 审计遗漏 | 双人复核 |
| 密码管理器 | 凭证管理 | 弱口令风险下降 >=30% | 主密钥风险 | 应急恢复方案 |

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
