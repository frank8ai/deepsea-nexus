# SOP Document

## Metadata
- SOP ID: SOP-20260217-01
- Name: Weekly Decision Review and Rule Update
- Owner: yizhi
- Team: deepsea-nexus
- Version: v1.0
- Status: active
- Risk tier: medium
- Reversibility class: R2
- Evidence tier at release: E3
- Created on: 2026-02-17
- Last reviewed on: 2026-02-17

## Hard Gates (must pass before activation)
- [x] Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- [x] Objective is explicit and measurable.
- [x] Outcome metric includes baseline and target delta.
- [x] Trigger conditions are testable (`if/then` with threshold or signal).
- [x] Inputs and outputs are defined.
- [x] Reversibility class and blast radius are declared.
- [x] Quality gates exist for critical steps.
- [x] Exception and rollback paths are defined.
- [x] SLA and metrics are numeric.

## Principle Compliance Declaration
- Non-negotiables check: compliant with repository policy, security boundaries, and traceability requirements.
- Outcome metric and baseline: cycle time baseline 52 min, target <= 30 min; first-pass yield baseline 68%, target >= 90%.
- Reversibility and blast radius: process-only changes, rollback by reverting markdown and rule status.
- Evidence tier justification: six pilot runs with measurable pass/fail outcomes satisfy E3 requirement.
- Best Practice compliance: hard-gated review checklist plus source-linked rules.
- Best Method compliance: weighted scorecard selection with explicit constraints.
- Best Tool compliance: markdown and `rg` chosen as minimal tool chain for current SLA.
- Compliance reviewer: yizhi

## Objective
Complete weekly review of active decision cards and publish 1-3 validated rule updates within 30 minutes.

## Scope and Boundaries
- In scope: `resources/decisions/YYYY-MM/*.md` and `agent/patterns/decision-rules.md`.
- Out of scope: non-decision knowledge notes and backlog grooming.
- Dependencies: decision cards must be updated in the same week.

## Trigger Conditions (if/then)
- IF it is Friday 17:00 local time OR open decision cards are 5 or more,
- THEN run this SOP once for the current week.

## Preconditions
- Precondition 1: at least 1 active decision card exists in current month folder.
- Precondition 2: previous week's iteration log is available.

## Inputs
- Input 1: active decision cards from `resources/decisions/YYYY-MM/`.
- Input 2: current rules from `agent/patterns/decision-rules.md`.

## Outputs
- Output 1: updated rule entries in `agent/patterns/decision-rules.md`.
- Output 2: weekly iteration log in `resources/sop/YYYY-MM/*-iteration-log.md`.

## Three-Optimal Decision
- Best Practice selected: hard-gated checklist review with explicit pass/fail.
- Best Method selected: batch review by threshold filters then 3-model comparison.
- Best Tool selected: markdown templates plus `rg` for fast field validation.
- Scorecard reference: `resources/sop/2026-02/2026-02-17-weekly-decision-review-scorecard.md`

## Procedure
| Step | Action | Quality Gate | Evidence |
|---|---|---|---|
| 1 | Collect this week's active decision cards | All cards have IDs and status fields | list of card paths |
| 2 | Run hard-gate check for metrics and stop conditions | 100 percent cards pass gate | pass/fail checklist |
| 3 | Identify variance signals and trigger models | At least 3 model views for important cards | comparison table |
| 4 | Draft 1-3 rule updates | Every rule is testable (`if/then` plus threshold) | proposed rule text |
| 5 | Commit approved rules into rules file | Rule IDs and source cards are linked | updated rules file |
| 6 | Publish weekly iteration log | Metrics and actions are complete | iteration log file |

## Exceptions
| Scenario | Detection Signal | Response | Escalation |
|---|---|---|---|
| Missing card fields | required fields missing in 1 or more cards | return card to owner and stop that card | escalate to owner same day |
| Conflicting rules | duplicate or opposite rule intent | keep existing active rule, mark candidate draft | escalate to reviewer |
| Time overrun risk | elapsed time > 30 minutes before step 5 | process top-risk cards first and defer remainder | escalate with carry-over list |

## Rollback and Stop Conditions
- Stop condition 1: fewer than 3 valid cards available for weekly review.
- Stop condition 2: unresolved conflicts in active rules after 2 review attempts.
- Blast radius limit: only decision-review workflow files in `resources/sop` and `agent/patterns/decision-rules.md`.
- Rollback action: revert newly drafted rules to draft status and reopen next cycle.

## SLA and Metrics
- Cycle time target: <= 30 minutes per weekly run.
- First-pass yield target: >= 90 percent cards pass hard gates on first review.
- Rework rate ceiling: <= 10 percent cards require second review.
- Adoption target: 100 percent high-scope decisions follow this review.

## Logging and Evidence
- Log location: `resources/sop/YYYY-MM/`.
- Required record fields: run date, cards reviewed, pass rate, rules changed, open risks.

## Change Control
- Rule updates this cycle (1-3 only):
1. IF `Success Metrics` or `Stop Condition` is missing, THEN block execution.
2. IF critical unknowns are 3 or more, THEN include probability framing.
3. IF local and system metrics diverge for 2 cycles, THEN run loop diagnosis.

## Release Readiness
- Validation command:
  - `python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-17-weekly-decision-review-sop.md --strict`
- Release decision: approve
- Approver: yizhi
- Approval date: 2026-02-17

## Links
- Scorecard: `resources/sop/2026-02/2026-02-17-weekly-decision-review-scorecard.md`
- Iteration log: `resources/sop/2026-02/2026-02-17-weekly-decision-review-iteration-log.md`
- Related decision cards: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
