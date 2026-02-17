# Model Card: Bayes and Probability

## One-Line Definition
Update confidence using new evidence instead of relying on fixed beliefs.

## When to Use
- High uncertainty with multiple plausible outcomes.
- Early-stage decisions where evidence is partial.
- Situations where new data arrives over time.

## Trigger Rules (testable if/then)
- IF probability interval width for success is greater than 0.30, THEN use this model.
- IF critical information gaps are 3 or more, THEN prioritize this model.

## When Not to Use
- Deterministic tasks with complete information.
- Decisions that are purely preference-based and non-quantitative.

## Common Misuse
- Treating one estimate as certainty.
- Ignoring base rates from historical decisions.
- Updating confidence without documenting evidence.

## Minimum Check Questions (exactly 3)
1. What is the prior probability and where did it come from?
2. Which new evidence changes the probability materially?
3. What range of outcomes remains after the update?

## Output Format
- Key variables: prior, evidence quality, posterior range.
- Key risks: overconfidence, weak data, hidden assumptions.
- Recommended action: run smallest reversible experiment to reduce uncertainty.
- Explicit non-actions: do not commit irreversible resources before update.

## Linked Decisions
- DEC-20260217-01

## Linked Rules
- R-20260217-02
