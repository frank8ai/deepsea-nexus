# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-42
- SOP ID: SOP-20260217-42
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 通过分层权限和可演练密钥体系降低单点失陷风险。

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 权限分层 -> 多签审批 -> 周期轮换 -> 应急演练。 | 在质量与效率间平衡 |
| B | 经验驱动快速执行 | 速度快但漏项风险高 |
| C | 重流程全量评审 | 风险低但成本高 |

## Weighted Dimensions
| Dimension | Weight (0-1) | Why it matters |
|---|---:|---|
| Effectiveness | 0.35 | Outcome quality and goal fit |
| Cycle Time | 0.20 | Throughput and speed |
| Error Prevention | 0.20 | Risk and defect reduction |
| Implementation Cost | 0.15 | Build and maintenance cost |
| Operational Risk | 0.10 | Stability and failure impact |

## Scoring Table (1-5 for each dimension)
| Option | Effectiveness | Cycle Time | Error Prevention | Implementation Cost | Operational Risk | Weighted Score |
|---|---:|---:|---:|---:|---:|---:|
| A | 5 | 4 | 5 | 4 | 4 | 4.55 |
| B | 3 | 5 | 3 | 5 | 3 | 3.70 |
| C | 4 | 2 | 4 | 2 | 5 | 3.50 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| 私钥管理必须去单点化并可演练恢复。 | Safe Docs:https://help.safe.global/en/ | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |
| 私钥管理必须去单点化并可演练恢复。 | NIST Key Management (SP 800-57):https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |

## Best Method Decision
- Selected method: Option A (权限分层 -> 多签审批 -> 周期轮换 -> 应急演练。)
- Why this method is best under current constraints: 在硬门禁约束下同时保证结果质量与执行效率。
- Rejected alternatives and reasons:
  - Option B: 关键风险识别不足，容易漏掉不可协商约束。
  - Option C: 过程过重，不适合高频执行。

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| Safe多签 | 核心执行 | 单点失陷风险下降 >=50%；权限违规下降 >=35% | 工具依赖增加 | 立即吊销异常密钥并切换应急签名组 |
| 指标看板 | 结果跟踪 | 主结果指标可视化覆盖 >=95% | 指标噪声 | 回退到核心指标集 |
| 校验脚本 | 结构门禁 | 漏项率下降 >=40% | 误报导致阻塞 | 草稿模式+人工复核 |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: A
- Winner weighted score: 4.55
- Runner-up weighted score: 3.70
- Margin: 0.85
- Override reason (required when margin < 0.20): n/a
- Approval: yizhi
- Effective from: 2026-02-17
