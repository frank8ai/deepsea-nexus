# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-29
- SOP ID: SOP-20260217-29
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 高压事件处置必须先止损再沟通再恢复

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 临场经验驱动 | 速度快但一致性差 |
| B | 危机分级+沟通模板+恢复清单 | 稳定且可复盘 |
| C | 全部升级最高级响应 | 安全但资源消耗过高 |

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
| 非可协商约束优先 | SOP_PRINCIPLES.md | policy | 控制高风险扩散 | 反应过慢 |
| 反馈回路闭环 | agent/patterns/sop-factory.md | process | 提升恢复质量 | 复盘不充分 |
| strict校验 | scripts/validate_sop_factory.py | executable | 流程完整性保障 | 忽略现场变化 |

## Best Method Decision
- Selected method: Option B 危机分级+沟通模板+恢复清单
- Why this method is best under current constraints: 在高压环境下提供稳定执行骨架并保留应变空间
- Rejected alternatives and reasons:
  - Option A: 经验不可复制且遗漏率高
  - Option C: 资源占用过大影响恢复

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 事件分级表 | 决策分流 | 分级正确率提升 >=25% | 规则僵化 | 允许人工override |
| 危机沟通模板 | 沟通一致性 | 信息偏差下降 >=30% | 话术僵硬 | 现场补充说明 |
| 恢复检查清单 | 恢复闭环 | 恢复时间下降 >=20% | 清单过长 | 关键项优先 |

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
