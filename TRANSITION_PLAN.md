# StoryTree Transition Plan

## Overview

This document outlines the steps required to complete the transition of StoryTree components from the SyncoPaid repository into the standalone StoryTree repository, and how to set up StoryTree for use in other projects.

## Naming Convention

- **StoryTree**: The repository and overall project for story-driven development orchestration
- **Xstory** (eXploreStory): The Python GUI tool (PySide6) for visually exploring the story tree

---

## Critical Requirement: CI Continuity

**The existing StoryTree components in SyncoPaid must continue working throughout this transition.**

SyncoPaid has active CI workflows that depend on the current `.claude/` structure. These workflows must not break during the transition. This means:

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
├── setup.py             # Installer script
├── README.md            # Project documentation
├── claude/
│   ├── skills/          # 11 skills
│   ├── commands/        # 11 slash commands
│   ├── scripts/         # Helper scripts
│   └── data/            # DB initialization scripts
├── github/
│   ├── workflows/       # CI workflows
│   └── actions/         # Composite actions
├── gui/                 # Xstory GUI tool
└── templates/
    └── story-tree.db.empty
```

### 1.2 Test Setup Script

Run the installer in dry-run mode to verify it works:

```bash
cd C:\Users\Brahm\Git\StoryTree
python setup.py --help
python setup.py install --help
```

### 1.3 Add Missing Components

Check if any components are missing from the initial extraction:

| Component | Status | Notes |
|-----------|--------|-------|
| Skills (10) | Verify | Compare with SyncoPaid (story-writing merged into story-building) |
| Commands (10) | Verify | Compare with SyncoPaid |
| Scripts (5) | Verify | Compare with SyncoPaid |
| Workflows (8) | Verify | Compare with SyncoPaid |
| Xstory GUI | Present | In `gui/` folder |

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
| `.claude/skills/execute-story-workflow.md` | Legacy file |

### 2.4 Remove StoryTree-Managed Components (Test Branch Only)

Remove components that will be replaced by symlinks:

```bash
cd C:\Users\Brahm\Git\SyncoPaid\.claude

# Skills to remove (will be symlinked from StoryTree)
rm -rf skills/code-sentinel
rm -rf skills/goal-synthesis
rm -rf skills/prioritize-story-nodes
rm -rf skills/story-arborist
rm -rf skills/story-building
rm -rf skills/story-execution
rm -rf skills/story-planning
rm -rf skills/story-tree
rm -rf skills/story-verification
rm -rf skills/story-vetting

# Commands to remove (will be symlinked)
# List commands managed by StoryTree and remove them

# Scripts to remove (will be symlinked)
# List scripts managed by StoryTree and remove them
```

### 2.5 Run StoryTree Installer

```bash
cd C:\Users\Brahm\Git\StoryTree
python setup.py install --target C:\Users\Brahm\Git\SyncoPaid
```

**Important**: Do NOT use `--init-db` flag - SyncoPaid already has a story-tree.db with data.

### 2.6 Verify Local Installation

```bash
cd C:\Users\Brahm\Git\SyncoPaid\.claude\skills

# Check that symlinks point to StoryTree
ls -la story-tree
# Should show: story-tree -> C:\Users\Brahm\Git\StoryTree\claude\skills\story-tree
```

### 2.7 Test Local Functionality

1. Open Claude Code in SyncoPaid
2. Run `/story-tree` command
3. Verify skills are accessible
4. Run Xstory GUI: `python C:\Users\Brahm\Git\StoryTree\gui\xstory.py`

### 2.8 If Tests Fail: Rollback

```bash
cd C:\Users\Brahm\Git\SyncoPaid
git checkout main  # Return to working main branch
git branch -D test/storytree-integration  # Delete failed test branch
```

---

## Phase 3: Validate CI with New Setup

**Goal**: Ensure CI workflows pass with the StoryTree integration before merging.

### 3.1 Understand CI Symlink Limitation

**Important**: CI environments cannot use symlinks - they need actual files.

The StoryTree installer handles this automatically:
- Local dev: Creates symlinks
- CI (Linux or `CI=true`): Copies files instead

### 3.2 Prepare Branch for CI Testing

On the test branch, the installer should have copied (not symlinked) the workflows:

```bash
cd C:\Users\Brahm\Git\SyncoPaid
git status
# Should show modified/new files in .github/workflows/
```

### 3.3 Commit and Push Test Branch

```bash
git add .
git commit -m "test: integrate StoryTree from standalone repo"
git push -u origin test/storytree-integration
```

### 3.4 Run CI Workflows

1. Open GitHub Actions for SyncoPaid
2. Manually trigger the story-related workflows on `test/storytree-integration` branch
3. Verify all workflows pass

### 3.5 If CI Fails: Debug Without Affecting Main

- Fix issues on the test branch
- Re-run CI until all workflows pass
- Main branch remains unaffected throughout

### 3.6 CI Passes: Ready for Phase 4

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
- Keep `xstory/` directory until Phase 6 confirms stability

### 4.4 Monitor for Issues

- Run the system normally for a few days
- Watch for any CI failures
- Test local development workflow

### 4.5 If Issues Arise: Rollback

```bash
cd C:\Users\Brahm\Git\SyncoPaid
# Restore backup
rm -rf .claude
cp -r .claude.backup-YYYYMMDD .claude
git checkout -- .  # Discard uncommitted changes
```

---

## Phase 5: Set Up Listbot to Use StoryTree

**Prerequisite**: Phase 4 complete and stable for SyncoPaid.

### 5.1 Backup Current Listbot State

```bash
cd C:\Users\Brahm\Git\Listbot
cp -r .claude .claude.backup-$(date +%Y%m%d)
```

### 5.2 Identify Listbot-Specific Components

Preserve these Listbot-specific files:

| Path | Reason |
|------|--------|
| `.claude/data/story-tree.db` | Contains Listbot's story data |
| `.claude/settings.json` | Project settings |
| `.claude/settings.local.json` | Local settings |
| Any Listbot-specific skills | Project-specific |

### 5.3 Remove Conflicting Components

Remove any existing story-* skills/commands that will be replaced:

```bash
cd C:\Users\Brahm\Git\Listbot\.claude
# Remove story-related skills that StoryTree will provide
# (Check what exists first before removing)
```

### 5.4 Run StoryTree Installer

```bash
cd C:\Users\Brahm\Git\StoryTree
python setup.py install --target C:\Users\Brahm\Git\Listbot
```

**Note**: If Listbot doesn't have a story-tree.db yet, use `--init-db`:

```bash
python setup.py install --target C:\Users\Brahm\Git\Listbot --init-db
```

### 5.5 Verify Installation

Same verification steps as SyncoPaid (Phase 2.6-2.7).

---

## Phase 6: Cleanup SyncoPaid (Only After Stability Confirmed)

**Prerequisite**: CI has been stable for at least several days after Phase 4.

### 6.1 Remove Extracted xstory Directory

After confirming StoryTree works correctly:

```bash
cd C:\Users\Brahm\Git\SyncoPaid
rm -rf xstory/
```

### 6.2 Remove Backup

```bash
rm -rf .claude.backup-YYYYMMDD
```

### 6.3 Remove Redundant Files

Clean up files that are now managed by StoryTree:

```bash
# Remove legacy/archived story-related content
rm -rf .claude/archived-skills/  # If contains story-* skills
```

### 6.4 Update .gitignore

Add StoryTree symlinks to .gitignore if they shouldn't be tracked:

```gitignore
# StoryTree symlinks (managed by StoryTree installer)
.claude/skills/story-*
.claude/skills/code-sentinel
.claude/skills/goal-synthesis
.claude/skills/prioritize-story-nodes
.claude/commands/story-*.md
# etc.
```

### 6.5 Update CLAUDE.md

Add reference to StoryTree dependency in SyncoPaid's CLAUDE.md:

```markdown
## Dependencies

This project uses [StoryTree](https://github.com/Mharbulous/StoryTree) for story-driven development.
StoryTree components are installed via symlinks. To update:

```bash
cd C:\Users\Brahm\Git\StoryTree
git pull
python setup.py sync-workflows --target C:\Users\Brahm\Git\SyncoPaid
```
```

---

## Phase 7: Documentation & Future Projects

### 7.1 Update StoryTree README

Ensure README.md includes:

- [ ] Installation instructions
- [ ] Usage guide for new projects
- [ ] Component overview
- [ ] Xstory GUI documentation

### 7.2 Create Installation Guide for New Projects

Document the standard process for adding StoryTree to a new project:

```bash
# 1. Clone or ensure StoryTree is available locally
cd C:\Users\Brahm\Git
git clone https://github.com/Mharbulous/StoryTree.git

# 2. Install to target project
cd StoryTree
python setup.py install --target /path/to/new-project --init-db

# 3. Verify installation
cd /path/to/new-project
ls -la .claude/skills/
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

### If StoryTree Installation Fails

1. Remove symlinks created by installer
2. Restore from backup: `cp -r .claude.backup-YYYYMMDD .claude`

### If Story-Tree.db is Corrupted

1. Check for backups in `.claude/data/`
2. Use Xstory GUI to diagnose issues
3. Last resort: Initialize fresh DB (loses story data)

---

## Checklist Summary

### Phase 1: Validate Repository
- [ ] Verify all components present
- [ ] Test setup.py script
- [ ] Identify missing components

### Phase 2: Test in Isolated Branch
- [ ] Create test branch in SyncoPaid
- [ ] Backup .claude folder
- [ ] Remove StoryTree-managed components
- [ ] Run installer (without --init-db)
- [ ] Verify symlinks created
- [ ] Test local functionality

### Phase 3: Validate CI
- [ ] Commit and push test branch
- [ ] Run CI workflows on test branch
- [ ] All workflows pass

### Phase 4: Merge and Switch Over
- [ ] Merge test branch to main
- [ ] Verify main branch CI passes
- [ ] Keep backup available
- [ ] Monitor for issues

### Phase 5: Set Up Listbot
- [ ] Backup .claude folder
- [ ] Identify project-specific components
- [ ] Remove conflicting components
- [ ] Run installer
- [ ] Verify installation

### Phase 6: Cleanup SyncoPaid
- [ ] Confirm CI stable for several days
- [ ] Remove xstory/ directory
- [ ] Remove backup
- [ ] Remove redundant files
- [ ] Update .gitignore
- [ ] Update CLAUDE.md

### Phase 7: Documentation
- [ ] Update StoryTree README
- [ ] Create installation guide
- [ ] Add GitHub topics

---

## Notes

- **Symlinks vs Copies**: Local development uses symlinks so changes to StoryTree reflect immediately. CI uses copies.
- **Symlink Bidirectionality**: Edits made through symlinked files modify StoryTree directly. This is intentional (improvements propagate everywhere) but requires awareness. Use `git diff` in StoryTree to review changes before committing.
- **GitHub Workflows**: Always copied (not symlinked) per GitHub requirements.
- **story-tree.db**: Never overwritten by installer unless explicitly requested with `--init-db`.
