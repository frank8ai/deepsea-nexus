# Decision Card

## Metadata
- Decision ID: DEC-20260217-01
- Date: 2026-02-17
- Owner: yizhi
- Status: completed
- Scope: medium

## Hard Gates (must pass before execution)
- [x] Goal is explicit and singular.
- [x] Constraints are explicit (time, budget, dependencies).
- [x] Success metrics are numeric thresholds.
- [x] Stop condition is defined.
- [x] At least 3 models are selected for comparison.

## Problem
The second-brain workflow was documented conceptually but lacked hard artifacts for repeatable execution and review.

## Goal
Deploy a minimum executable operating loop in `deepsea-nexus` today: decision template, model template, rule template, and one completed decision sample.

## Constraints
- Time: complete within 90 minutes.
- Budget: no external tooling spend.
- Resources: markdown files only, no runtime code changes.
- Non-negotiables: use testable triggers (`if/then` plus thresholds) and include 3-model comparison.

## Success Metrics (numeric thresholds)
- At least 3 template artifacts are created and saved in target paths.
- 100 percent of required hard-gate fields are present in the sample card.
- At least 1 active rule is written back to `agent/patterns/decision-rules.md`.

## Stop Condition (terminate or pivot when any is true)
- Path conflict with existing structure that cannot be resolved in under 15 minutes.
- Inability to define testable trigger thresholds for selected models.

## Model Trigger Check (if/then)
- IF available build window is less than 7 days, THEN prioritize Opportunity Cost.
- IF critical unknowns are 3 or more, THEN include Bayes and Probability.
- IF local completion rises while system adoption stalls for 2 cycles, THEN apply Systems Feedback Loop.

## Multi-Model Comparison (minimum 3)
| Model | Key Variables | Risk Signal | Preferred Action | Do Not Do |
|---|---|---|---|---|
| Opportunity Cost | build time, maintenance load, opportunity loss | setup scope grows beyond markdown | ship minimum files first | automate tooling before proving workflow |
| Bayes and Probability | unknown count, evidence quality, confidence range | assumptions remain untested | define priors and required evidence | treat initial confidence as certainty |
| Systems Feedback Loop | local completion, weekly adoption, lag | local metrics improve but adoption is flat | pair local and system metrics in review | optimize one metric in isolation |

## Experiment Card
- Hypothesis: A hard-gated markdown workflow can turn the framework into executable behavior within one work session.
- Intervention: Create target directories, templates, three base model cards, one completed decision card, and rule updates.
- Primary metric: artifact completeness ratio.
- Expected delta: from 0 percent to 100 percent of required artifacts.
- Observation window: same day (single session).
- Review cadence: immediate post-implementation review.
- Data source: repository file checks and section presence validation.

## Execution Log
- Start date: 2026-02-17
- End date: 2026-02-17
- Actual metric values:
  - Required template artifacts: 3 of 3 present.
  - Hard-gate fields in sample card: 5 of 5 present.
  - Active rules added: 3.
- Unexpected events: no directory conflicts.

## Review
- Prediction vs Result: matched; minimum loop was implemented within scope.
- Main deviation: added 3 base model cards instead of only template card.
- Why deviation happened: lower retrieval friction for immediate usage outweighed minor extra effort.

## Rule Updates (1-3 only)
1. IF `Success Metrics` or `Stop Condition` is missing, THEN block execution until complete.
2. IF critical unknowns are 3 or more, THEN include Bayes and probability framing.
3. IF local metric rises but system metric is flat for 2 cycles, THEN run feedback-loop diagnosis.

## Linked Artifacts
- Related decision cards: `resources/decisions/TEMPLATE.decision-card.md`
- Related model cards:
  - `agent/patterns/mental-models/opportunity-cost.md`
  - `agent/patterns/mental-models/bayes-probability.md`
  - `agent/patterns/mental-models/systems-feedback-loop.md`
- Rule IDs: `R-20260217-01`, `R-20260217-02`, `R-20260217-03`
