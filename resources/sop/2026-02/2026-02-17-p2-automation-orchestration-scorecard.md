# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-24
- SOP ID: SOP-20260217-24
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 自动化必须可回滚、可观测、可降级

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 手工重复执行 | 低工程成本但效率低 |
| B | 脚本化自动化+告警+回滚 | 平衡质量与速度最佳 |
| C | 全自动无人值守 | 复杂度和风险高 |

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
| 可逆性决定速度 | SOP_PRINCIPLES.md | policy | 降低自动化事故风险 | 过度保守 |
| 工厂门禁 | agent/patterns/sop-factory.md | process | 控制上线质量 | 覆盖不足 |
| strict校验 | scripts/validate_sop_factory.py | executable | 保证结构合规 | 执行遗漏 |

## Best Method Decision
- Selected method: Option B 脚本化自动化+告警+回滚
- Why this method is best under current constraints: 在可控复杂度下显著提升效率且可止损
- Rejected alternatives and reasons:
  - Option A: 重复劳动高且易出错
  - Option C: 缺乏人审门槛风险过高

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 自动化脚本 | 执行引擎 | 人工工时下降 >=30% | 脚本缺陷 | 快速回滚脚本 |
| 告警规则 | 风险探测 | 异常发现提前 >=25% | 告警噪声 | 阈值调优 |
| 回滚手册 | 止损路径 | 恢复时间下降 >=20% | 手册过时 | 周度演练 |

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
