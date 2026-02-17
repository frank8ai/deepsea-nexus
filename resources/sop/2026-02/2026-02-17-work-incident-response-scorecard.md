# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-07
- SOP ID: SOP-20260217-07
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 高压场景下先控风险再恢复

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 先修复后补分级 | 速度快但风险不可控 |
| B | 分级驱动标准流程 | 风险与效率平衡 |
| C | 全量最高级处理 | 安全但资源浪费 |

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
| 事件生命周期管理 | https://csrc.nist.gov/projects/incident-response | external standard | 统一响应节奏 | 机械执行忽略上下文 |
| 非可协商约束优先 | SOP_PRINCIPLES.md | policy | 防止高风险误操作 | 过慢影响恢复 |
| strict校验 | scripts/validate_sop_factory.py | executable | 可验证追溯 | 演练不足 |

## Best Method Decision
- Selected method: Option B 分级驱动标准流程
- Why this method is best under current constraints: 能稳定压制风险扩散并保持恢复节奏
- Rejected alternatives and reasons:
  - Option A: 高概率遗漏关键风险信息
  - Option C: 资源消耗过高且不可持续

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 事件模板 | 统一记录 | 响应一致性提升 >=30% | 填写延迟 | 最小字段先行 |
| 严重度矩阵 | 快速分级 | 分级正确率提升 >=25% | 规则僵化 | 手工override并复盘 |
| strict validator | 规则门禁 | 漏项下降 >=35% | 执行压力 | 合并评审时运行 |

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
