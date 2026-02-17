# SOP Document

## Metadata
- SOP ID: SOP-20260217-24
- Name: 多代理并行研究与合并
- Owner: yizhi
- Team: deepsea-nexus
- Version: v1.0
- Status: active
- Risk tier: medium
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
- Non-negotiables check: no external actions beyond reading sources; output is markdown artifacts; sensitive data is redacted.
- Outcome metric and baseline: baseline from recent 3 similar research tasks; target is time-to-decision and confidence score improvement.
- Reversibility and blast radius: R1; only produces research pack + decision card + rule/case updates; rollback by deleting artifacts.
- Evidence tier justification: E2 because this SOP is a coordination method; E3 requires >=5 pilot runs with measurable deltas.
- Best Practice compliance: parallelize perspectives (evidence, critique, build) and enforce conflict-aware merge.
- Best Method compliance: 4-role loop (Researcher/Critic/Builder/Synthesizer) with strict output schema and merge rules.
- Best Tool compliance: structured markdown outputs; optional web research SOP tools and local repo evidence.
- Compliance reviewer: yizhi

## Objective
Systematize exploration breadth by running parallel agent roles and merging results into one conflict-audited, execution-ready conclusion.

## Scope and Boundaries
- In scope: technical research, product design, architecture options, SOP design, incident analysis.
- Out of scope: making irreversible external changes; public posts; using secrets in outputs.
- Dependencies: HQ research SOPs when web evidence is needed; writeback SOP for rule extraction after merge.

## Trigger Conditions (if/then)
- IF the question has >=2 plausible options OR high uncertainty OR high stakes (Risk tier medium+),
- THEN use this SOP.
- IF expected decision impact is >= 1 week of work OR cost impact is non-trivial,
- THEN use this SOP.

## Preconditions
- Precondition 1: question is written with objective + constraints + success criteria.
- Precondition 2: timebox is declared (default 45-90 minutes).

## Inputs
- Input 1: research question/topic.
- Input 2: constraints (time, budget, stack, security posture).

## Outputs
- Output 1: Research pack in `resources/research-packs/YYYY-MM/<topic>.md` with evidence + option matrix.
- Output 2: Decision card in `resources/decisions/YYYY-MM/<topic>.md` with chosen option + next steps.
- Output 3 (optional): rule updates and anti-patterns (route to 复盘写回 SOP).

## Three-Optimal Decision
- Best Practice selected: multi-perspective parallelism + conflict-aware merge + evidence weighting.
- Best Method selected: 4-role pipeline with strict schema and merge rules.
- Best Tool selected: SOP templates + citations + (optional) firecrawl/web-search when allowed.
- Scorecard reference: resources/sop/2026-02/2026-02-17-multi-agent-research-merge-scorecard.md

## Procedure
| Step | Action | Quality Gate | Evidence |
|---|---|---|---|
| 1 | Clarify problem statement and success criteria | objective/constraints/metrics written | problem statement |
| 2 | Spawn 3 parallel roles (Researcher/Critic/Builder) | each role has a timebox and output schema | role prompts |
| 3 | Collect outputs and normalize format | each output has: conclusion, evidence, uncertainties, next step | normalized blocks |
| 4 | Synthesizer merges with conflict table | conflicts are explicit with evidence comparison | merge report |
| 5 | Produce option matrix and recommendation | options include cost/risk/maintainability/migration | matrix |
| 6 | Write decision card + next actions | next 1-3 steps, stop conditions, owner | decision card |
| 7 | Route writeback | 1-3 rule updates and anti-patterns extracted | writeback note |
| 8 | Log iteration | record duration, sources, and delta vs baseline | iteration log |

## Output Schema (for each role)
- Role: Researcher | Critic | Builder
- Conclusion (1 sentence):
- Evidence (links/files):
- Uncertainties:
- Recommended next step:

## Merge Rules
- Any conflict must be written as a 4-column table: Claim A / Claim B / Evidence / Decision.
- Claims without evidence are downgraded (label: `low-evidence`).
- If critical claim has single source, mark as `needs-second-source`.

## Exceptions
| Scenario | Detection Signal | Response | Escalation |
|---|---|---|---|
| Too many sources, low clarity | pack > 2k words without decision | force option matrix and top-3 decision drivers | escalate to owner |
| Conflicts unresolved | >=2 critical conflicts remain | timebox a focused follow-up query | escalate if deadline |
| Tooling blocked | web tools unavailable | switch to local repo/docs evidence only; mark confidence | escalate if stakes high |

## Rollback and Stop Conditions
- Stop condition 1: no clear success criteria.
- Stop condition 2: timebox exceeded without decision.
- Blast radius limit: markdown artifacts under `resources/research-packs/`, `resources/decisions/`, and optional writeback files.
- Rollback action: delete pack and decision card or mark as `draft`.

## SLA and Metrics
- Cycle time target: <= 90 minutes for one full run.
- First-pass yield target: >= 80 percent runs produce a decision card with explicit next steps.
- Rework rate ceiling: <= 20 percent runs require a second merge pass.
- Adoption target: 100 percent medium+ risk research uses multi-agent merge.

## Logging and Evidence
- Log location: resources/sop/2026-02/2026-02-17-multi-agent-research-merge-iteration-log.md
- Required record fields: topic, roles used, sources count, conflicts count, decision, duration.

## Change Control
- Rule updates this cycle (1-3 only):
1. IF a critical claim has only one source, THEN label as `needs-second-source` and do not finalize without explicit acceptance.
2. IF conflicts remain, THEN create a follow-up query list (max 3) and timebox 15 minutes.
3. IF outputs exceed 2k words without decision, THEN force option matrix and decision drivers.

## Release Readiness
- Validation command:
  - `python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-17-multi-agent-research-merge-sop.md --strict`
- Release decision: approve
- Approver: yizhi
- Approval date: 2026-02-17

## Links
- Scorecard: resources/sop/2026-02/2026-02-17-multi-agent-research-merge-scorecard.md
- Iteration log: resources/sop/2026-02/2026-02-17-multi-agent-research-merge-iteration-log.md
- Related decision cards: resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md
