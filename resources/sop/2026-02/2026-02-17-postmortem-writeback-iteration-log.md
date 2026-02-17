# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-23
- SOP ID: SOP-20260217-23
- SOP Name: 复盘写回（规则库/反例库）
- Owner: yizhi
- Review window: 2026-02-17 to 2026-03-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | TBD | TBD | TBD | <= 30m | draft |
| First-pass yield | TBD | TBD | TBD | >= 90% | draft |
| Rework rate | TBD | TBD | TBD | <= 10% | draft |
| Adoption rate | TBD | TBD | TBD | 100% for P0/P1 | draft |

## Run Summary
- Total runs in window: 0
- Successful runs: 0
- Failed runs: 0
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no
- Best Method drift detected: no
- Best Tool drift detected: no
- Corrective action: n/a

## Findings
- What improved: n/a
- What degraded: n/a
- Root causes: n/a

## Rule Updates (1-3 only)
1. When (condition): IF outcome evidence is missing
   Then (strategy/model): define proxy metric and set `confidence=low` with `review_at`
   Check: proxy metric is measurable within 7 days
   Avoid: subjective-only conclusions

## Version Decision
- Current version: v1.0
- Proposed version: v1.0
- Change type: MINOR
- Why: initial release
- Release gate for active status:
  - [ ] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| Pilot 5 postmortems using this SOP | yizhi | 2026-03-17 | logged >= 5 runs |

## Links
- SOP document: resources/sop/2026-02/2026-02-17-postmortem-writeback-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-postmortem-writeback-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md
