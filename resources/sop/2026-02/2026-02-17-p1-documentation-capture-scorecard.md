# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-17
- SOP ID: SOP-20260217-17
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 提高知识沉淀速度并降低关键信息丢失

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 事后集中补文档 | 容易遗漏细节 |
| B | 决策后24小时内结构化沉淀 | 准确度和时效最好 |
| C | 完全自由格式记录 | 可读性和检索性差 |

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
| Link over paste | SOP_PRINCIPLES.md | policy | 降低上下文膨胀 | 关键信息缺链接 |
| 模板化沉淀 | resources/sop/TEMPLATE.sop.md | template | 提升复用率 | 模板僵化 |
| 严格路径校验 | scripts/validate_sop_factory.py | executable | 提高可检索性 | 引用路径错误 |

## Best Method Decision
- Selected method: Option B 决策后24小时内结构化沉淀
- Why this method is best under current constraints: 在准确性仍高的窗口内沉淀，复用成本最低
- Rejected alternatives and reasons:
  - Option A: 记忆衰减导致质量下降
  - Option C: 难以形成统一检索

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 沉淀模板 | 结构规范 | 复用率提升 >=30% | 过度格式化 | 增加自由备注区 |
| 标签规范 | 检索召回 | 检索命中率提升 >=25% | 标签泛滥 | 标签白名单 |
| 路径校验脚本 | 质量门禁 | 失链率下降 >=30% | 执行遗漏 | 发布前强制校验 |

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
