# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-25
- SOP ID: SOP-20260217-25
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 高影响决策必须多模型交叉且可追责

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 单模型直觉决策 | 速度快但盲区大 |
| B | 三模型对比+风险矩阵 | 质量与效率最平衡 |
| C | 全模型穷举 | 成本过高 |

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
| 证据强度随风险升级 | SOP_PRINCIPLES.md | policy | 降低高风险误判 | 决策过慢 |
| Decision Card门禁 | resources/decisions/TEMPLATE.decision-card.md | template | 提高可追溯性 | 填写流于形式 |
| strict校验 | scripts/validate_sop_factory.py | executable | 保证SOP结构稳定 | 忽略决策内容质量 |

## Best Method Decision
- Selected method: Option B 三模型对比+风险矩阵
- Why this method is best under current constraints: 在可接受时间内显著降低视角盲区
- Rejected alternatives and reasons:
  - Option A: 关键风险容易漏判
  - Option C: 分析成本超过收益

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 决策卡模板 | 结构化决策 | 漏项率下降 >=30% | 模板疲劳 | 精简字段 |
| 多模型对比表 | 交叉检验 | 风险识别率提升 >=25% | 评分主观 | 双人复核 |
| 风险矩阵 | 风险分层 | 止损速度提升 >=20% | 阈值失真 | 周期校准 |

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
