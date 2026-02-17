# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-15
- SOP ID: SOP-20260217-15
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: produce or upgrade SOP in one cycle while meeting strict gates and R/E mapping.

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | Template-first quick authoring | fast, but weak on evidence depth and drift control |
| B | Evidence-driven six-step SOP factory | balanced speed, quality, and governance |
| C | Automation-heavy generation pipeline | scalable, but complexity and lock-in risk are high |

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
| B | 5 | 4 | 5 | 4 | 4 | 4.55 |
| C | 4 | 3 | 4 | 2 | 3 | 3.40 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| Non-compensatory standard stack | `agent/patterns/sop-factory.md` | governance policy | avoid trading safety for speed | teams skip top-priority constraints |
| Mandatory hard gates and release checks | `resources/sop/TEMPLATE.sop.md` | template control | consistent minimum quality | fake completion without evidence links |
| Strict machine validation with R/E mapping | `scripts/validate_sop_factory.py` | executable control | enforce objective compliance | bypass if command not run in release flow |

## Best Method Decision
- Selected method: Option B evidence-driven six-step SOP factory.
- Why this method is best under current constraints: it enforces highest-standard ordering, keeps cycle time practical, and prevents low-evidence activation.
- Rejected alternatives and reasons:
  - Option A: too dependent on writer discipline and weak against quality drift.
  - Option C: tool-chain complexity is unnecessary for current SOP volume.

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| Markdown templates | artifact standardization | >=30% drafting consistency gain | rigid wording | keep custom notes in appendix |
| `validate_sop_factory.py --strict` | release gate enforcement | >=40% reduction in gate-miss defects | strictness fatigue | keep draft mode until pilot is complete |
| `rg` | fast field and path checks | >=30% reduction in manual review time | search misuse | manual section-by-section review |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: B
- Winner weighted score: 4.55
- Runner-up weighted score: 3.80
- Margin: 0.75
- Override reason (required when margin < 0.20): n/a
- Approval: owner approved on 2026-02-17
- Effective from: 2026-02-17
