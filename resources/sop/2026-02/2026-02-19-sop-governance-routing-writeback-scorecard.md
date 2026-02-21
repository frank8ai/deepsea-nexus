# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260219-02
- SOP ID: SOP-20260219-02
- Date: 2026-02-19
- Owner: yizhi
- Constraints summary: keep HQ lightweight, keep Nexus canonical, force writeback assets, and keep rollback simple.

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | HQ as canonical authority and Nexus as mirror | Fast local edits but increases duplication risk |
| B | HQ as execution entry and Nexus as canonical authority | Clear ownership and lower drift risk |
| C | HQ and Nexus dual-authority | Highest flexibility but split-brain risk |

## Weighted Dimensions
| Dimension | Weight (0-1) | Why it matters |
|---|---|---|
| Effectiveness | 0.35 | Governance quality and consistency |
| Cycle Time | 0.20 | Decision and rollout speed |
| Error Prevention | 0.20 | Drift/duplication prevention |
| Implementation Cost | 0.15 | Setup and maintenance burden |
| Operational Risk | 0.10 | Long-term stability |

## Scoring Table (1-5 for each dimension)
| Option | Effectiveness | Cycle Time | Error Prevention | Implementation Cost | Operational Risk | Weighted Score |
|---|---|---|---|---|---|---|
| A | 3.70 | 4.10 | 3.10 | 3.80 | 3.20 | 3.62 |
| B | 4.70 | 4.30 | 4.80 | 3.90 | 4.40 | 4.50 |
| C | 3.10 | 2.90 | 2.10 | 2.50 | 2.00 | 2.63 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| HQ as entry and Nexus as canonical source | SOP/SOP_INDEX.md and resources/sop governance bundle | Internal governance evidence | Reduce duplicate SOP edits and retrieval ambiguity | Pointer links become stale |
| Mandatory assetized writeback after each run | 2026-02-19 governance SOP procedure step 5 | Internal process evidence | Increase compounding reuse and fewer repeated mistakes | Team skips writeback under time pressure |
| Unified KPI/stop fields across SOPs | `scripts/validate_sop_factory.py` strict checks | Tool-enforced evidence | Faster quality gating and consistent release decisions | KPI fields filled but not reviewed |

## Best Method Decision
- Selected method: Option B (HQ entry + Nexus canonical authority)
- Why this method is best under current constraints: preserves fast execution entry while keeping one authoritative full-fidelity SOP library and avoiding split-brain updates.
- Rejected alternatives and reasons:
  - A rejected because HQ would become heavy and duplicate canonical governance artifacts.
  - C rejected because dual authority creates frequent conflict and expensive reconciliation.

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| SOP pointer entry in HQ | Fast operator access | Routing decision latency down >= 30% | Pointer drift | Restore previous pointer mapping from git |
| Nexus canonical triplet (`sop`, `scorecard`, `iteration-log`) | Single source of truth | Duplicate-governance incidents down >= 60% | Canonical doc not updated in time | Revert to last active canonical version |
| `validate_sop_factory.py --strict` | Enforce release gates | Section/gate misses down >= 70% | False confidence without review rhythm | Keep weekly manual review checklist |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: B
- Winner weighted score: 4.50
- Runner-up weighted score: 3.62
- Margin: 0.88
- Override reason (required when margin < 0.20): n/a
- Approval: approved
- Effective from: 2026-02-19
