# SOP Document

## Metadata
- SOP ID: SOP-20260217-23
- Name: 复盘写回（规则库/反例库）
- Owner: yizhi
- Team: deepsea-nexus
- Version: v1.0
- Status: draft
- Risk tier: low
- Reversibility class: R1
- Evidence tier at release: E2
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
- Non-negotiables check: no external side effects; writeback is limited to markdown under `agent/` and `resources/` and may be reverted.
- Outcome metric and baseline: baseline measured from recent 3 tasks; target is delta improvement on repeat-work and rework rate.
- Reversibility and blast radius: R1; blast radius limited to writeback files; rollback is git revert or restore previous version blocks.
- Evidence tier justification: E2 because procedure is internal and validated by schema + validator; higher tiers require >=5 pilot runs.
- Best Practice compliance: turn postmortems into executable rules; versioned, sourced, and reviewable.
- Best Method compliance: 3-artifact writeback (facts card + rules + anti-pattern) with 1-3 rule updates per cycle.
- Best Tool compliance: markdown templates + grep checks + (optional) SOP factory validator.
- Compliance reviewer: yizhi

## Objective
Systematize dynamic learning by converting every completed task/decision into versioned, reusable rules and anti-patterns with traceable sources.

## Scope and Boundaries
- In scope: tasks, decisions, experiments, incidents; writing postmortem artifacts; updating rule library and anti-pattern library.
- Out of scope: changing production systems, editing secrets, or taking external actions.
- Dependencies: `resources/decisions/`, `agent/patterns/`, `agent/cases/`.

## Trigger Conditions (if/then)
- IF a task/decision is marked done OR KPI outcome is observed (success or failure),
- THEN run this SOP within 24 hours.
- IF the same failure mode occurs twice within 30 days,
- THEN run this SOP immediately and upgrade the related rule to higher priority.

## Preconditions
- Precondition 1: there is a stable task identifier or decision card to attach as source.
- Precondition 2: at least one measurable outcome signal exists (metric, time, defect, user feedback, pass/fail).

## Inputs
- Input 1: task/decision description and context (goal, constraints, key variables).
- Input 2: outcome evidence (metrics, logs, diff, screenshots, feedback).

## Outputs
- Output 1: Postmortem card in `resources/decisions/YYYY-MM/` (facts + metrics + what changed).
- Output 2: Rule updates appended to `agent/patterns/decision-rules.md` (1-3 only) and/or new anti-pattern case in `agent/cases/anti-patterns/`.

## Three-Optimal Decision
- Best Practice selected: executable writeback with traceable sources and versioning.
- Best Method selected: 3-artifact loop (facts -> rule update -> anti-pattern) with bounded rule updates.
- Best Tool selected: markdown templates + minimal grep validation; optional strict SOP validator.
- Scorecard reference: resources/sop/2026-02/2026-02-17-postmortem-writeback-scorecard.md

## Procedure
| Step | Action | Quality Gate | Evidence |
|---|---|---|---|
| 1 | Create/locate the source decision card for this task | source path exists and is linkable | source URI/path |
| 2 | Write a Postmortem Card (facts) | includes goal/constraints, actions, results, metrics, and stop conditions | postmortem card |
| 3 | Extract 1-3 rule updates in if/then form | each rule has trigger + action + check + avoid | rule entries |
| 4 | Create/update Anti-pattern case if failure mode exists | anti-pattern includes detection signal + minimal reproduction + mitigation | anti-pattern file |
| 5 | Version + confidence + review date | each new rule has `confidence` and `review_at` | rule metadata |
| 6 | Run light validation | no broken links; required fields present | grep checklist |
| 7 | Log iteration | append to iteration log with changes and metrics | iteration log |

## Exceptions
| Scenario | Detection Signal | Response | Escalation |
|---|---|---|---|
| No metric evidence | only subjective outcome | define proxy metric and set `confidence=low` with `review_at` | escalate to owner |
| Too many rule candidates | >3 updates | keep top 1-3 by impact; defer rest to backlog | escalate if repeated |
| Sensitive content risk | API keys / secrets found | redact and store only pointers; do not write secrets | stop and escalate |

## Rollback and Stop Conditions
- Stop condition 1: source cannot be identified.
- Stop condition 2: writeback contains sensitive content.
- Blast radius limit: markdown files under `resources/decisions/`, `agent/patterns/`, `agent/cases/` only.
- Rollback action: revert the writeback commit or restore prior version block in the target file.

## SLA and Metrics
- Cycle time target: <= 30 minutes per postmortem.
- First-pass yield target: >= 90 percent postmortems produce at least 1 valid rule update.
- Rework rate ceiling: <= 10 percent rule updates require correction after review.
- Adoption target: 100 percent tasks tagged P0/P1 have postmortem writeback.

## Logging and Evidence
- Log location: resources/sop/2026-02/2026-02-17-postmortem-writeback-iteration-log.md
- Required record fields: source, outcome metric(s), rules changed, anti-pattern created/updated, confidence, review_at.

## Change Control
- Rule updates this cycle (1-3 only):
1. IF outcome evidence is missing, THEN require proxy metric and set `confidence=low` with `review_at`.
2. IF a failure mode repeats twice in 30 days, THEN anti-pattern case creation is mandatory.
3. IF a rule lacks a trigger signal, THEN block writeback until trigger is specified.

## Release Readiness
- Validation command:
  - `python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-17-postmortem-writeback-sop.md`  # draft OK
  - `python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-17-postmortem-writeback-sop.md --strict`  # requires >=5 pilot runs
- Release decision: hold
- Approver: yizhi
- Approval date: 2026-02-17

## Links
- Scorecard: resources/sop/2026-02/2026-02-17-postmortem-writeback-scorecard.md
- Iteration log: resources/sop/2026-02/2026-02-17-postmortem-writeback-iteration-log.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md
