# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

StoryTree is a story-driven development orchestration tool for Claude Code. It provides hierarchical story management using a SQLite database with a closure table pattern, plus a PySide6-based visual GUI (Xstory) for story tree exploration.

This repository is designed to be installed as a **git submodule** in other projects, with symlinks providing access to skills, commands, and scripts.

## Key Commands

### Setup & Installation

```bash
# Install to a target project
python setup.py install --target /path/to/project

# Initialize empty story database
python setup.py init-db --target /path/to/project

# Sync workflows after StoryTree updates
python setup.py sync-workflows --target /path/to/project

# Manage dependent projects
python setup.py register --target /path/to/project --name ProjectName
python setup.py list-dependents
python setup.py update-all  # Sync workflows to all registered projects
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

### Directory Structure

- `claude/` - Claude Code integration components
  - `skills/` - 10 Claude Code skills (story-tree, story-planning, story-execution, etc.)
  - `commands/` - 10 slash commands (ci-create-plan.md, write-story.md, ci-*.md, etc.)
  - `scripts/` - Helper Python scripts for story operations
  - `data/` - Database initialization and migration scripts
- `gui/` - Xstory visual tree explorer (PySide6)
  - `xstory.py` - Main 99K LOC GUI application
  - `migrate_*.py` - Database migration scripts
- `github/` - GitHub Actions workflows and composite actions
  - `workflows/` - CI pipeline workflows (story orchestrator, execution, review, etc.)
  - `actions/` - Custom composite actions
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
