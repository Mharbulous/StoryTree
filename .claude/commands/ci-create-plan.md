Create implementation plans for stories in the planning stage.

## Arguments

$Arguments

## CI Mode

CI mode auto-activates when `CI=true` env var is set or trigger includes "(ci)".
Uses compact template (~60% token reduction).

## Argument Handling

- **Specific ID(s)**: `/ci-create-plan 1.8.2` or `/ci-create-plan 1.2 1.3 1.4`
- **Count**: `/ci-create-plan 3` → plan top 3 priority stories
- **No arguments**: Plan single highest-priority story in planning stage

## Constraints

- Maximum 5 plans per invocation
- Only stories with `stage = 'planning'` and no hold_reason (not disposed)
- Skip non-existent/non-planning IDs with error message, continue with remaining
- If fewer planning stories than requested, plan all available

## Execution

Invoke `story-planning` skill, then:
- Process stories sequentially
- Create separate plan files
- Update each story's stage to `executing`
- Summary report at end listing all plans created
