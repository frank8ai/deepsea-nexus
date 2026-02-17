# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-06
- SOP ID: SOP-20260217-06
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 保证质量门禁通过且不牺牲关键时效

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 仅自检后发布 | 快速但风险偏高 |
| B | 自检+同行评审双门禁 | 质量最稳 |
| C | 自动化测试替代评审 | 维护成本高 |

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
| 质量先于速度 | SOP_PRINCIPLES.md | policy | 防止低质量上线 | 业务压力绕过门禁 |
| 关键步骤硬检查 | resources/sop/TEMPLATE.sop.md | template | 降低漏检率 | 检查项膨胀 |
| strict验证 | scripts/validate_sop_factory.py | executable | 发布一致性提升 | 仅形式验证 |

## Best Method Decision
- Selected method: Option B 双门禁（自检+同行评审）
- Why this method is best under current constraints: 在可接受成本下显著降低缺陷外溢
- Rejected alternatives and reasons:
  - Option A: 单点失误风险高
  - Option C: 自动化覆盖不足以替代评审

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 质量清单 | 门禁执行 | 漏检下降 >=30% | 清单过长 | 按风险分层 |
| 回归记录 | 证据沉淀 | 回归失败率下降 >=20% | 记录滞后 | 最小字段强制 |
| strict validator | 激活检查 | 激活错误下降 >=40% | 执行负担 | 合并批次校验 |

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
