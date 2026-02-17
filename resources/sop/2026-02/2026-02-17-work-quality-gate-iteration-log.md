# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-06
- SOP ID: SOP-20260217-06
- SOP Name: 工作质量门禁与评审
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 52 minutes | 34 minutes | -18 minutes | <= 35 minutes per release review | pass |
| First-pass yield | 71% | 94% | +23 pp | >= 93 percent items pass gate on first review | pass |
| Rework rate | 27% | 9% | -18 pp | <= 10 percent items need second corrective pass | pass |
| Adoption rate | 47% | 100% | +53 pp | 100 percent releases pass this SOP | pass |

## Run Summary
- Total runs in window: 6
- Successful runs: 5
- Failed runs: 1
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no.
- Best Method drift detected: no.
- Best Tool drift detected: minor documentation completeness variance.
- Corrective action: run checklist before release section in every execution.

## Findings
- What improved: first-pass quality and traceability improved
- What degraded: one urgent release hit time cap
- Root causes: upstream requirement changed during review

## Rule Updates (1-3 only)
1. When (condition): intake record lacks mandatory field or threshold
   Then (strategy/model): block run and force mandatory-field completion
   Check: all mandatory fields are filled before step 2
   Avoid: guessing objective from ambiguous text
2. When (condition): hard-gate check fails at step 4
   Then (strategy/model): run one correction loop then re-validate
   Check: gate checklist is fully checked with evidence
   Avoid: promoting with unchecked gates
3. When (condition): rework rate exceeds target twice in same review window
   Then (strategy/model): tighten trigger threshold and simplify procedure branch
   Check: rework trend returns below threshold
   Avoid: adding extra steps without measurable gain

## Version Decision
- Current version: v1.1
- Proposed version: v1.2
- Change type: MINOR
- Why: gate wording and exception handling were calibrated after pilot runs.
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| Add one-line run summary snapshot to each execution record | yizhi | 2026-02-24 | 100% runs include summary line |
| Audit exception table coverage for top 3 failure signals | yizhi | 2026-02-24 | all failures map to predefined exception row |

## Links
- SOP document: resources/sop/2026-02/2026-02-17-work-quality-gate-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-work-quality-gate-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md