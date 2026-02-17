# L1 Overview - Weekly Decision Review and Rule Update

## When to use
- it is Friday 17:00 local time OR open decision cards are 5 or more

## Inputs
- Input 1: active decision cards from `resources/decisions/YYYY-MM/`.
- Input 2: current rules from `agent/patterns/decision-rules.md`.

## Outputs
- Output 1: updated rule entries in `agent/patterns/decision-rules.md`.
- Output 2: weekly iteration log in `resources/sop/YYYY-MM/*-iteration-log.md`.

## Minimal procedure
1) Collect this week's active decision cards
2) Run hard-gate check for metrics and stop conditions
3) Identify variance signals and trigger models
4) Draft 1-3 rule updates
5) Commit approved rules into rules file
6) Publish weekly iteration log

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：Weekly Decision Review and Rule Update <输入>`
