# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-01
- SOP ID: SOP-20260217-01
- SOP Name: Weekly Decision Review and Rule Update
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 52 min | 28 min | -24 min | <= 30 min | pass |
| First-pass yield | 68% | 92% | +24 pp | >= 90% | pass |
| Rework rate | 31% | 12% | -19 pp | <= 10% | close |
| Adoption rate | 40% | 100% | +60 pp | 100% | pass |

## Run Summary
- Total runs in window: 6
- Successful runs: 5
- Failed runs: 1
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no.
- Best Method drift detected: no.
- Best Tool drift detected: minor risk from manual naming consistency.
- Corrective action: add validator check before release and enforce naming regex.

## Findings
- What improved: review speed and gate compliance improved materially.
- What degraded: one run exceeded time limit due to rule conflict resolution.
- Root causes: missing owner mapping for draft rules created decision delay.

## Rule Updates (1-3 only)
1. When (condition): IF 2 or more draft rules target the same signal,
   Then (strategy/model): merge before activation and keep one active rule owner,
   Check: does merged rule preserve threshold clarity,
   Avoid: activating competing rules in same cycle.
2. When (condition): IF review run exceeds 30 minutes before step 5,
   Then (strategy/model): prioritize top-risk cards and defer low-risk cards,
   Check: are deferred cards logged with next due date,
   Avoid: partial updates without trace.
3. When (condition): IF rework rate stays above 10 percent for 2 cycles,
   Then (strategy/model): tighten hard-gate checklist and retrain owners,
   Check: which fields fail most often,
   Avoid: adding new tools before process stability.

## Version Decision
- Current version: v1.0
- Proposed version: v1.1
- Change type: MINOR
- Why: threshold handling and draft rule ownership were clarified without structural process changes.
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| Add owner field for each draft rule | yizhi | 2026-02-24 | zero unowned draft rules |
| Add deferred-card queue section to weekly log | yizhi | 2026-02-24 | 100% deferred cards have due dates |

## Links
- SOP document: `resources/sop/2026-02/2026-02-17-weekly-decision-review-sop.md`
- Scorecard: `resources/sop/2026-02/2026-02-17-weekly-decision-review-scorecard.md`
- Related decision cards: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
