# SOP Document

## Metadata
- SOP ID: SOP-YYYYMMDD-XX
- Name:
- Tags:
- Primary triggers:
- Primary outputs:
- Owner:
- Team:
- Version: v1.0
- Status: draft | active | deprecated
- Risk tier: low | medium | high
- Reversibility class: R1 | R2 | R3
- Evidence tier at release: E1 | E2 | E3 | E4
- Effective condition:
- Review cycle:
- Retirement condition:
- Created on:
- Last reviewed on:

## Hard Gates (must pass before activation)
- [ ] Non-negotiables (legal/safety/security/data integrity) are explicitly checked.
- [ ] Objective is explicit and measurable.
- [ ] Outcome metric includes baseline and target delta.
- [ ] Trigger conditions are testable (`if/then` with threshold or signal).
- [ ] Inputs and outputs are defined.
- [ ] Reversibility class and blast radius are declared.
- [ ] Quality gates exist for critical steps.
- [ ] Exception and rollback paths are defined.
- [ ] SLA and metrics are numeric.

## Principle Compliance Declaration
- Non-negotiables check:
- Outcome metric and baseline:
- Reversibility and blast radius:
- Evidence tier justification:
- Best Practice compliance:
- Best Method compliance:
- Best Tool compliance:
- Simplicity and maintainability check:
- Closed-loop writeback check:
- Compliance reviewer:

## Objective

## Scope and Boundaries
- In scope:
- Out of scope:
- Dependencies:

## Trigger Conditions (if/then)
- IF
- THEN

## Preconditions
- Precondition 1:
- Precondition 2:

## Inputs
- Input 1:
- Input 2:

## Outputs
- Output 1:
- Output 2:

## Three-Optimal Decision
- Best Practice selected:
- Best Method selected:
- Best Tool selected:
- Scorecard reference:

## Procedure
| Step | Action | Quality Gate | Evidence |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |

## Exceptions
| Scenario | Detection Signal | Response | Escalation |
|---|---|---|---|
| | | | |

## Kill Switch
| Trigger threshold | Immediate stop | Rollback action |
|---|---|---|
| Non-negotiable breach (legal/safety/security/data integrity) | Stop execution immediately and block release | Revert to last approved SOP version and open incident record |
| Primary result metric degrades for 2 consecutive monthly cycles | Downgrade SOP status to `draft` and stop rollout | Restore previous stable SOP and rerun pilot >= 5 with strict validation |

## Rollback and Stop Conditions
- Stop condition 1:
- Stop condition 2:
- Blast radius limit:
- Rollback action:

## SLA and Metrics
- Cycle time target:
- First-pass yield target:
- Rework rate ceiling:
- Adoption target:
- Result metric (primary):
- Process metric (secondary):
- Replacement rule: process metrics cannot replace result metrics for release decisions.

## Logging and Evidence
- Log location:
- Required record fields:

## Change Control
- Rule updates this cycle (1-3 only):
1.
2.
3.

## Release Readiness
- Validation command:
  - `python3 scripts/validate_sop_factory.py --sop <this-file-path> --strict`
- Auto-downgrade gate:
- Release decision: approve | hold
- Approver:
- Approval date:

## Links
- Scorecard:
- Iteration log:
- L0 abstract:
- L1 overview:
- Related decision cards:
