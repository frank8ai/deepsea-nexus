# L1 Overview - 复盘写回（规则库/反例库）

## When to use
- task done
- repeated failure
- KPI observed (success/fail)

## Inputs
- Input 1: task/decision description and context (goal, constraints, key variables).
- Input 2: outcome evidence (metrics, logs, diff, screenshots, feedback).

## Outputs
- Output 1: Postmortem card in `resources/decisions/YYYY-MM/` (facts + metrics + what changed).
- Output 2: Rule updates appended to `agent/patterns/decision-rules.md` (1-3 only) and/or new anti-pattern case in `agent/cases/anti-patterns/`.

## Minimal procedure
1) Create/locate the source decision card for this task
2) Write a Postmortem Card (facts)
3) Extract 1-3 rule updates in if/then form
4) Create/update Anti-pattern case if failure mode exists
5) Version + confidence + review date
6) Run light validation
7) Log iteration

## Quality gates
- Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- Objective is explicit and measurable.
- Outcome metric includes baseline and target delta.

## Invocation
`按SOP执行：复盘写回（规则库/反例库） <输入>`
