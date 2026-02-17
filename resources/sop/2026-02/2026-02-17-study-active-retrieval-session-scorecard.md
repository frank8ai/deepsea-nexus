# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-09
- SOP ID: SOP-20260217-09
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 提升长期记忆并控制单次学习时长

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 直接重读笔记 | 保持率低 |
| B | 检索-纠错-重测 | 长期记忆效果最好 |
| C | 只刷题不复盘 | 迁移能力差 |

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
| 检索练习优于重读 | https://pubmed.ncbi.nlm.nih.gov/21252317/ | external research | 提升延迟保持 | 题目质量低 |
| Test-enhanced learning | https://pubmed.ncbi.nlm.nih.gov/16719566/ | external research | 提升长期回忆 | 缺少复盘 |
| 闭环记录 | agent/patterns/sop-factory.md | process | 可持续优化 | 记录中断 |

## Best Method Decision
- Selected method: Option B 检索-纠错-重测
- Why this method is best under current constraints: 在相同时长下带来更高长期记忆收益
- Rejected alternatives and reasons:
  - Option A: 容易产生熟悉感幻觉
  - Option C: 缺乏错因修正闭环

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 题库/闪卡 | 检索触发 | 回忆率提升 >=25% | 题目偏差 | 每周校准题库 |
| 计时器 | 节奏控制 | 单次效率提升 >=20% | 过度赶时 | 放宽窗口 |
| 会话日志 | 复盘证据 | 错因闭环率提升 >=30% | 记录懈怠 | 最小字段记录 |

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
