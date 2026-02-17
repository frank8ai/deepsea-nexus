# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-04
- SOP ID: SOP-20260217-04
- SOP Name: 工作周计划与日计划
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 37 minutes | 24 minutes | -13 minutes | <= 25 minutes per daily planning run | pass |
| First-pass yield | 72% | 91% | +19 pp | >= 90 percent planned critical tasks started on time | pass |
| Rework rate | 29% | 13% | -16 pp | <= 15 percent tasks rescheduled without rationale | pass |
| Adoption rate | 42% | 100% | +58 pp | 100 percent workdays start with plan record | pass |

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
- What improved: plan stability and on-time starts improved
- What degraded: one day had over-planning overhead
- Root causes: backlog pruning was delayed until mid-day

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
- SOP document: resources/sop/2026-02/2026-02-17-work-weekly-daily-planning-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-work-weekly-daily-planning-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md