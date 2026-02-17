# SOP Factory Standard

## Supreme Standard Stack (ordered)
These standards are non-compensatory and must be applied top-down:

1. Non-Negotiables First
   - Legal, safety, security, and data integrity constraints cannot be traded off for speed or convenience.
2. Outcome Value over Activity
   - SOPs optimize measurable outcomes, not step completion counts.
3. Evidence before Escalation
   - Higher-impact or less-reversible decisions require stronger evidence.
4. Reversibility-Aware Speed
   - Move fast on reversible changes, slow down on irreversible changes.
5. Three-Optimal Execution
   - Best Practice defines valid option space.
   - Best Method chooses within that space by weighted score.
   - Best Tool optimizes execution with minimal complexity.
6. Simplicity and Maintainability
   - Prefer the simplest process that meets SLA and quality targets.
7. Closed-Loop Learning
   - Every release must feed back measured signals into rule updates.

## Objective
Turn repeatable work into measurable SOPs with explicit artifacts, hard gates, and iteration control.

## Evidence-Reversibility Matrix
- Reversibility classes:
  - `R1`: fully reversible, low blast radius.
  - `R2`: partially reversible, medium blast radius.
  - `R3`: hard to reverse, high blast radius.
- Minimum evidence tiers for release:
  - `R1` requires at least `E2`.
  - `R2` requires at least `E3`.
  - `R3` requires at least `E4`.
- Evidence tiers:
  - `E1`: judgment only.
  - `E2`: internal baseline with at least 3 samples.
  - `E3`: pilot evidence with at least 5 runs.
  - `E4`: stable production evidence for at least 2 review cycles.

## Routing Policy
- Route to SOP when all are true:
  - Frequency is at least 3 times per month.
  - Outcome variance is acceptable (coefficient of variation <= 0.20).
  - Steps are stable enough to document.
- Route to Decision Card when any is true:
  - Unknowns are high.
  - Constraints are changing rapidly.
  - Path is exploratory and not yet stable.

## Factory Pipeline
| Step | Required Artifact | Hard Gate |
|---|---|---|
| 1. Scope and classify | `resources/sop/<date>-<slug>.md` draft with objective and boundaries | Missing objective or owner blocks progress |
| 2. Baseline capture | Baseline section with cycle time, error rate, rework rate | Fewer than 3 historical samples blocks progress |
| 3. Three-optimal scoring | `resources/sop/<date>-<slug>-scorecard.md` | No weighted score blocks method selection |
| 4. SOP v1 authoring | SOP steps, quality gates, exceptions, SLA | Missing trigger or output schema blocks release |
| 5. Pilot run | Execution log with at least 5 runs | Fewer than 5 runs blocks promotion |
| 6. Review and iterate | `resources/sop/<date>-<slug>-iteration-log.md` | More than 3 rule changes per cycle is not allowed |

## Three-Optimal Implementation Rules
### Best Practice
- Source priority: internal evidence > official docs > trusted industry references.
- Every adopted practice must include:
  - Source link or origin.
  - Expected benefit.
  - Failure mode.

### Best Method
- Select method by weighted scoring under current constraints.
- Required dimensions:
  - Effectiveness.
  - Cycle time.
  - Error prevention.
  - Implementation cost.
  - Operational risk.
- Use highest weighted score only if hard constraints pass.
- Release threshold:
  - Winner weighted score >= 3.50.
  - Winner margin over second option >= 0.20, or document override reason.

### Best Tool
- Start from the minimum tool chain.
- Add a tool only if at least one is true:
  - Cycle time improvement >= 20 percent.
  - Error rate reduction >= 30 percent.
  - Manual effort reduction >= 30 percent.
- Record tool lock-in risk and rollback path.

## Mandatory Release Criteria
An SOP can move to `active` only when all are true:
1. SOP hard gates are all checked.
2. Scorecard hard constraints are all checked.
3. Pilot run count is at least 5 in iteration log.
4. Rule updates are capped at 1-3 for the release cycle.
5. Reversibility class and evidence tier satisfy matrix rules.
6. Validation command passes:
   - `python3 scripts/validate_sop_factory.py --sop <path> --strict`

## Governance
- Versioning: `vMAJOR.MINOR`.
  - MAJOR for structural changes.
  - MINOR for step or threshold tuning.
- Review cadence:
  - Weekly: metrics review.
  - Biweekly: rule updates (1-3 only).
- Mandatory metrics:
  - Cycle time.
  - First-pass yield.
  - Rework rate.
  - SOP adoption rate.

## File Layout
- SOP files: `resources/sop/YYYY-MM/<date>-<slug>.md`
- Scorecards: `resources/sop/YYYY-MM/<date>-<slug>-scorecard.md`
- Iteration logs: `resources/sop/YYYY-MM/<date>-<slug>-iteration-log.md`
- Global decision rules: `agent/patterns/decision-rules.md`
