# Model Card: Systems Feedback Loop

## One-Line Definition
Track how local actions feed back into the whole system over time, including delays.

## When to Use
- Outcomes change in the opposite direction of local improvements.
- Repeated interventions produce diminishing or unstable results.
- Cross-team or cross-process dependencies are present.

## Trigger Rules (testable if/then)
- IF a primary metric moves opposite to intent for 2 consecutive cycles, THEN use this model.
- IF local KPI improves while global KPI declines in the same period, THEN prioritize this model.

## When Not to Use
- Single-step deterministic tasks with no delayed effects.
- One-off actions with no recurring feedback.

## Common Misuse
- Optimizing one metric without system-level checks.
- Ignoring delay between action and signal.
- Treating symptoms as root causes.

## Minimum Check Questions (exactly 3)
1. Which loop is reinforcing and which is balancing?
2. Where are the delay points that can mislead interpretation?
3. What system metric must stay healthy while local metrics improve?

## Output Format
- Key variables: local KPI, global KPI, lag duration, dependency map.
- Key risks: local optimization trap, delayed side effects.
- Recommended action: monitor paired local/global metrics with lag-aware review.
- Explicit non-actions: do not ship interventions without system guardrails.

## Linked Decisions
- DEC-20260217-01

## Linked Rules
- R-20260217-03
