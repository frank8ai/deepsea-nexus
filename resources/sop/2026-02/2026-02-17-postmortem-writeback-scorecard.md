# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-23
- SOP ID: SOP-20260217-23
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: Low-risk internal writeback; no external side effects; must be reversible; must avoid sensitive content.

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 3-artifact writeback (facts card + rules + anti-pattern) | Balanced quality + low overhead |
| B | Rules-only writeback | Faster but loses traceability and anti-pattern capture |
| C | Full narrative postmortem only | Traceable but not reusable; hard to call next time |

## Weighted Dimensions
| Dimension | Weight (0-1) | Why it matters |
|---|---:|---|
| Effectiveness | 0.35 | Converts outcomes into reusable behavior |
| Cycle Time | 0.20 | Must be fast enough to run consistently |
| Error Prevention | 0.20 | Prevent repeat failures via anti-patterns |
| Implementation Cost | 0.15 | Minimal process overhead |
| Operational Risk | 0.10 | Avoids harmful writeback and secrets |

## Scoring Table (1-5 for each dimension)
| Option | Effectiveness | Cycle Time | Error Prevention | Implementation Cost | Operational Risk | Weighted Score |
|---|---:|---:|---:|---:|---:|---:|
| A | 5 | 4 | 5 | 4 | 5 | 4.65 |
| B | 3 | 5 | 2 | 5 | 4 | 3.45 |
| C | 2 | 2 | 2 | 2 | 5 | 2.45 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| Turn postmortems into rules | Internal deepsea-nexus patterns | internal best-practice | fewer repeat mistakes | rules too vague |
| Anti-pattern library | Engineering postmortem norms | general practice | faster detection and mitigation | not maintained |

## Best Method Decision
- Selected method: Option A (facts + rules + anti-pattern)
- Why this method is best under current constraints: high reuse and prevention with bounded overhead; retains traceability.
- Rejected alternatives and reasons: B loses anti-pattern + trace; C is not directly reusable.

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| Markdown templates | Structure consistency | >=30% drafting consistency | rigidity | keep appendix |
| validate_sop_factory.py --strict | Gate enforcement | >=40% fewer missing-section defects | false negatives | draft mode |
| grep checks | Link/field sanity | >=30% less review time | misses semantics | manual review |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: A
- Winner weighted score: 4.65
- Runner-up weighted score: 3.45
- Margin: 1.20
- Override reason (required when margin < 0.20): n/a
- Approval: yizhi
- Effective from: 2026-02-17
