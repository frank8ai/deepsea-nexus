# SOP Factory Quickstart

## Highest Principle
All SOPs must satisfy the supreme standard stack in this order:
1. Non-negotiables (legal/safety/security/data integrity).
2. Outcome value over activity.
3. Evidence strength follows risk.
4. Reversibility-aware speed.
5. Three-optimal execution (Best Practice, Best Method, Best Tool).
6. Simplicity and maintainability.
7. Closed-loop learning.

## Mandatory Mechanisms
1. Lifecycle fields: effective condition, review cycle, retirement condition.
2. Kill Switch: trigger threshold -> immediate stop -> rollback action.
3. Dual-track metrics: result (primary) + process (secondary), no substitution.
4. Auto-downgrade gate: 2 consecutive monthly degradations -> `active` to `draft`.

## Evidence-Reversibility Rule
- `R1` requires at least `E2`.
- `R2` requires at least `E3`.
- `R3` requires at least `E4`.

## Six-Step Factory Flow
1. Classify task and confirm it should enter SOP Factory.
2. Capture baseline metrics from at least 3 recent runs.
3. Build scorecard and select winner by weighted score.
4. Author SOP v1 with hard gates, exceptions, SLA, and release readiness.
5. Run pilot for at least 5 runs and record iteration log.
6. Update 1-3 rules and release only after strict validation passes.

## File Templates
- SOP template: `resources/sop/TEMPLATE.sop.md`
- Scorecard template: `resources/sop/TEMPLATE.sop-scorecard.md`
- Iteration log template: `resources/sop/TEMPLATE.sop-iteration-log.md`

## Retrieval-Friendly Layer
- Metadata fields are mandatory in every SOP:
  - `Tags`
  - `Primary triggers`
  - `Primary outputs`
- L0/L1 files:
  - `<sop>.abstract.md` (L0, minimal semantic summary)
  - `<sop>.overview.md` (L1, invocation and execution skeleton)

## System SOP Quick Cards
- `resources/sop/2026-02/2026-02-17-postmortem-writeback-quick-card.md`
- `resources/sop/2026-02/2026-02-17-multi-agent-research-merge-quick-card.md`

## Release Command
Run before changing SOP status to `active`:

```bash
python3 scripts/validate_sop_factory.py --sop <sop-file-path> --strict
```

## Monthly KPI Dashboard
Generate monthly trend dashboard from iteration logs:

```bash
python3 scripts/generate_sop_iteration_trends.py --month 2026-02
```

Default output:
- `resources/sop/2026-02/2026-02-sop-iteration-kpi-dashboard.md`

## Example
- SOP: `resources/sop/2026-02/2026-02-17-weekly-decision-review-sop.md`
- Scorecard: `resources/sop/2026-02/2026-02-17-weekly-decision-review-scorecard.md`
- Iteration log: `resources/sop/2026-02/2026-02-17-weekly-decision-review-iteration-log.md`
- SOP: `resources/sop/2026-02/2026-02-17-sop-factory-production-sop.md`
- Scorecard: `resources/sop/2026-02/2026-02-17-sop-factory-production-scorecard.md`
- Iteration log: `resources/sop/2026-02/2026-02-17-sop-factory-production-iteration-log.md`
