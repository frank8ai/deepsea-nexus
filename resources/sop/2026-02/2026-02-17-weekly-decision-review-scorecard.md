# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-01
- SOP ID: SOP-20260217-01
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: complete rollout in one day, markdown-first, zero new paid tools.

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | Markdown checklist plus `rg` validation | Fastest rollout and low lock-in |
| B | Notion database workflow | Better UI, higher setup and migration cost |
| C | Scripted CLI validator | Highest automation, requires development time |

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
| A | 4 | 4 | 4 | 5 | 4 | 4.15 |
| B | 4 | 3 | 3 | 2 | 3 | 3.20 |
| C | 5 | 2 | 4 | 1 | 2 | 3.30 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| Hard gate before execution | internal decision card runs | observed rework reduction | fewer invalid starts | gate bypass by urgency |
| Limit rule updates to 1-3 | internal weekly reviews | decision latency reduction | stable change control | unresolved debt accumulates |
| Threshold-based triggers | internal model cards | better recall consistency | less subjective switching | threshold drift over time |

## Best Method Decision
- Selected method: Option A method with structured review checklist and threshold checks.
- Why this method is best under current constraints: fastest deploy path while preserving measurable controls.
- Rejected alternatives and reasons:
  - Option B: setup and tool migration cost exceeds current window.
  - Option C: automation benefit is high but not feasible in one-day rollout window.

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| Markdown templates | execution artifact | immediate standardization | manual consistency risk | keep template strict and reviewed |
| `rg` | field validation | fast presence checks | syntax misuse | fallback to manual checklist |
| `git` | version control | auditable iteration history | merge conflict | branch per cycle |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: A
- Winner weighted score: 4.15
- Runner-up weighted score: 3.30
- Margin: 0.85
- Override reason (required when margin < 0.20): n/a
- Approval: owner approved on 2026-02-17
- Effective from: 2026-02-17
