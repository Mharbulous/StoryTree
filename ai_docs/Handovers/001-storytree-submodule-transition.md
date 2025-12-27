# Handover: StoryTree Submodule Transition

## ✅ TRANSITION COMPLETE

**Status:** Merged to main via PR #407 on 2024-12-24

**What was done:**
- StoryTree added as git submodule in SyncoPaid (replaces embedded copy)
- Relative symlinks created for all skills, commands, scripts, data scripts
- All 8 story workflows updated with `submodules: recursive` in checkout action
- **StoryTree repository made PUBLIC** (required for CI to clone submodule)
- CI validation passed on test branch (Build Story workflow)
- Merged via PR #407 to main
- Backup preserved: `.claude.backup-20241224`

**Post-merge local setup:** After `git pull`, symlinks appear as text files on Windows (Git's fallback). Recreate with Python (see Technical Details below).

---

## Key Files

| File | Purpose |
|------|---------|
| `StoryTree/TRANSITION_PLAN.md` | Master doc - updated with submodule approach, has checklist |
| `SyncoPaid/.gitmodules` | Submodule config pointing to StoryTree |
| `SyncoPaid/.github/workflows/*.yml` | 8 story workflows, all have `submodules: recursive` |

---

## Failed Approaches (Don't Repeat)

1. **MINGW `ln -s`** - Copies files instead of creating symlinks on Windows. Use Python `os.symlink()` instead.

2. **Absolute symlinks** - Work locally but break on other machines/CI. Use relative paths via `os.path.relpath()`.

3. **src/setup.py installer** - Originally planned, but git submodule is cleaner. The src/setup.py still exists for `init-db` but isn't needed for installation.

4. **Private submodule repo** - CI failed with "Repository not found" because GitHub Actions' GITHUB_TOKEN can't access private repos outside the current repo. **Solution:** Made StoryTree public.

---

## Technical Details

**Creating symlinks on Windows:**
```python
import os
from pathlib import Path
src = Path('StoryTree/.claude/skills/story-tree')
dst = Path('.claude/skills/story-tree')
rel_path = os.path.relpath(src, dst.parent)  # ../../StoryTree/.claude/skills/story-tree
os.symlink(rel_path, dst, target_is_directory=True)
```

**Requires:** Windows Developer Mode enabled (Settings → Privacy & Security → For developers)

**Verify symlinks (Windows):**
```cmd
dir /AL .claude\skills
# Shows: <SYMLINKD> story-tree [..\..\StoryTree\.claude\skills\story-tree]
```

---

## Component Counts

- Skills: 10 (story-writing merged into story-building)
- Commands: 10
- Scripts: 5
- Workflows: 8

---

## Red Herrings

- `StoryTree/src/setup.py` - Still exists but only needed for `init-db`, not for installation
- Old `StoryTree/` directory in SyncoPaid - Was tracked as regular files, now deleted and replaced with submodule
- `xstory/` directory - May exist in old SyncoPaid, can be deleted in Phase 6

---

## Commands Reference

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/Mharbulous/SyncoPaid.git

# After git pull, initialize submodule if needed
git submodule update --init --recursive

# Update submodule after StoryTree changes
cd StoryTree && git pull && cd .. && git add StoryTree && git commit -m "update StoryTree"

# Recreate Windows symlinks after pull (run from SyncoPaid root)
python -c "
import os
from pathlib import Path
os.chdir('.')

skills = ['code-sentinel', 'concept-vetting', 'goal-synthesis', 'prioritize-story-nodes',
          'story-arborist', 'story-building', 'story-execution',
          'story-planning', 'story-tree', 'story-verification']
for skill in skills:
    src = Path(f'StoryTree/.claude/skills/{skill}')
    dst = Path(f'.claude/skills/{skill}')
    if dst.exists(): os.remove(dst)
    os.symlink(os.path.relpath(src, dst.parent), dst, target_is_directory=True)
    print(f'Symlink: {dst}')
"
```

---

## Remaining Tasks

### Phase 5: Set Up Listbot
- [ ] Add StoryTree as submodule in Listbot
- [ ] Create relative symlinks
- [ ] Initialize database

### Phase 6: Cleanup SyncoPaid (after stable for several days)
- [ ] Remove `.claude.backup-20241224`
- [ ] Remove legacy `xstory/` directory if exists
- [ ] Update CLAUDE.md with submodule usage
