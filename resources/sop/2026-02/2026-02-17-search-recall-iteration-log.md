# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-02
- SOP ID: SOP-20260217-02
- SOP Name: Search Recall Execution
- Owner: yizhi
- Review window: 2026-02-10 to 2026-02-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 108 sec | 74 sec | -34 sec | <= 90 sec | pass |
| First-pass yield | 70% | 87% | +17 pp | >= 85% | pass |
| Rework rate | 30% | 13% | -17 pp | <= 15% | pass |
| Adoption rate | 45% | 100% | +55 pp | 100% | pass |

## Run Summary
- Total runs in window: 8
- Successful runs: 7
- Failed runs: 1
- Major incident count: 0

## Principle Drift Check
- Best Practice drift detected: no.
- Best Method drift detected: no.
- Best Tool drift detected: minor variability from trigger-only phrasing.
- Corrective action: keep two-pass path as default when first-pass gate fails.

## Findings
- What improved: relevance gate pass rate and source consistency improved after two-pass strategy.
- What degraded: one long query exceeded latency threshold due to repeated refinement.
- Root causes: ambiguous intent text without domain anchor increased expansion retries.

## Rule Updates (1-3 only)
1. When (condition): IF top1 relevance < 0.35 OR top3 median < 0.25 in first pass,
   Then (strategy/model): execute second-pass expansion with up to 2 rewritten queries and n=8,
   Check: does second pass produce at least one result meeting gate,
   Avoid: returning weak first-pass results directly.
2. When (condition): IF health check fails OR docs count is 0,
   Then (strategy/model): block retrieval and return explicit readiness response,
   Check: did health and stats run before search,
   Avoid: silent empty results.
3. When (condition): IF low-relevance outcome repeats 3 times in one cycle,
   Then (strategy/model): force query clarification prompt before next retrieval,
   Check: is clarification adding domain or timeframe anchors,
   Avoid: repeated blind retries.

## Version Decision
- Current version: v1.0
- Proposed version: v1.1
- Change type: MINOR
- Why: thresholded second-pass behavior and escalation rules were clarified.
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| Add latency percentile line (p95) to weekly record | yizhi | 2026-02-24 | p95 tracked for every run |
| Add query-intent label audit in logs | yizhi | 2026-02-24 | 100% runs include intent label |

## Links
- SOP document: `resources/sop/2026-02/2026-02-17-search-recall-sop.md`
- Scorecard: `resources/sop/2026-02/2026-02-17-search-recall-scorecard.md`
- Related decision cards: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
