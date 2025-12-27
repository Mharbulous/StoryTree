# StoryTree Transition Plan

## Overview

This document outlines the steps required to complete the transition of StoryTree components from the SyncoPaid repository into the standalone StoryTree repository, and how to set up StoryTree for use in other projects.

## Naming Convention

- **StoryTree**: The repository and overall project for story-driven development orchestration
- **Xstory** (eXploreStory): The Python GUI tool (PySide6) for visually exploring the story tree

---

## Integration Approach: Git Submodule + Relative Symlinks

StoryTree is integrated into projects using **git submodules** with **relative symlinks**:

```
YourProject/
├── .StoryTree/             ← Git submodule (https://github.com/Mharbulous/StoryTree)
├── .claude/
│   ├── skills/
│   │   ├── story-tree/     ← Symlink → ../../.StoryTree/claude/skills/story-tree
│   │   └── ...
│   ├── commands/
│   │   └── *.md            ← Symlinks → ../../.StoryTree/claude/commands/*.md
│   └── data/
│       └── story-tree.db   ← Project-specific (NOT symlinked)
└── .github/
    └── workflows/          ← Copied from StoryTree (GitHub requires actual files)
```

### Why This Approach?

| Approach | Pros | Cons |
|----------|------|------|
| **Git Submodule** | Portable, version-controlled, works in CI | Requires `--recurse-submodules` on clone |
| ~~Absolute symlinks~~ | Simple | Breaks on other machines/CI |
| ~~setup.py installer~~ | Flexible | Extra step, complex CI setup |

### Requirements

- **Windows**: Developer Mode enabled (Settings → Privacy & Security → For developers)
- **Linux/macOS**: Symlinks work natively
- **Git clone**: Use `git clone --recurse-submodules` or run `git submodule update --init`

---

## Critical Requirement: CI Continuity

**The existing StoryTree components in SyncoPaid must continue working throughout this transition.**

1. **No destructive changes** until the new setup is fully validated
2. **Parallel operation** - old and new must coexist during testing
3. **CI validation** - run CI workflows against the new setup before switching
4. **Rollback capability** - ability to revert to original setup at any point

### Transition Strategy

```
Phase 1: Validate StoryTree repo (no changes to SyncoPaid)
    ↓
Phase 2: Test in isolated branch (main branch + CI unaffected)
    ↓
Phase 3: Validate CI passes on test branch
    ↓
Phase 4: Merge and switch over (backup still available)
    ↓
Phase 5: Set up Listbot (after SyncoPaid stable)
    ↓
Phase 6: Cleanup (only after CI stable for several days)
    ↓
Phase 7: Documentation
```

**At any point before Phase 6, you can rollback to the original setup.**

---

## Phase 1: Validate StoryTree Repository (No SyncoPaid Changes)

### 1.1 Verify Repository Structure

Confirm all essential components are present:

```
StoryTree/
├── setup.py             # Optional installer script (for database init)
├── README.md            # Project documentation
├── claude/
│   ├── skills/          # 10 skills
│   ├── commands/        # 10 slash commands
│   ├── scripts/         # Helper scripts
│   └── data/            # DB initialization scripts
├── github/
│   ├── workflows/       # CI workflows
│   └── actions/         # Composite actions
├── gui/                 # Xstory GUI tool
└── templates/
    └── story-tree.db.empty
```

### 1.2 Component Inventory

| Component | Count | Notes |
|-----------|-------|-------|
| Skills | 10 | story-writing merged into story-building |
| Commands | 10 | Slash commands for Claude Code |
| Scripts | 5 | Python helper scripts |
| Workflows | 8 | GitHub Actions workflows |
| Xstory GUI | 1 | In `gui/` folder |

---

## Phase 2: Test StoryTree Integration in Isolated Branch

**Goal**: Test the new StoryTree setup without affecting the working main branch or CI.

### 2.1 Create Test Branch in SyncoPaid

```bash
cd C:\Users\Brahm\Git\SyncoPaid
git checkout -b test/storytree-integration
```

### 2.2 Backup Current State (Safety Net)

```bash
# Create backup (stays local, not committed)
cp -r .claude .claude.backup-$(date +%Y%m%d)
```

### 2.3 Identify Components to Preserve

Components in SyncoPaid that should NOT be replaced (project-specific):

| Path | Reason |
|------|--------|
| `.claude/data/story-tree.db` | Contains SyncoPaid's story data |
| `.claude/data/goals/` | SyncoPaid-specific goals |
| `.claude/data/plans/` | SyncoPaid-specific plans |
| `.claude/settings.local.json` | Project settings |
| `.claude/skills/streamline/` | SyncoPaid-specific skill |
| `.claude/skills/skill-refinement/` | SyncoPaid-specific skill |
| `.claude/skills/user-manual-generator/` | SyncoPaid-specific skill |

### 2.4 Remove Old StoryTree Files and Add as Submodule

```bash
cd C:\Users\Brahm\Git\SyncoPaid

# If StoryTree exists as regular files, remove from index
git rm -r --cached StoryTree 2>/dev/null
rm -rf StoryTree

# Add as git submodule (hidden directory)
git submodule add https://github.com/Mharbulous/StoryTree.git .StoryTree
```

### 2.5 Remove StoryTree-Managed Components

Remove components that will be replaced by symlinks:

```bash
cd C:\Users\Brahm\Git\SyncoPaid\.claude\skills
rm -rf code-sentinel goal-synthesis prioritize-story-nodes
rm -rf story-arborist story-building story-execution
rm -rf story-planning story-tree story-verification concept-vetting

cd C:\Users\Brahm\Git\SyncoPaid\.claude\commands
rm -f ci-decompose-plan.md ci-execute-plan.md ci-identify-plan.md ci-review-plan.md
rm -f generate-stories.md plan-story.md review-stories.md
rm -f synthesize-goals.md vet-stories.md write-story.md

cd C:\Users\Brahm\Git\SyncoPaid\.claude\scripts
rm -f generate_vision_doc.py insert_story.py prioritize_stories.py
rm -f story_tree_helpers.py story_workflow.py

cd C:\Users\Brahm\Git\SyncoPaid\.claude\data
rm -f init_story_tree.py insert_stories.py migrate_normalize_stage_hierarchy.py verify_root.py
```

### 2.6 Create Relative Symlinks

Use Python to create proper Windows symlinks with relative paths:

```python
# Run from SyncoPaid root directory
import os
from pathlib import Path

# Skills
skills_src = Path('.StoryTree/claude/skills')
skills_dst = Path('.claude/skills')
for skill in ['code-sentinel', 'concept-vetting', 'goal-synthesis', 'prioritize-story-nodes',
              'story-arborist', 'story-building', 'story-execution',
              'story-planning', 'story-tree', 'story-verification']:
    src = skills_src / skill
    dst = skills_dst / skill
    rel_path = os.path.relpath(src, skills_dst)
    os.symlink(rel_path, dst, target_is_directory=True)

# Commands
cmds_src = Path('.StoryTree/claude/commands')
cmds_dst = Path('.claude/commands')
for cmd in ['ci-decompose-plan.md', 'ci-execute-plan.md', 'ci-identify-plan.md',
            'ci-review-plan.md', 'generate-stories.md', 'plan-story.md',
            'review-stories.md', 'synthesize-goals.md', 'vet-stories.md', 'write-story.md']:
    src = cmds_src / cmd
    dst = cmds_dst / cmd
    rel_path = os.path.relpath(src, cmds_dst)
    os.symlink(rel_path, dst)

# Scripts
scripts_src = Path('.StoryTree/claude/scripts')
scripts_dst = Path('.claude/scripts')
for script in ['generate_vision_doc.py', 'insert_story.py', 'prioritize_stories.py',
               'story_tree_helpers.py', 'story_workflow.py']:
    src = scripts_src / script
    dst = scripts_dst / script
    rel_path = os.path.relpath(src, scripts_dst)
    os.symlink(rel_path, dst)

# Data scripts
data_src = Path('.StoryTree/claude/data')
data_dst = Path('.claude/data')
for script in ['init_story_tree.py', 'insert_stories.py',
               'migrate_normalize_stage_hierarchy.py', 'verify_root.py']:
    src = data_src / script
    dst = data_dst / script
    rel_path = os.path.relpath(src, data_dst)
    os.symlink(rel_path, dst)
```

### 2.7 Verify Symlinks

```bash
# Windows
dir /AL .claude\skills

# Should show:
# <SYMLINKD>  story-tree [..\..\.StoryTree\claude\skills\story-tree]
```

### 2.8 Test Local Functionality

1. Read a skill file through the symlink
2. Verify database is accessible (117 story nodes)
3. Run Xstory GUI: `python .StoryTree\gui\xstory.py`

### 2.9 If Tests Fail: Rollback

```bash
cd C:\Users\Brahm\Git\SyncoPaid
git checkout main  # Return to working main branch
git branch -D test/storytree-integration  # Delete failed test branch
```

---

## Phase 3: Validate CI with New Setup

**Goal**: Ensure CI workflows pass with the StoryTree integration before merging.

### 3.1 CI Submodule Configuration

CI environments need to clone submodules. Update workflows to use:

```yaml
- uses: actions/checkout@v4
  with:
    submodules: recursive
```

### 3.2 Symlinks in CI (Linux)

Linux CI environments support symlinks natively. The relative symlinks will work as long as the submodule is checked out.

### 3.3 Commit and Push Test Branch

```bash
cd C:\Users\Brahm\Git\SyncoPaid
git add .
git commit -m "refactor: integrate StoryTree as git submodule with relative symlinks"
git push -u origin test/storytree-integration
```

### 3.4 Run CI Workflows

1. Open GitHub Actions for SyncoPaid
2. Manually trigger story-related workflows on `test/storytree-integration` branch
3. Verify all workflows pass

### 3.5 If CI Fails

- Check that `submodules: recursive` is in checkout action
- Verify symlinks resolve correctly on Linux
- Fix issues and re-push

---

## Phase 4: Merge and Switch Over

**Goal**: Merge the validated integration into main, while keeping rollback capability.

### 4.1 Merge Test Branch

```bash
cd C:\Users\Brahm\Git\SyncoPaid
git checkout main
git merge test/storytree-integration
git push
```

### 4.2 Verify Main Branch CI

1. CI should automatically run on the push to main
2. Monitor all story-related workflows
3. Confirm they pass

### 4.3 Keep Backup Available

Do NOT delete the backup yet:
- Keep `.claude.backup-YYYYMMDD` locally
- Monitor for issues over several days

---

## Phase 5: Set Up Listbot to Use StoryTree

**Prerequisite**: Phase 4 complete and stable for SyncoPaid.

### 5.1 Add StoryTree as Submodule

```bash
cd C:\Users\Brahm\Git\Listbot
git submodule add https://github.com/Mharbulous/StoryTree.git .StoryTree
```

### 5.2 Create Relative Symlinks

Use the same Python script from Phase 2.6.

### 5.3 Initialize Database (New Project)

```bash
# Copy empty database template
cp .StoryTree/templates/story-tree.db.empty .claude/data/story-tree.db
```

Or use the setup script:

```bash
python .StoryTree/setup.py init-db --target .
```

### 5.4 Verify Installation

Same verification steps as SyncoPaid (Phase 2.7-2.8).

---

## Phase 6: Cleanup SyncoPaid (Only After Stability Confirmed)

**Prerequisite**: CI has been stable for at least several days after Phase 4.

### 6.1 Remove Backup

```bash
rm -rf .claude.backup-YYYYMMDD
```

### 6.2 Remove Legacy Files

```bash
# Remove old xstory directory if it exists
rm -rf xstory/

# Remove legacy story files
rm -f .claude/skills/execute-story-workflow.md
```

### 6.3 Update CLAUDE.md

Add reference to StoryTree dependency:

```markdown
## Dependencies

This project uses [StoryTree](https://github.com/Mharbulous/StoryTree) as a git submodule.

### Cloning This Repo

```bash
git clone --recurse-submodules https://github.com/Mharbulous/SyncoPaid.git
```

### Updating StoryTree

```bash
cd .StoryTree
git pull origin main
cd ..
git add .StoryTree
git commit -m "chore: update StoryTree submodule"
```
```

---

## Phase 7: Documentation & Future Projects

### 7.1 Update StoryTree README

Ensure README.md includes:

- [x] Installation instructions (submodule approach)
- [x] Usage guide for new projects
- [x] Component overview
- [x] Xstory GUI documentation
- [x] Troubleshooting section

### 7.2 Standard Process for New Projects

```bash
# 1. Add StoryTree as submodule (hidden directory)
cd /path/to/new-project
git submodule add https://github.com/Mharbulous/StoryTree.git .StoryTree

# 2. Create relative symlinks (use Python script from Phase 2.6)
python create_symlinks.py

# 3. Initialize database
cp .StoryTree/templates/story-tree.db.empty .claude/data/story-tree.db

# 4. Copy workflows to .github/
cp -r .StoryTree/github/workflows/* .github/workflows/
cp -r .StoryTree/github/actions/* .github/actions/

# 5. Verify
ls -la .claude/skills/  # Should show symlinks
```

### 7.3 Add GitHub Topics

```bash
cd C:\Users\Brahm\Git\StoryTree
gh repo edit --add-topic claude-code
gh repo edit --add-topic story-driven-development
gh repo edit --add-topic developer-tools
```

---

## Rollback Procedures

### If Submodule Integration Fails

```bash
cd C:\Users\Brahm\Git\SyncoPaid
# Remove submodule
git submodule deinit -f .StoryTree
git rm -f .StoryTree
rm -rf .git/modules/.StoryTree

# Restore backup
rm -rf .claude
cp -r .claude.backup-YYYYMMDD .claude
```

### If Story-Tree.db is Corrupted

1. Check for backups in `.claude/data/`
2. Use Xstory GUI to diagnose issues
3. Last resort: Initialize fresh DB (loses story data)

---

## Checklist Summary

### Phase 1: Validate Repository
- [x] Verify all components present
- [x] Count: 10 skills, 10 commands, 5 scripts, 8 workflows

### Phase 2: Test in Isolated Branch
- [x] Create test branch in SyncoPaid
- [x] Backup .claude folder
- [x] Add StoryTree as git submodule
- [x] Remove old StoryTree-managed components
- [x] Create relative symlinks
- [x] Test local functionality

### Phase 3: Validate CI
- [x] Commit and push test branch
- [x] Verify CI workflows pass with submodule
- [x] Update checkout action if needed (`submodules: recursive`)
- [x] **Made StoryTree repository PUBLIC** (required for CI access)

### Phase 4: Merge and Switch Over
- [x] Merge test branch to main (PR #407)
- [x] Verify main branch CI passes
- [x] Keep backup available (`.claude.backup-20241224`)
- [ ] Monitor for issues

### Phase 5: Set Up Listbot
- [x] Add StoryTree as submodule
- [x] Create relative symlinks (29 symlinks)
- [x] Initialize database (preserved existing 34 story nodes)
- [x] Verify installation

### Phase 6: Cleanup SyncoPaid
- [ ] Confirm CI stable for several days
- [ ] Remove backup
- [ ] Remove legacy files
- [ ] Update CLAUDE.md

### Phase 7: Documentation
- [x] Update StoryTree README
- [x] Document standard installation process
- [x] Add GitHub topics (claude-code, story-driven-development, developer-tools)

---

## Notes

- **Relative Symlinks**: All symlinks use relative paths (`../../.StoryTree/claude/...`) so they work on any machine after cloning with submodules.
- **Symlink Bidirectionality**: Edits made through symlinked files modify StoryTree directly. This is intentional (improvements propagate everywhere) but requires awareness. Use `git diff` in StoryTree to review changes before committing.
- **Git Submodule**: Always clone with `--recurse-submodules` or run `git submodule update --init` after cloning.
- **GitHub Workflows**: Must be copied to `.github/workflows/` (GitHub doesn't follow symlinks).
- **story-tree.db**: Project-specific data, never symlinked.
- **Windows Developer Mode**: Required for creating symlinks on Windows.
