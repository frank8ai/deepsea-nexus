# L1 Overview - SOP Factory Production

## When to use
- task frequency is >= 3 per month AND outcome variance coefficient is <= 0.20
- an active SOP has first-pass yield < 85% or rework rate > 20% in one review window

## Inputs
- Input 1: candidate task description with frequency and variance data.
- Input 2: baseline metrics, constraints, and current tool/method options.

## Outputs
- Output 1: SOP artifact triplet (`sop.md`, `scorecard.md`, `iteration-log.md`) with release decision.
- Output 2: strict validation evidence and 1-3 rule updates for next cycle.

## Minimal procedure
1) Classify candidate and confirm SOP routing
2) Capture baseline from recent runs
3) Build three-optimal scorecard and select method
4) Author SOP v1 from template with all hard fields
5) Run pilot and produce iteration log
6) Run strict validator and resolve failures
7) Release decision and indexing

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：SOP Factory Production <输入>`
