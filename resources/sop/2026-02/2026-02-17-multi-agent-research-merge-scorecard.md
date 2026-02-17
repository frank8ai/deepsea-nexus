# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-24
- SOP ID: SOP-20260217-24
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: Medium-risk decision support; must control noise; must handle conflicts; no irreversible external actions.

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | 4-role pipeline (Researcher/Critic/Builder/Synthesizer) with strict merge rules | Best breadth + conflict control |
| B | 2-role pipeline (Researcher + Synthesizer) | Faster but weak risk/critique |
| C | Single-pass deep research only | Deep but narrow; higher bias risk |

## Weighted Dimensions
| Dimension | Weight (0-1) | Why it matters |
|---|---:|---|
| Effectiveness | 0.35 | Finds best option under uncertainty |
| Cycle Time | 0.20 | Must fit 45-90m timebox |
| Error Prevention | 0.20 | Critic role reduces blind spots |
| Implementation Cost | 0.15 | Setup overhead should be low |
| Operational Risk | 0.10 | Prevents noisy/unsafe outputs |

## Scoring Table (1-5 for each dimension)
| Option | Effectiveness | Cycle Time | Error Prevention | Implementation Cost | Operational Risk | Weighted Score |
|---|---:|---:|---:|---:|---:|---:|
| A | 5 | 4 | 5 | 4 | 4 | 4.55 |
| B | 4 | 5 | 3 | 5 | 4 | 4.05 |
| C | 3 | 3 | 2 | 4 | 4 | 2.95 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| Parallel perspectives reduce bias | General decision hygiene | general practice | fewer blind spots | merge chaos |
| Conflict table + evidence weighting | Internal research SOP principles | internal principle | clearer decision | missing sources |

## Best Method Decision
- Selected method: Option A (4-role pipeline)
- Why this method is best under current constraints: adds critique and build tracks, while merge rules keep noise bounded.
- Rejected alternatives and reasons: B lacks independent critique; C is narrow and bias-prone.

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| Structured markdown schema | Normalization | >=30% faster merge | rigidity | allow appendix |
| Conflict table rule | Auditability | >=40% fewer hidden disagreements | extra work | timebox conflicts |
| validate_sop_factory.py --strict | Gate enforcement | >=40% fewer missing sections | false negatives | draft mode |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: A
- Winner weighted score: 4.55
- Runner-up weighted score: 4.05
- Margin: 0.50
- Override reason (required when margin < 0.20): n/a
- Approval: yizhi
- Effective from: 2026-02-17
