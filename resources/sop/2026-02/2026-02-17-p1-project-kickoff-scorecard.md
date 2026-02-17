# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-18
- SOP ID: SOP-20260217-18
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 启动阶段需同步范围、风险、依赖，避免后期返工

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 直接开工后补启动文档 | 短期快，后期返工多 |
| B | 启动会+范围风险依赖清单 | 启动质量最佳 |
| C | 长周期前期论证 | 质量高但启动慢 |

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
| 非可协商约束优先 | SOP_PRINCIPLES.md | policy | 减少高风险遗漏 | 过度保守 |
| 基线与门禁 | agent/patterns/sop-factory.md | process | 启动可控 | 基线采样不足 |
| strict门禁 | scripts/validate_sop_factory.py | executable | 激活一致性 | 仅形式通过 |

## Best Method Decision
- Selected method: Option B 启动会+范围风险依赖清单
- Why this method is best under current constraints: 兼顾启动速度与后续稳定性
- Rejected alternatives and reasons:
  - Option A: 后续范围漂移明显
  - Option C: 前期成本超预算

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 启动清单模板 | 启动标准化 | 漏项率下降 >=30% | 模板过长 | 核心字段优先 |
| 风险矩阵 | 风险识别 | 重大风险提前发现 >=25% | 评分主观 | 双人复核 |
| 依赖图 | 依赖透明化 | 延误预警提前 >=20% | 维护成本 | 周更新一次 |

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
