# SOP Document

## Metadata
- SOP ID: SOP-20260219-02
- Name: SOP Governance Routing and Assetized Writeback
- Tags: sop, governance, routing, writeback, hq, nexus, multi-agent
- Primary triggers: new SOP is requested; existing SOP requires upgrade; HQ and Nexus references diverge; execution finished but no writeback asset exists
- Primary outputs: routing decision with canonical SOP path; mandatory writeback asset bundle; KPI and stop-condition decision record
- Owner: yizhi
- Team: OpenClaw operations
- Version: v1.0
- Status: active
- Risk tier: medium
- Reversibility class: R1
- Evidence tier at release: E2
- Effective condition: HQ entry index points to this canonical SOP and strict validator passes.
- Review cycle: weekly operations review and monthly governance review.
- Retirement condition: replaced by a higher-performing v2+ governance SOP with stable gains for 2 cycles.
- Created on: 2026-02-19
- Last reviewed on: 2026-02-19

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
- Non-negotiables check: no secret exposure, no unsafe config writes, and no unreviewed public output in governance runs.
- Outcome metric and baseline: baseline governance close rate 61 percent in the last 14 days; target >= 85 percent with complete writeback assets.
- Reversibility and blast radius: R1; changes are limited to SOP docs, indexes, and summary files; rollback by restoring previous markdown versions.
- Evidence tier justification: E2 is sufficient for R1 and backed by 6 governance pilot runs in the iteration log.
- Best Practice compliance: use one canonical SOP source and pointer-based entry files to prevent split-brain governance.
- Best Method compliance: route -> execute -> writeback -> score -> stop/continue loop with one converge owner.
- Best Tool compliance: markdown SOP triplets, `rg` consistency scan, and strict validator gate.
- Simplicity and maintainability check: HQ stays lightweight as execution entry; Nexus stores full canonical artifacts.
- Closed-loop writeback check: each execution must write 1 memory card, 1 counterexample or risk note, 1 parameter update, and 1 reusable snippet path.
- Compliance reviewer: yizhi

## Objective
Standardize SOP governance into one executable loop so all agents run with the same source of truth, mandatory asset writeback, and unified KPI/stop criteria.

## Scope and Boundaries
- In scope:
  - SOP routing and dispatch.
  - HQ entry versus Nexus authority governance.
  - Mandatory writeback assets and lifecycle updates.
  - KPI/stop-condition standardization across SOPs.
  - P0/P1/P2 catalog consistency checks and pilot-run records.
- Out of scope:
  - Model-provider procurement policy.
  - Channel-specific routing mechanics outside SOP governance.
  - Unrelated product roadmap decisions.
- Dependencies:
  - `SOP/SOP_INDEX.md`
  - `SOP/SOP_HQ_SOP_Governance_Routing_v1.md`
  - `resources/sop/2026-02/2026-02-17-sop-factory-production-sop.md`
  - `scripts/validate_sop_factory.py`

## Trigger Conditions (if/then)
- IF a request requires SOP creation or upgrade, THEN run this SOP to route and govern execution.
- IF HQ entry and Nexus canonical file disagree on version or acceptance rules, THEN stop rollout and repair source-of-truth links first.
- IF an execution ends without the required asset writeback bundle, THEN mark run as failed and block completion.

## Preconditions
- Precondition 1: access to both HQ (`SOP/`) and Nexus (`resources/sop/`) trees is available.
- Precondition 2: strict validation tooling is runnable in the Nexus repository.

## Inputs
- Input 1: task description and target project/channel context.
- Input 2: current SOP catalogs, active versions, KPI snapshots, and last iteration log.

## Outputs
- Output 1: accepted routing decision with HQ entry path and Nexus canonical path.
- Output 2: writeback asset bundle with memory card, counterexample/risk note, parameter delta, reusable snippet, and pilot record update.

## Three-Optimal Decision
- Best Practice selected: HQ is execution entry, Nexus is canonical authority, and all long artifacts stay on disk with path-only summaries.
- Best Method selected: route task to SOP -> parallel execution -> main converge -> mandatory writeback -> KPI review -> release or rollback.
- Best Tool selected: SOP index pointers, strict validator, `rg` drift checks, and fixed writeback path schema.
- Scorecard reference: `resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-scorecard.md`

## Procedure
| Step | Action | Quality Gate | Evidence |
|---|---|---|---|
| 1 | Intake request and classify risk/tier/project. | Request has owner, scope, and due window. | Classification record in run log. |
| 2 | Route task to an existing SOP or create/upgrade target SOP via factory path. | Route decision includes invoke name and canonical path. | Routing entry in summary doc. |
| 3 | Enforce source of truth: HQ as entry, Nexus as authority, with explicit pointer links. | HQ file contains canonical pointer; Nexus file is the only full-fidelity version. | Link check output and file references. |
| 4 | Execute with parallel-first pattern when decomposable; converge only in main agent. | At most 2-3 parallel branches and one converge decision owner. | Converge note and artifact paths. |
| 5 | Apply mandatory assetized writeback after execution. | Required 4 assets are all present and path-resolved. | Asset bundle list in iteration log. |
| 6 | Apply unified KPI and stop conditions using company-level fields (`DoD`, `Result metric`, `Process metric`, `Stop`). | KPI fields are numeric and stop rules are testable. | SOP diff and validation pass. |
| 7 | Merge Discord multi-agent SOPs as mother SOP + scoped variants with version lock. | Mother SOP has stable version; variants declare delta only. | Version map file update. |
| 8 | Run P0/P1/P2 catalog consistency checks (count, names, invoke strings, paths). | No count/name/path mismatches (for example, no `12 vs 14` drift). | Consistency report in logs. |
| 9 | Standardize research artifacts (`pack`, `card`, `abstract`, `overview`) and naming. | All required artifact types exist for target SOP. | Artifact index with paths. |
| 10 | Ensure HQ scorecard/iteration links point to Nexus canonical files. | HQ references are pointer-only and non-duplicated. | Link audit output. |
| 11 | Record pilot runs in unified schema and apply automation trigger policy (cron or manual confirm). | Pilot schema complete and automation class is declared per SOP. | Pilot record and trigger policy table. |

## Exceptions
| Scenario | Detection Signal | Response | Escalation |
|---|---|---|---|
| Canonical file missing or unreadable | Nexus path fails existence check | Stop release, restore from last good commit, and rerun validation | Escalate to owner immediately |
| KPI data unavailable at close time | Required KPI fields empty or stale | Mark run as `hold`; allow only temporary summary output | Escalate within same review cycle |
| Parallel branches conflict at merge | Contradictory outputs from sub-agents | Freeze merge, request one reconciliation pass, then re-converge | Escalate if conflict repeats twice in 24h |

## Kill Switch
| Trigger threshold | Immediate stop | Rollback action |
|---|---|---|
| Non-negotiable breach (legal/safety/security/data integrity) | Stop execution immediately and block release | Revert to last approved SOP version and open incident record |
| Source-of-truth drift unresolved for > 24 hours | Freeze all SOP upgrades and hold new releases | Revert HQ pointers to last stable canonical mapping |
| Primary result metric degrades for 2 consecutive monthly cycles | Downgrade SOP status to `draft` and stop rollout | Restore previous stable SOP and rerun pilot >= 5 with strict validation |

## Rollback and Stop Conditions
- Stop condition 1: required writeback asset bundle is incomplete after one correction loop.
- Stop condition 2: strict validation fails or source-of-truth mapping remains inconsistent.
- Blast radius limit: SOP markdown artifacts, SOP indexes, and memory/shared guidance files only.
- Rollback action: restore previous approved SOP files and index pointers, then reopen as `draft`.

## SLA and Metrics
- Routing decision latency target: <= 10 minutes from intake.
- Governance close rate target: >= 85 percent completed runs with full acceptance.
- Writeback completeness target: >= 95 percent runs with all required assets.
- Catalog consistency target: 100 percent no mismatch across P0/P1/P2 indexes.
- Result metric (primary): governance close rate with full writeback completeness.
- Process metric (secondary): median routing latency and merge cycle time.
- Replacement rule: process metrics cannot replace result metrics for release decisions.

## Logging and Evidence
- Log location: `resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-iteration-log.md`
- Required record fields: run id, route decision, canonical path, asset bundle paths, KPI values, stop/rollback decision, pilot flag, automation class.

## Change Control
- Rule updates this cycle (1-3 only):
1. IF HQ and Nexus links drift, THEN block execution and repair links before any SOP upgrade.
2. IF execution output is long, THEN persist artifacts to files and keep channel/main output as summary plus paths only.
3. IF run close lacks required assets, THEN mark run `hold` and rerun writeback gate.

## Release Readiness
- Validation command:
  - `python3 scripts/validate_sop_factory.py --sop resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-sop.md --strict`
- Auto-downgrade gate: if monthly KPI trend shows primary result metric degradation for 2 consecutive cycles, set `Status: draft` and rerun pilot + strict validation.
- Release decision: approve
- Approver: yizhi
- Approval date: 2026-02-19

## Links
- Scorecard: `resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-scorecard.md`
- Iteration log: `resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-iteration-log.md`
- L0 abstract: `resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-sop.abstract.md`
- L1 overview: `resources/sop/2026-02/2026-02-19-sop-governance-routing-writeback-sop.overview.md`
- Related decision cards: n/a
