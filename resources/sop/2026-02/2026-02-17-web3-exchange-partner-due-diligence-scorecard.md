# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-45
- SOP ID: SOP-20260217-45
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 在合作前识别法律、运营与安全风险，降低外部依赖失效冲击。

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 清单尽调 -> 风险分级 -> 缓解条件 -> 准入决策。 | 在质量与效率间平衡 |
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
| 合作准入必须通过分层尽调与风险评级。 | NIST SCRM:https://csrc.nist.gov/pubs/sp/800/161/r1/upd1/final | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |
| 合作准入必须通过分层尽调与风险评级。 | FATF Virtual Assets Guidance:https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Guidance-rba-virtual-assets-2021.html | source-backed | 降低关键失败风险 | 执行僵化或成本上升 |

## Best Method Decision
- Selected method: Option A (清单尽调 -> 风险分级 -> 缓解条件 -> 准入决策。)
- Why this method is best under current constraints: 在硬门禁约束下同时保证结果质量与执行效率。
- Rejected alternatives and reasons:
  - Option B: 关键风险识别不足，容易漏掉不可协商约束。
  - Option C: 过程过重，不适合高频执行。

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 尽调问卷 | 核心执行 | 高风险合作误入率下降 >=30%；准入效率提升 >=20% | 工具依赖增加 | 暂停合作签约并切换候选合作方 |
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
