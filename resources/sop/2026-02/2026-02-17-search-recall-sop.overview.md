# L1 Overview - Search Recall Execution

## When to use
- user query contains memory triggers (`还记得`, `上次`, `之前提到`) OR query intent is historical lookup
- first-pass top1 relevance is below `0.35` OR top3 median relevance is below `0.25`

## Inputs
- Input 1: raw user query.
- Input 2: target `n` (default 5, expanded pass uses 8).

## Outputs
- Output 1: top-k recall results with relevance, source, and snippet.
- Output 2: search quality record (latency, relevance, pass/fail gate decision).

## Minimal procedure
1) Run readiness checks (`health`, `stats`)
2) Normalize and classify query intent
3) Execute first-pass recall with original query
4) If gate fails, run second-pass with up to 2 rewritten queries and n=8
5) Merge, dedupe, and rank final results
6) Record metrics and update iteration log

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：Search Recall Execution <输入>`
