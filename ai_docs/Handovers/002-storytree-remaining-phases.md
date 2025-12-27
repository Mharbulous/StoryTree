# Handover: StoryTree Remaining Phases (6 & 7)

## Context

StoryTree submodule transition complete for both SyncoPaid (PR #407) and Listbot. Both projects now use StoryTree as a git submodule with relative symlinks.

**Critical:** StoryTree repo was made PUBLIC to allow GitHub Actions to clone the submodule.

## Completed

### Phase 5: Set Up Listbot ✓ (2024-12-24)
- Added StoryTree as git submodule
- Removed old embedded story-tree skill folder
- Created 29 relative symlinks (10 skills, 10 commands, 5 scripts, 4 data scripts)
- Preserved existing database (34 story nodes)
- Commit: `0cf0afd5`

## Remaining Work

### Phase 6: Cleanup SyncoPaid (after several days stable)
- Remove `.claude.backup-20241224`
- Remove `xstory/` if exists
- Update CLAUDE.md with submodule usage docs

## Key Files

| File | Purpose |
|------|---------|
| `StoryTree/TRANSITION_PLAN.md` | Master checklist with detailed steps |
| `StoryTree/ai_docs/Handovers/001-storytree-submodule-transition.md` | Completed phases, failed approaches, technical details |
| `SyncoPaid/.gitmodules` | Submodule config |

## Technical Notes

**Windows symlinks:** After `git pull`, symlinks appear as text files (Git fallback when `core.symlinks=false`). Must recreate with Python `os.symlink()`. Requires Windows Developer Mode enabled.

**CI:** All workflows need `submodules: recursive` in checkout action. Already done for SyncoPaid's 8 story workflows.

## Red Herrings

- `StoryTree/src/setup.py` - Only for `init-db`, not installation
- Old embedded `StoryTree/` files in SyncoPaid - Replaced by submodule, gone now

## Failed Approaches (don't repeat)

1. MINGW `ln -s` copies files instead of symlinks on Windows
2. Absolute symlinks break on other machines/CI
3. Private submodule repo - CI gets "Repository not found"
