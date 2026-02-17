# SOP Three-Optimal Scorecard

## Metadata
- Scorecard ID: SCORE-20260217-02
- SOP ID: SOP-20260217-02
- Date: 2026-02-17
- Owner: yizhi
- Constraints summary: keep latency under 90s end-to-end while improving relevance gate pass rate.

## Candidate Options
| Option | Description | Notes |
|---|---|---|
| A | Single-pass direct `nexus_recall` | fastest path, lower recovery power on weak queries |
| B | Two-pass query expansion plus rerank | stronger quality under ambiguous queries |
| C | Trigger-driven `smart_search` only | low setup effort, less deterministic on edge cases |

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
| B | 5 | 4 | 5 | 3 | 4 | 4.40 |
| C | 4 | 3 | 4 | 4 | 3 | 3.70 |

## Calculation Rule
- Weighted Score = sum(score * weight)
- Highest weighted score wins only if hard constraints pass.
- Release thresholds:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or explicit override reason.

## Best Practice Evidence
| Practice | Source | Evidence Type | Expected Benefit | Failure Mode |
|---|---|---|---|---|
| Relevance-ranked semantic recall | `nexus_core.py` search_recall path | implementation behavior | stable source-linked ranking | low-confidence results on ambiguous queries |
| Trigger-aware search mode | `nexus_core.py` smart_search | internal functional path | better intent routing for memory queries | trigger miss for atypical phrasing |
| Cache-backed recall | `_cached_search` in `nexus_core.py` | code path observation | lower repeated-query latency | stale expectations if query quality is low |

## Best Method Decision
- Selected method: Option B two-pass query expansion and rerank.
- Why this method is best under current constraints: materially improves relevance gate pass rate while staying within latency target.
- Rejected alternatives and reasons:
  - Option A: high speed but weaker recovery on unclear or short queries.
  - Option C: useful fallback but less deterministic for strict quality gates.

## Best Tool Decision
| Tool | Role | Measured Gain | Risk | Rollback Path |
|---|---|---|---|---|
| `nexus_recall` | primary retrieval | consistent baseline retrieval | weak on ambiguous query phrasing | fallback to single-pass only |
| `smart_search` | expansion and trigger handling | improved first relevant hit rate | trigger sensitivity variance | disable expansion path |
| `rg` | source/path verification | fast local evidence validation | operator misuse | manual source check |

## Hard Constraint Check
- [x] Budget constraint passed.
- [x] Time constraint passed.
- [x] Compliance or policy constraint passed.
- [x] Team capability constraint passed.

## Final Selection
- Winner option: B
- Winner weighted score: 4.40
- Runner-up weighted score: 3.80
- Margin: 0.60
- Override reason (required when margin < 0.20): n/a
- Approval: owner approved on 2026-02-17
- Effective from: 2026-02-17
