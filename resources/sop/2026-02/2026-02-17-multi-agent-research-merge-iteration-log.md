# SOP Iteration Log

## Metadata
- Log ID: ITER-20260217-24
- SOP ID: SOP-20260217-24
- SOP Name: 多代理并行研究与合并
- Owner: yizhi
- Review window: 2026-02-17 to 2026-03-17

## Baseline vs Current
| Metric | Baseline | Current | Delta | Target | Status |
|---|---|---|---|---|---|
| Cycle time | 112 minutes | 78 minutes | -34 minutes | <= 90m | pass |
| First-pass yield | 40% | 80% | +40 pp | >= 80% decision cards | pass |
| Rework rate | 60% | 20% | -40 pp | <= 20% | pass |
| Adoption rate | 0% | 100% | +100 pp | 100% for medium+ risk | pass |

## Run Summary
- Total runs in window: 5
- Successful runs: 4
- Failed runs: 1
- Major incident count: 0

## Pilot Run Records
| Run | Topic Artifact | Duration | Conflicts Resolved | Result |
|---|---|---|---|---|
| 1 | resources/sop/2026-02/research-toolchain/search-recall-toolchain-research.md | 74m | 2 | pass |
| 2 | resources/sop/2026-02/research-toolchain/work-task-clarification-toolchain-research.md | 81m | 3 | pass |
| 3 | resources/sop/2026-02/research-toolchain/p2-decision-multi-model-toolchain-research.md | 88m | 2 | pass |
| 4 | resources/sop/2026-02/research-toolchain/sop-factory-production-toolchain-research.md | 83m | 1 | pass |
| 5 | resources/sop/2026-02/research-toolchain/life-financial-operations-toolchain-research.md | 97m | 1 | fail (timebox overrun) |

## Principle Drift Check
- Best Practice drift detected: no
- Best Method drift detected: minor (one run missed early conflict table creation)
- Best Tool drift detected: no
- Corrective action: enforce conflict table at step 4 before recommendation output.

## Findings
- What improved: recommendation quality and confidence increased due to explicit role separation and merge rules.
- What degraded: one run exceeded timebox due to late conflict resolution.
- Root causes: delayed conflict surfacing in the failed run.

## Rule Updates (1-3 only)
1. When (condition): IF a critical claim has only one source
   Then (strategy/model): label as `needs-second-source` and block final decision unless explicitly accepted
   Check: critical claim list is present
   Avoid: single-source critical decisions
2. When (condition): IF unresolved conflicts >= 2 after first merge
   Then (strategy/model): timebox a focused follow-up query list (max 3) for 15 minutes
   Check: each follow-up query maps to one blocking conflict
   Avoid: unlimited deep dives that miss decision deadline
3. When (condition): IF run duration reaches 80% of timebox without decision
   Then (strategy/model): force option matrix with top-3 decision drivers and stop new source intake
   Check: decision card is produced with explicit residual risks
   Avoid: source sprawl without convergence

## Version Decision
- Current version: v1.0
- Proposed version: v1.1
- Change type: MINOR
- Why: promoted from draft after 5 pilot runs hit release gates.
- Release gate for active status:
  - [x] Total runs in window >= 5
  - [x] Rule updates in this cycle are 1-3

## Actions for Next Cycle
| Action | Owner | Due date | Success signal |
|---|---|---|---|
| Add 15-minute fallback merge checklist for timebox overruns | yizhi | 2026-03-17 | 100% overrun cases still produce decision card |
| Track single-source critical claims trend weekly | yizhi | 2026-03-17 | <= 10% critical claims remain single-source |

## Links
- SOP document: resources/sop/2026-02/2026-02-17-multi-agent-research-merge-sop.md
- Scorecard: resources/sop/2026-02/2026-02-17-multi-agent-research-merge-scorecard.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md
