# StoryTree

Story-driven development orchestration tool for Claude Code.

## Overview

StoryTree provides a complete workflow for managing development stories in Claude Code projects:

- **Story Tree**: Hierarchical story management with closure table pattern
- **CI/CD Integration**: GitHub Actions workflows for automated story processing
- **Xstory GUI**: Visual story tree explorer and editor (PySide6)
- **Skills & Commands**: Claude Code integration for story operations

## Installation

StoryTree is installed as a **git submodule** with **relative symlinks**.

### Adding StoryTree to a New Project

```bash
cd /path/to/your-project

# 1. Add StoryTree as a git submodule (hidden directory)
git submodule add https://github.com/Mharbulous/StoryTree.git .StoryTree

# 2. Create relative symlinks (see Symlink Setup below)

# 3. Initialize the story database
cp .StoryTree/templates/story-tree.db.empty .claude/data/story-tree.db

# 4. Copy GitHub workflows (GitHub doesn't follow symlinks)
cp -r .StoryTree/github/workflows/* .github/workflows/
cp -r .StoryTree/github/actions/* .github/actions/
```

### Cloning a Project with StoryTree

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/YourOrg/YourProject.git

# Or initialize submodules after cloning
git clone https://github.com/YourOrg/YourProject.git
cd YourProject
git submodule update --init --recursive
```

### Symlink Setup

Create relative symlinks from your project's `.claude/` directory to StoryTree components. Use Python for cross-platform compatibility:

```python
# Run from your project root directory
import os
from pathlib import Path

# Skills (10 total)
skills_src = Path('.StoryTree/.claude/skills')
skills_dst = Path('.claude/skills')
for skill in ['code-sentinel', 'concept-vetting', 'goal-synthesis', 'prioritize-story-nodes',
              'story-arborist', 'story-building', 'story-execution',
              'story-planning', 'story-tree', 'story-verification']:
    src = skills_src / skill
    dst = skills_dst / skill
    rel_path = os.path.relpath(src, skills_dst)
    os.symlink(rel_path, dst, target_is_directory=True)

# Commands (10 total)
cmds_src = Path('.StoryTree/.claude/commands')
cmds_dst = Path('.claude/commands')
for cmd in ['ci-decompose-plan.md', 'ci-execute-plan.md', 'ci-identify-plan.md',
            'ci-create-plan.md', 'ci-generate-concept.md', 'ci-review-plan.md',
            'review-stories.md', 'synthesize-goals.md', 'vet-concepts.md', 'write-story.md']:
    src = cmds_src / cmd
    dst = cmds_dst / cmd
    rel_path = os.path.relpath(src, cmds_dst)
    os.symlink(rel_path, dst)

# Scripts (5 total)
scripts_src = Path('.StoryTree/.claude/scripts')
scripts_dst = Path('.claude/scripts')
for script in ['generate_vision_doc.py', 'insert_story.py', 'prioritize_stories.py',
               'story_tree_helpers.py', 'story_workflow.py']:
    src = scripts_src / script
    dst = scripts_dst / script
    rel_path = os.path.relpath(src, scripts_dst)
    os.symlink(rel_path, dst)

# Data scripts (4 total)
data_src = Path('.StoryTree/.claude/data')
data_dst = Path('.claude/data')
for script in ['init_story_tree.py', 'insert_stories.py',
               'migrate_normalize_stage_hierarchy.py', 'verify_root.py']:
    src = data_src / script
    dst = data_dst / script
    rel_path = os.path.relpath(src, data_dst)
    os.symlink(rel_path, dst)
```

**Windows Requirement**: Developer Mode must be enabled (Settings > Privacy & Security > For developers).

### Updating StoryTree

```bash
cd .StoryTree
git pull origin main
cd ..
git add .StoryTree
git commit -m "chore: update StoryTree submodule"
git push
```

**Workflow Sync**: After pushing, the `sync-storytree-workflows` action will automatically create a PR if any GitHub workflows changed in StoryTree. Review and merge that PR to complete the update.

### Managing Multiple Projects

If you have multiple projects using StoryTree, you can register them for batch updates:

```bash
# Register projects (one-time setup, run from StoryTree directory)
python src/setup.py register --target /path/to/SyncoPaid --name SyncoPaid
python src/setup.py register --target /path/to/Listbot --name Listbot

# List registered projects
python src/setup.py list-dependents

# After pulling StoryTree updates, sync workflows to ALL projects
python src/setup.py update-all

# Remove a project from registry
python src/setup.py unregister --target /path/to/Project
```

The `update-all` command copies workflows to all registered projects at once, then prompts you to commit the changes in each project.

## Component Organization

Components are organized by their usage scope using a dot-prefix convention:

| Usage Scope | Location | Description |
|-------------|----------|-------------|
| **StoryTree only** | `.claude/`, `.github/` | Components active only in StoryTree |
| **Dependents only** | `claude/`, `github/` | Components exported to dependent repos |
| **Both** | `claude/`, `github/` + symlinks | Shared components (source in non-dot, symlink in dot) |

**Exception:** `src/setup.py` is used by both StoryTree and dependents.

**How it works:**
- Claude Code reads from `.claude/` — this is what's "active" in a project
- GitHub Actions read from `.github/` — this is what runs in a project
- Dependent repos get components from `claude/` and `github/` via symlinks or copies
- To share a component with dependents, place it in `claude/` or `github/` and optionally symlink from `.claude/` or `.github/` if StoryTree also uses it

## Directory Structure

```
StoryTree/
├── README.md
├── CLAUDE.md
├── src/
│   └── setup.py             # Installation & management (used by both)
│
├── .claude/                 # Active in StoryTree
│   ├── skills/              # StoryTree-only skills
│   ├── commands/            # StoryTree-only commands
│   ├── scripts/             # Helper scripts
│   └── data/                # Database & scripts
│
├── .github/                 # Active in StoryTree
│   └── workflows/           # StoryTree-only workflows
│
├── claude/                  # Exported to dependents
│   ├── skills/              # Shared skills (story-tree, story-planning, etc.)
│   └── commands/            # Shared commands (ci-*.md, write-story.md, etc.)
│
├── github/                  # Exported to dependents
│   ├── workflows/           # Shared workflows (story-tree-orchestrator.yml, etc.)
│   └── actions/             # Custom composite actions
│
├── gui/                     # Xstory visual explorer
│   ├── xstory.py
│   ├── requirements.txt
│   └── tests/
│
└── templates/
    └── story-tree.db.empty  # Empty database template
```

## Project Integration Structure

After installation, your project will have:

```
YourProject/
├── .StoryTree/               ← Git submodule (hidden directory)
├── .claude/
│   ├── skills/
│   │   ├── story-tree/       ← Symlink → ../../.StoryTree/.claude/skills/story-tree
│   │   └── ...               ← (other symlinked skills)
│   ├── commands/
│   │   └── *.md              ← Symlinks → ../../.StoryTree/.claude/commands/*.md
│   ├── scripts/
│   │   └── *.py              ← Symlinks → ../../.StoryTree/.claude/scripts/*.py
│   └── data/
│       ├── story-tree.db     ← Project-specific (NOT symlinked)
│       └── *.py              ← Symlinks → ../../.StoryTree/.claude/data/*.py
└── .github/
    └── workflows/            ← Copied from StoryTree (GitHub requires actual files)
```

## CI Configuration

GitHub Actions workflows require explicit submodule checkout:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive
```

**Note**: StoryTree must be a **public** repository for GitHub Actions to clone it.

## Database Schema

The story tree uses SQLite with a closure table pattern for efficient hierarchical queries.

Key tables:
- `story_nodes`: Story definitions with three-field workflow system
- `story_paths`: Closure table for ancestor/descendant relationships
- `story_commits`: Commit tracking per story
- `vetting_decisions`: Entity resolution cache

See `.claude/skills/story-tree/references/schema.sql` for full schema.

## Workflow Stages

Stories progress through these stages:

```
concept → planning → executing → reviewing → verifying → implemented → ready → released
```

Stories can be held (queued, pending, blocked, etc.) or disposed (rejected, archived, etc.) at any stage.

## Xstory GUI

Xstory is a visual story tree explorer built with PySide6 (Qt for Python).

### Running Xstory

```bash
# Install dependencies
pip install -r .StoryTree/gui/requirements.txt

# Run the GUI (from project root)
python .StoryTree/gui/xstory.py

# Or specify a database path
python .StoryTree/gui/xstory.py --db .claude/data/story-tree.db
```

### Features

- Visual tree navigation with expand/collapse
- Story node editing (title, description, stage, hold/dispose status)
- Stage progression tracking
- Parent-child relationship management
- Database integrity verification

### Building Standalone Executable

```bash
cd .StoryTree/gui
python build.py
```

## Troubleshooting

### Symlinks Appear as Text Files (Windows)

After a fresh clone, symlinks may appear as text files containing the target path.

**Fix**: Recreate symlinks using the Python script in the Installation section. Requires Developer Mode enabled.

### "Permission denied" Creating Symlinks

**Windows**: Enable Developer Mode (Settings > Privacy & Security > For developers).

**Linux/macOS**: Should work natively. Check directory permissions.

### Submodule Not Cloned

If the `.StoryTree/` directory is empty:

```bash
git submodule update --init --recursive
```

### CI Can't Access Submodule

Ensure:
1. StoryTree repository is **public**
2. Checkout action uses `submodules: recursive`:
   ```yaml
   - uses: actions/checkout@v4
     with:
       submodules: recursive
   ```

### Database Errors

If story-tree.db is corrupted:
1. Run Xstory GUI to diagnose
2. Check for backups in `.claude/data/`
3. Last resort: `cp .StoryTree/templates/story-tree.db.empty .claude/data/story-tree.db`

## License

MIT
