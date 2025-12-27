Invoke the `design-synthesis` skill to generate/update UI/UX patterns and anti-patterns documentation.

## Usage

```
/synthesize-designs [--as-is]
```

## Options

- `--as-is` - Analyze the current codebase UI/UX implementation to derive patterns, even if design documents already exist

## Behavior

- **First run (no existing files):** Analyzes the codebase to discover current UI/UX patterns and anti-patterns
- **Subsequent runs:** Takes guidance from existing `.claude/data/design/patterns.md` and `anti-patterns.md`, updating with new story data
- **With `--as-is`:** Forces codebase analysis to refresh patterns based on current implementation
