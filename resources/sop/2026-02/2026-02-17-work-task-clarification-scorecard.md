# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-03
- SOP ID: SOP-20260217-03
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 20分钟内完成澄清并将返工风险前置

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 单轮口头澄清 | 速度快但遗漏率高 |
| B | 双轮澄清卡 + 硬门槛 | 质量稳定，可追溯 |
| C | 先执行后补澄清 | 返工风险最高 |

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
| 目标先行且可量化 | SOP_PRINCIPLES.md | policy | 降低返工和误解 | 指标过虚导致无法验收 |
| 必填约束与非目标 | resources/sop/TEMPLATE.sop.md | template | 防止范围失控 | 约束遗漏引发延期 |
| strict release gate | scripts/validate_sop_factory.py | executable | 拦截不完整SOP | 未执行校验导致漏项 |

## Best Method Decision
- Selected method: Option B 双轮澄清卡 + 硬门槛
- Why this method is best under current constraints: 在可控时间内显著降低需求歧义与后续返工
- Rejected alternatives and reasons:
  - Option A: 关键字段缺失概率高
  - Option C: 风险后置到成本更高阶段

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 澄清卡模板 | 结构化输入 | 返工率下降 >=30% | 过度模板化 | 增加备注区 |
| strict validator | 发布门禁 | 漏项率下降 >=40% | 执行成本增加 | 草稿先宽后严 |
| issue 看板 | 路由与追踪 | 状态可见性提升 >=30% | 维护不及时 | 每日收盘更新 |

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
