# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

StoryTree is a story-driven development orchestration tool for Claude Code. It provides hierarchical story management using a SQLite database with a closure table pattern, plus a PySide6-based visual GUI (Xstory) for story tree exploration.

This repository is designed to be installed as a **git submodule** in other projects, with symlinks providing access to skills, commands, and scripts.

## Key Commands

### Setup & Installation

```bash
# Install to a target project
python src/setup.py install --target /path/to/project

# Initialize empty story database
python src/setup.py init-db --target /path/to/project

# Sync workflows after StoryTree updates
python src/setup.py sync-workflows --target /path/to/project

# Manage dependent projects
python src/setup.py register --target /path/to/project --name ProjectName
python src/setup.py list-dependents
python src/setup.py update-all  # Sync workflows to all registered projects
```

### Xstory GUI

```bash
# Install dependencies
pip install -r gui/requirements.txt

# Run GUI (specify database path)
python gui/xstory.py --db /path/to/story-tree.db

# Build standalone executable
python gui/build.py
```

### GUI Tests

```bash
# Run migration tests
python -m pytest gui/tests/ -v
```

## Architecture

### Component Organization Convention

Components are organized based on their usage scope:

| Usage Scope | Location | Examples |
|-------------|----------|----------|
| **StoryTree only** | `.claude/`, `.github/` | StoryTree-specific skills, internal workflows |
| **Dependents only** | `claude/`, `github/` | Skills/commands/workflows for dependent repos |
| **Both** | `claude/`, `github/` with symlinks from `.claude/`, `.github/` | Shared components used by both |

**Exception:** `src/setup.py` is used by both StoryTree and dependents (handles installation and dependent management).

**Key principle:** The dot-prefixed directories (`.claude/`, `.github/`) are what Claude Code and GitHub Actions read. The non-dot directories (`claude/`, `github/`) contain exportable components for dependent repos.

### Repo-Agnostic vs Repo-Specific Files

| File Type | Location | Examples |
|-----------|----------|----------|
| **Repo-agnostic** | `claude/`, `github/` (source of truth) | `SKILL.md`, `schema.sql`, command templates, workflows |
| **Repo-specific** | `.claude/`, `.github/` only (not exported) | `file-inventory.json`, `story-tree.db`, `settings.local.json` |

**Rule:** If StoryTree uses a repo-agnostic file, symlink from `.claude/`/`.github/` → `claude/`/`github/`.

**Example:** For the `streamline` skill:
```
claude/skills/streamline/SKILL.md              # Agnostic (source)
.claude/skills/streamline/SKILL.md             # Symlink → ../../claude/...
.claude/skills/streamline/references/
    file-inventory.json                        # Repo-specific (original, not in claude/)
```

### Directory Structure

- `.claude/` - Claude Code components **active in StoryTree**
  - `skills/` - StoryTree-only skills (e.g., `streamline`)
  - `commands/` - StoryTree-only commands
  - `scripts/` - Helper Python scripts
  - `data/` - Database scripts and `story-tree.db`
- `.github/` - GitHub workflows **active in StoryTree**
  - `workflows/` - StoryTree-only workflows (e.g., `notify-dependents.yml`)
- `claude/` - Components **exported to dependent repos**
  - `skills/` - Shared skills (story-tree, story-planning, etc.)
  - `commands/` - Shared commands (ci-*.md, write-story.md, etc.)
- `github/` - GitHub components **exported to dependent repos**
  - `workflows/` - Shared workflows (story-tree-orchestrator.yml, etc.)
  - `actions/` - Custom composite actions
- `src/` - Shared utilities
  - `setup.py` - Installation and dependent management (used by both)
- `gui/` - Xstory visual tree explorer (PySide6)
- `templates/` - Empty database template (`story-tree.db.empty`)

### Database Schema

The story tree uses SQLite with a closure table pattern:

- `story_nodes` - Story definitions with three-field workflow (stage, hold_reason, disposition)
- `story_paths` - Closure table for ancestor/descendant relationships
- `story_commits` - Commit tracking per story
- `vetting_decisions` - Entity resolution cache for deduplication

**Three-Field Workflow System:**
- **Stage** (8 values): concept → planning → executing → reviewing → verifying → implemented → ready → released
- **Hold Reason** (8 values + NULL): broken, conflicted, blocked, escalated, paused, polish, queued, wishlisted
- **Disposition** (6 values + NULL): infeasible, rejected, duplicative, deprecated, legacy, archived

### Story ID Format

| Level | Parent | Format | Examples |
|-------|--------|--------|----------|
| Root | None | `root` | `root` |
| Level 1 | `root` | Plain integer | `1`, `2`, `15` |
| Level 2+ | Any non-root | `[parent].[N]` | `1.1`, `8.4`, `15.2.1` |

**Critical:** Primary epics (children of root) must have plain integer IDs, not decimal format.

### Submodule Installation Pattern

When installed in a project:
1. StoryTree lives at `.StoryTree/` as a git submodule
2. Symlinks connect `.claude/skills/`, `.claude/commands/`, `.claude/scripts/` to StoryTree
3. GitHub workflows are **copied** (not symlinked) because GitHub Actions doesn't follow symlinks
4. Database lives at `.claude/data/story-tree.db` (project-specific, not symlinked)

### Environment Notes

- **sqlite3 CLI is not available** - Always use Python's sqlite3 module for database operations
- **Windows symlinks require Developer Mode** (Settings > Privacy & Security > For developers)
- **GitHub Actions** require `submodules: recursive` in checkout step
