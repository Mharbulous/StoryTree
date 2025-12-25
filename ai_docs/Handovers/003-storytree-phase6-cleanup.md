# Handover: StoryTree Phase 6 & 7 - Cleanup and Documentation

## Status

**Phases 1-5 complete.** StoryTree is now a git submodule in both SyncoPaid and Listbot with relative symlinks.

## Remaining Work

### Phase 6: Cleanup SyncoPaid (wait several days for CI stability first)
- Remove `.claude.backup-20241224`
- Remove `xstory/` if exists
- Update CLAUDE.md with submodule usage docs

### Phase 7: Documentation
- Update StoryTree README with usage guide
- Document standard installation process for new projects
- Add GitHub topics via `gh repo edit --add-topic`

## Key Files

| File | Purpose |
|------|---------|
| `Listbot/StoryTree/TRANSITION_PLAN.md` | Master checklist - use this as source of truth |
| `Listbot/StoryTree/ai_docs/Handovers/002-storytree-remaining-phases.md` | Previous handover with Phase 5 completion details |

## Critical Insight: Submodule Workflow

**Always work through submodules, not the standalone repo.**

When editing StoryTree files:
1. Edit in submodule (e.g., `Listbot/StoryTree/`)
2. Push from submodule
3. Update parent repo's submodule pointer: `git add StoryTree && git commit`

The standalone `C:/Users/Brahm/Git/StoryTree/` repo exists but should be avoided - it causes confusion about which clone has the latest commits.

## Technical Notes

- **Windows symlinks:** Require Developer Mode. After fresh clone, symlinks may appear as text files - recreate with Python `os.symlink()`.
- **CI:** Workflows need `submodules: recursive` in checkout action.
- **StoryTree is PUBLIC** - required for GitHub Actions to clone the submodule.

## Not Relevant

- `StoryTree/setup.py` - Only for `init-db`, not installation
- Standalone `C:/Users/Brahm/Git/StoryTree/` - Use submodule instead
