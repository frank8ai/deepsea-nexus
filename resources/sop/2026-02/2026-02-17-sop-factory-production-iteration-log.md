# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-15
- SOP ID: SOP-20260217-15
- SOP Name: SOP Factory Production
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 145 min | 86 min | -59 min | <= 90 min | pass |
| First-pass yield | 58% | 91% | +33 pp | >= 90% | pass |
| Rework rate | 42% | 13% | -29 pp | <= 15% | pass |
| Adoption rate | 33% | 100% | +67 pp | 100% | pass |

## Run Summary
- Total runs in window: 6
- Successful runs: 5
- Failed runs: 1
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no.
- Best Method drift detected: no.
- Best Tool drift detected: minor omissions in initial evidence links.
- Corrective action: make source-link check mandatory before strict validation.

## Findings
- What improved: release quality and repeatability improved with hard gates plus strict validator.
- What degraded: one run exceeded cycle-time target due to missing baseline samples.
- Root causes: intake discipline was inconsistent before mandatory baseline gate.

## Rule Updates (1-3 only)
1. When (condition): IF task frequency is below 3 per month OR process variance CV is above 0.20,
   Then (strategy/model): keep the item in Decision Card mode instead of SOP Factory mode,
   Check: are frequency and CV values explicitly recorded,
   Avoid: forcing unstable work into SOP too early.
2. When (condition): IF SOP has reversibility class R2 or R3 and evidence tier is below minimum mapping,
   Then (strategy/model): block activation and require evidence upgrade before release,
   Check: does R/E mapping satisfy R1->E2, R2->E3, R3->E4,
   Avoid: publishing high-impact SOP on weak evidence.
3. When (condition): IF strict validator fails on any gate or reference path,
   Then (strategy/model): apply one focused correction loop and rerun strict validation,
   Check: is validator exit code 0 before active release,
   Avoid: manual approval override without machine-verifiable pass.

## Version Decision
- Current version: v1.0
- Proposed version: v1.1
- Change type: MINOR
- Why: strengthened routing and evidence gates after pilot failures.
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| Add CV computation snippet to baseline capture checklist | yizhi | 2026-02-24 | 100% SOP candidates include CV field |
| Add release note line for strict validator command output | yizhi | 2026-02-24 | every active SOP includes validation evidence |

## Links
- SOP document: `resources/sop/2026-02/2026-02-17-sop-factory-production-sop.md`
- Scorecard: `resources/sop/2026-02/2026-02-17-sop-factory-production-scorecard.md`
- Related decision cards: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
