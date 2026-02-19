# SOP Document

## Metadata
- SOP ID: SOP-20260219-01
- Name: Discord Multi-Agent Efficient Collaboration and Token Control
- Tags: discord, multi-agent, orchestration, token-efficiency, routing
- Primary triggers: long output tasks, multi-subtask requests, cross-topic requests in same channel
- Primary outputs: accepted summary in main channel + complete artifacts on disk paths
- Owner: yizhi
- Team: OpenClaw operations
- Version: v1.1
- Status: active
- Risk tier: medium
- Reversibility class: R2
- Evidence tier at release: E3
- Effective condition: Discord routing and role bindings are healthy, and on-call can run probe checks.
- Review cycle: weekly metric review, biweekly rule update, monthly lifecycle review.
- Retirement condition: replaced by a higher-performing SOP for 2 review cycles with stable KPI gains.
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
- Non-negotiables check: Keep `configWrites=false`, no secret exposure in channel output, and no unapproved high-risk admin action.
- Outcome metric and baseline: first-pass yield baseline 72% -> target >= 85%; cycle time baseline 42 min -> target <= 30 min.
- Reversibility and blast radius: R2, scoped to Discord routing and channel execution behavior; rollback by restoring previous config and previous SOP version.
- Evidence tier justification: E3 met with 12 runs in review window and documented iteration log.
- Best Practice compliance: deterministic routing (`peer > roles > guild > account`) and summary-only main channel policy.
- Best Method compliance: parallel dispatch then converge under main-agent acceptance gate.
- Best Tool compliance: OpenClaw bindings + artifact file-drop paths + converge checklist.
- Simplicity and maintainability check: fixed path list and role boundaries, minimal extra tooling.
- Closed-loop writeback check: weekly KPI review writes back rule updates (1-3 only) into iteration log.
- Compliance reviewer: yizhi

## Objective
Achieve fast and stable collaboration between main agent and subagents in Discord while minimizing token consumption and preventing cross-talk.

## Scope and Boundaries
- In scope:
  - Main-agent task routing and converge decision.
  - Subagent execution for research, coding, and writing.
  - Artifact persistence and summary-only output in main channel.
- Out of scope:
  - New model procurement and provider policy changes.
  - Cross-platform process redesign outside Discord.
- Dependencies:
  - OpenClaw gateway health.
  - Stable bindings in `~/.openclaw/openclaw.json`.
  - Access to `agent/`, `docs/`, and `logs/` directories.

## Trigger Conditions (if/then)
- IF output is long (full code diff, long log, or > 600 tokens), THEN persist full output to file and post summary + path only in main channel.
- IF request can be decomposed into 2-3 independent subtasks, THEN dispatch in parallel to distinct subagents and enforce single converge gate.
- IF a new topic or new project appears, THEN start a new channel or isolated session before execution.

## Preconditions
- Precondition 1: `openclaw channels status --probe` reports Discord as working.
- Precondition 2: bindings are deterministic and include main fallback.

## Inputs
- Input 1: user request from Discord channel or DM policy-allowed source.
- Input 2: current routing context (peer, role, guild, channel ownership).

## Outputs
- Output 1: concise decision summary in main channel.
- Output 2: full artifacts written on disk under standard paths.

### Output File Path List (mandatory)
- `agent/HOT.md` (active execution snapshot)
- `agent/WARM.md` (milestone summary)
- `agent/RESULT.md` (final completion record)
- `docs/discord/<project>/<date>-decision-summary.md` (human-readable delivery doc)
- `logs/discord/<project>/<run-id>.log` (full runtime logs)
- `logs/discord/<project>/<run-id>-qa-tail.log` (quality gate tail)

## Three-Optimal Decision
- Best Practice selected: deterministic routing + role specialization + summary-only main channel output.
- Best Method selected: main-agent orchestrated parallel execution with single converge acceptance.
- Best Tool selected: OpenClaw bindings, artifact path checklist, and converge gate checklist.
- Scorecard reference: `resources/sop/2026-02/2026-02-19-discord-multi-agent-efficient-collaboration-scorecard.md`

## Procedure
| Step | Action | Quality Gate | Evidence |
|---|---|---|---|
| 1 | Main agent classifies request type and risk. | Type and risk fields are non-empty before dispatch. | Request classification note in `agent/HOT.md`. |
| 2 | Main agent splits work into 2-3 parallel subtasks when possible. | Every subtask has owner, output format, and deadline. | Subtask list in `docs/discord/<project>/<date>-decision-summary.md`. |
| 3 | Researcher, coder, writer run independently in their own scope. | No direct worker-to-worker dependency chat. | Worker outputs persisted in `docs/` and `logs/`. |
| 4 | Workers persist full outputs to disk paths. | No long output posted directly in main channel. | File paths listed in RESULT summary. |
| 5 | Main agent performs converge review and acceptance. | Acceptance checklist complete: correctness, scope, risk, rollback. | Converge record in `agent/RESULT.md`. |
| 6 | Main channel receives only concise summary and artifact paths. | Summary <= 200 tokens unless incident mode. | Main channel message snapshot. |
| 7 | If topic/project changes, open new channel/session and rebind ownership. | Existing channel remains single-purpose. | New channel/session reference in summary doc. |

## Exceptions
| Scenario | Detection Signal | Response | Escalation |
|---|---|---|---|
| Urgent incident with severe time pressure | Priority is P0 and SLA at risk | Allow temporary serial mode, still enforce file drop | Escalate to owner within 15 minutes |
| Routing mismatch or wrong-agent reply | Incorrect agent responded to known owned channel | Stop run, fix binding order, rerun from classify step | Escalate if repeated >= 2 times in 24h |

## Kill Switch
| Trigger threshold | Immediate stop | Rollback action |
|---|---|---|
| Non-negotiable breach (legal/safety/security/data integrity) | Stop execution immediately and block release | Revert to last approved SOP version and open incident record |
| Primary result metric degrades for 2 consecutive monthly cycles | Downgrade SOP status to `draft` and stop rollout | Restore previous stable SOP and rerun pilot >= 5 with strict validation |
| Cross-talk incident occurs in 2 runs within one week | Freeze parallel split and revert to guarded serial flow | Restore prior routing policy and rerun checklist-based pilot |

## Rollback and Stop Conditions
- Stop condition 1: routing is non-deterministic or binding conflict remains unresolved.
- Stop condition 2: artifact file-drop discipline fails in >= 2 consecutive runs.
- Blast radius limit: single Discord guild and mapped project channels only.
- Rollback action: revert to previous validated SOP and previous stable binding snapshot.

## SLA and Metrics
- Cycle time target: <= 30 minutes per standard request.
- First-pass yield target: >= 85%.
- Rework rate ceiling: <= 15%.
- Adoption target: >= 75% of eligible tasks follow this SOP.
- Result metric (primary): first-pass yield of main-agent accepted deliveries.
- Process metric (secondary): median cycle time from request intake to converge acceptance.
- Replacement rule: process metrics cannot replace result metrics for release decisions.

## Logging and Evidence
- Log location: `logs/discord/<project>/` and summary records in `agent/`.
- Required record fields: request id, route decision, subtask owners, artifact paths, acceptance decision, rollback note (if any).

## Change Control
- Rule updates this cycle (1-3 only):
1. Enforce mandatory path list for all long outputs.
2. Enforce parallel-first dispatch for decomposable tasks.
3. Enforce new-channel/new-session policy for new topic or new project.

## Release Readiness
- Validation command:
  - `python3 scripts/validate_sop_factory.py --sop <this-file-path> --strict`
- Auto-downgrade gate: if primary metric degrades for 2 consecutive monthly cycles, set status `active -> draft` and rerun pilot.
- Release decision: approve
- Approver: yizhi
- Approval date: 2026-02-19

## Links
- Scorecard: `resources/sop/2026-02/2026-02-19-discord-multi-agent-efficient-collaboration-scorecard.md`
- Iteration log: `resources/sop/2026-02/2026-02-19-discord-multi-agent-efficient-collaboration-iteration-log.md`
- L0 abstract: `resources/sop/2026-02/2026-02-19-discord-multi-agent-efficient-collaboration-sop.abstract.md`
- L1 overview: `resources/sop/2026-02/2026-02-19-discord-multi-agent-efficient-collaboration-sop.overview.md`
- Related decision cards: n/a
