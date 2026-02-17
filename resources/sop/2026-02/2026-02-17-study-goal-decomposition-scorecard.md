# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-08
- SOP ID: SOP-20260217-08
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: 将抽象学习目标转为可执行里程碑

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 只列主题不拆能力 | 难验收 |
| B | 技能树+里程碑+阈值 | 可执行性最高 |
| C | 按教材目录推进 | 个性化较弱 |

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
| 目标可测性 | SOP_PRINCIPLES.md | policy | 减少无效学习 | 指标设计失真 |
| 分层拆解 | agent/patterns/sop-factory.md | process | 提升计划稳定性 | 过度拆解 |
| 学习技术证据 | https://pubmed.ncbi.nlm.nih.gov/26173288/ | external research | 提升长期保持 | 只做形式化练习 |

## Best Method Decision
- Selected method: Option B 技能树+里程碑+阈值
- Why this method is best under current constraints: 同时满足可执行、可测量、可复盘
- Rejected alternatives and reasons:
  - Option A: 无法衡量阶段完成度
  - Option C: 难以匹配个人薄弱点

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| 学习目标卡 | 目标结构化 | 清晰度提升 >=30% | 填写成本 | 模板简化 |
| 进度表 | 周里程碑跟踪 | 偏差发现提前 >=25% | 维护惰性 | 周复盘强制更新 |
| strict validator | 发布门禁 | 漏项减少 >=35% | 严格度高 | 草稿迭代后发布 |

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
