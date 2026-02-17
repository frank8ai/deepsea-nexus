# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-13
- SOP ID: SOP-20260217-13
- SOP Name: 生活财务运行
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 47 minutes | 29 minutes | -18 minutes | <= 30 minutes per weekly finance run | pass |
| First-pass yield | 74% | 96% | +22 pp | >= 95 percent bills tracked before due date | pass |
| Rework rate | 23% | 9% | -14 pp | <= 10 percent spending categories exceed plan | pass |
| Adoption rate | 52% | 100% | +48 pp | 100 percent weeks include finance log | pass |

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
- What improved: bill readiness and cash visibility improved
- What degraded: one category overspent in pilot
- Root causes: late transaction import caused temporary mismatch

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
- SOP document: resources/sop/2026-02/2026-02-17-life-financial-operations-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-life-financial-operations-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md