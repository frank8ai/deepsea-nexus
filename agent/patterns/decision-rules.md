# Decision Rules

## Operating Constraints
- Add only 1-3 rule updates per decision review.
- Every rule must be testable (`if/then` plus threshold or explicit signal).
- Every rule must link to a source decision card.

## Rule Template
### R-YYYYMMDD-XX: <short-title>
- Status: active | draft | retired
- Source decision:
- Added on:
- Review on:
- When (condition):
- Then (model or strategy):
- Check (questions):
- Avoid (pitfall):
- Threshold or Signal:
- Validation metric:

## Active Rules

### R-20260217-01: Gate before execution
- Status: active
- Source decision: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF a decision card misses either `Success Metrics` or `Stop Condition`, THEN execution is blocked.
- Then (model or strategy): Apply constraints optimization and complete missing fields before selecting actions.
- Check (questions): Are metrics numeric thresholds; Is at least one stop trigger explicit; Are constraints measurable.
- Avoid (pitfall): Launching execution with only qualitative goals.
- Threshold or Signal: Presence check for both sections plus at least one numeric threshold.
- Validation metric: 100 percent of completed decision cards pass hard gates.

### R-20260217-02: Uncertainty requires probability framing
- Status: active
- Source decision: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF critical information gaps are 3 or more, THEN include Bayes and probability in the 3-model set.
- Then (model or strategy): Convert assumptions into priors and list evidence needed for update.
- Check (questions): Is prior stated; Is update evidence defined; Is posterior range captured.
- Avoid (pitfall): Treating first estimates as fixed truth.
- Threshold or Signal: Count of unresolved critical unknowns.
- Validation metric: 100 percent of high-uncertainty cards include probability update fields.

### R-20260217-03: Protect system outcome from local optimization
- Status: active
- Source decision: `resources/decisions/2026-02/2026-02-17-closed-loop-pilot.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF local progress is positive but system adoption is flat or declining for 2 cycles, THEN run feedback-loop diagnosis.
- Then (model or strategy): Pair one local metric with one system metric and inspect lag.
- Check (questions): Which loop is reinforcing; Which loop is balancing; What lag exists.
- Avoid (pitfall): Declaring success from isolated local metrics.
- Threshold or Signal: Two consecutive cycles of local-global divergence.
- Validation metric: Every weekly review includes one local and one system metric.

### R-20260217-04: Route repeatable work into SOP Factory
- Status: active
- Source decision: `resources/sop/2026-02/2026-02-17-weekly-decision-review-sop.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF task frequency is 3 or more per month AND outcome variation coefficient is 0.20 or less, THEN route to SOP Factory.
- Then (model or strategy): Use three-optimal scorecard and publish SOP v1 before next cycle.
- Check (questions): Is frequency validated; Is variance measured; Are hard gates complete.
- Avoid (pitfall): Treating exploratory tasks as stable SOP.
- Threshold or Signal: frequency >= 3 per month and CV <= 0.20.
- Validation metric: 100 percent of qualified repeat tasks have active SOP documents.

### R-20260217-05: Active SOP must pass strict validator
- Status: active
- Source decision: `resources/sop/2026-02/2026-02-17-weekly-decision-review-sop.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF SOP status is `active`, THEN strict validation must pass before release or update.
- Then (model or strategy): Run `python3 scripts/validate_sop_factory.py --sop <path> --strict` and block release on failure.
- Check (questions): Are all hard gates checked; Are scorecard thresholds met; Is pilot run count >= 5.
- Avoid (pitfall): Publishing process docs without machine-verifiable gates.
- Threshold or Signal: validator exit code must be 0.
- Validation metric: 100 percent of active SOP updates include a successful strict validation run.

### R-20260217-06: Evidence must scale with irreversibility
- Status: active
- Source decision: `resources/sop/2026-02/2026-02-17-weekly-decision-review-sop.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF SOP release has reversibility class `R1`, `R2`, or `R3`, THEN enforce minimum evidence tier `E2`, `E3`, or `E4` respectively.
- Then (model or strategy): Block activation until evidence tier meets mapping and is documented in metadata.
- Check (questions): Is reversibility class declared; Is evidence tier declared; Does mapping pass.
- Avoid (pitfall): Shipping high-blast-radius SOPs on weak evidence.
- Threshold or Signal: `R1->E2`, `R2->E3`, `R3->E4`.
- Validation metric: 100 percent of active SOPs satisfy reversibility-evidence mapping.

### R-20260217-07: Search relevance gate requires second pass
- Status: active
- Source decision: `resources/sop/2026-02/2026-02-17-search-recall-sop.md`
- Added on: 2026-02-17
- Review on: 2026-03-03
- When (condition): IF first-pass top1 relevance is below 0.35 OR first-pass top3 median relevance is below 0.25, THEN second-pass expansion is mandatory.
- Then (model or strategy): Run up to 2 rewritten queries with `n=8`, merge and rerank before response.
- Check (questions): Did first-pass gate fail; Did second-pass run; Did final results include source and relevance.
- Avoid (pitfall): Returning weak first-pass results without refinement.
- Threshold or Signal: `top1 < 0.35` OR `median(top3) < 0.25`.
- Validation metric: 100 percent of failed first-pass searches have documented second-pass execution.
