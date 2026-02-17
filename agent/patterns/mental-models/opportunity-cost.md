# Model Card: Opportunity Cost

## One-Line Definition
Choose actions by comparing what you gain against the best alternative you must give up.

## When to Use
- Time or budget is fixed.
- Multiple initiatives compete for the same resources.
- Prioritization decisions with clear trade-offs.

## Trigger Rules (testable if/then)
- IF available execution time is less than 7 days, THEN use this model.
- IF budget ceiling is fixed and expected tasks exceed capacity, THEN prioritize this model.

## When Not to Use
- Unlimited resource simulation tasks.
- Pure exploration phases with no commitment needed.

## Common Misuse
- Comparing options without a baseline alternative.
- Ignoring hidden maintenance costs.
- Maximizing local output while harming global priorities.

## Minimum Check Questions (exactly 3)
1. What is the best alternative use of the same resources?
2. What is the total cost of each option, including maintenance?
3. What value is delayed or lost if this option is chosen?

## Output Format
- Key variables: time, budget, expected value, maintenance burden.
- Key risks: sunk-cost bias, undercounted downstream cost.
- Recommended action: select highest expected value per constrained unit.
- Explicit non-actions: do not start low-leverage work in constrained windows.

## Linked Decisions
- DEC-20260217-01

## Linked Rules
- R-20260217-01
