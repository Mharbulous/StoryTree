---
name: design-synthesis
description: Use when user says "synthesize designs", "show design patterns", "UI patterns", "UX patterns", "update design docs", or asks about UI/UX design decisions - generates two markdown files summarizing UI/UX patterns from implemented stories and anti-patterns from rejected or problematic UI/UX stories.
disable-model-invocation: true
---

# Design Synthesis Skill

Generate `patterns.md` and `anti-patterns.md` in `.claude/data/design/`.

## Workflow

### Step 1: Determine Mode

Check for `--as-is` argument and whether design files exist:

```bash
python .claude/scripts/design_synthesis_helpers.py prereq
```

**Mode Selection:**
- `--as-is` flag passed → **Codebase Analysis Mode**
- `patterns_exists` = false OR `anti_patterns_exists` = false → **Codebase Analysis Mode** (for missing files)
- Both files exist and no `--as-is` → **Incremental Update Mode**

**Exit early if (Incremental Mode only):**
- `needs_patterns_update` = false AND `needs_anti_patterns_update` = false (counts unchanged)

### Step 2A: Codebase Analysis Mode (First Run or --as-is)

When creating files from scratch or refreshing from codebase, spawn exploration agents:

**Agent 1 (patterns - codebase analysis):**
- Use Glob to find UI files: `**/*.py`, `**/*.qml`, `**/*.ui`, `**/*.tsx`, `**/*.vue`
- Focus on GUI frameworks: PySide6, PyQt, Tkinter, React, Vue, etc.
- Identify patterns for:
  - Widget/component organization
  - Layout management approaches
  - Color schemes and theming
  - Event handling patterns
  - State management in UI
  - Navigation patterns
  - Form validation approaches
  - Error display conventions
  - Loading/progress indicators
  - Responsive design patterns
- Read existing `.claude/data/design/patterns.md` if it exists (preserve valuable content)
- Write `.claude/data/design/patterns.md`

**Agent 2 (anti-patterns - codebase analysis):**
- Search for UI-related issues in code comments (TODO, FIXME, HACK, XXX)
- Look for deprecated UI patterns
- Check for accessibility issues (missing alt text, poor contrast references)
- Query rejected stories: `python .claude/scripts/design_synthesis_helpers.py anti-patterns`
- Read existing `.claude/data/design/anti-patterns.md` if it exists (preserve valuable content)
- Write `.claude/data/design/anti-patterns.md`

### Step 2B: Incremental Update Mode (Existing Files)

When design files exist, use them as authoritative guidance and update with new story data:

**Agent 1 (patterns)** - Only if `needs_patterns_update` is true:
- **Read existing `.claude/data/design/patterns.md` first** - this is the source of truth
- Query: `python .claude/scripts/design_synthesis_helpers.py patterns`
- Merge new story patterns while preserving existing documented patterns
- Write updated `.claude/data/design/patterns.md`

**Agent 2 (anti-patterns)** - Only if `needs_anti_patterns_update` is true:
- **Read existing `.claude/data/design/anti-patterns.md` first** - this is the source of truth
- Query: `python .claude/scripts/design_synthesis_helpers.py anti-patterns`
- Merge new story anti-patterns while preserving existing documented anti-patterns
- Write updated `.claude/data/design/anti-patterns.md`

### Step 3: Update Metadata

After agents complete, update the synthesis metadata:

```bash
python .claude/scripts/design_synthesis_helpers.py update-meta
```

## Document Structure

**patterns.md:**
- **Design Philosophy** - Core UI/UX principles guiding the project
- **Component Patterns** - Reusable UI component patterns (with code examples)
- **Interaction Patterns** - Standard user interaction flows
- **Layout Conventions** - Consistent layout approaches
- **Theming & Styling** - Color, typography, and visual consistency
- **Accessibility Standards** - A11y requirements and patterns
- Footer with timestamp

**anti-patterns.md:**
- **Rejected Approaches** - UI/UX ideas explicitly rejected (with rejection reasons)
- **Usability Issues** - Known usability problems to avoid
- **Visual Anti-Patterns** - Visual design mistakes to avoid
- **Interaction Anti-Patterns** - Poor interaction patterns to avoid
- **Performance Concerns** - UI patterns that cause performance issues
- Footer with timestamp

## Key Rules

- Spawn agents in parallel, never sequentially
- Use Python sqlite3 module, NOT sqlite3 CLI
- **Codebase Analysis Mode:** Derive patterns from actual implementation
- **Incremental Mode:** Existing files are authoritative - preserve and extend
- Include rejection reasons in anti-patterns bullets
- Always run update-meta after successful synthesis
- Focus on UI/UX-related stories (keywords: ui, ux, design, layout, component, button, form, modal, dialog, menu, navigation, style, theme, color, font, icon, responsive, accessibility, a11y)
