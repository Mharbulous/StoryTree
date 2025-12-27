#!/usr/bin/env python3
"""
Xstory Setup Script

Installs xstory components into a target project directory.

Local development mode (default):
  - Creates symlinks for skills, commands, scripts (live updates)
  - Copies workflows and actions (GitHub requirement)

CI mode (--ci or CI=true environment):
  - Copies all files (no symlinks)

Usage:
  python setup.py install --target /path/to/project
  python setup.py install --target /path/to/project --ci
  python setup.py sync-workflows --target /path/to/project
  python setup.py init-db --target /path/to/project

Dependent Management:
  python setup.py register --target /path/to/project [--name ProjectName]
  python setup.py unregister --target /path/to/project
  python setup.py list-dependents
  python setup.py update-all
"""

import argparse
import json
import os
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path


def is_ci_mode(force_ci: bool = False) -> bool:
    """Detect if running in CI environment."""
    if force_ci:
        return True
    if os.environ.get('CI', '').lower() == 'true':
        return True
    if platform.system() == 'Linux' and not os.environ.get('FORCE_SYMLINKS'):
        # Default to copy mode on Linux (common CI environment)
        # Set FORCE_SYMLINKS=1 to use symlinks on Linux
        return True
    return False


def get_xstory_root() -> Path:
    """Get the root directory of the xstory installation."""
    return Path(__file__).parent.resolve()


def get_dependents_file() -> Path:
    """Get the path to the dependents registry file."""
    return get_xstory_root() / 'dependents.json'


def load_dependents() -> list[dict]:
    """Load the list of registered dependent projects."""
    dependents_file = get_dependents_file()
    if dependents_file.exists():
        with open(dependents_file) as f:
            return json.load(f)
    return []


def save_dependents(dependents: list[dict]) -> None:
    """Save the list of registered dependent projects."""
    dependents_file = get_dependents_file()
    with open(dependents_file, 'w') as f:
        json.dump(dependents, f, indent=2)
    print(f"Saved to: {dependents_file}")


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists, creating it if necessary."""
    path.mkdir(parents=True, exist_ok=True)


def configure_git_for_symlinks(target: Path) -> bool:
    """Configure git in target repo to support symlinks.

    Returns True if configuration was changed, False if already correct.
    """
    # Check if target is a git repo
    git_dir = target / '.git'
    if not git_dir.exists():
        print("\nNote: Target is not a git repository, skipping git configuration.")
        return False

    # Check current symlinks setting
    try:
        result = subprocess.run(
            ['git', '-C', str(target), 'config', '--local', '--get', 'core.symlinks'],
            capture_output=True, text=True
        )
        current_value = result.stdout.strip().lower()
    except FileNotFoundError:
        print("\nWarning: git not found in PATH, skipping git configuration.")
        return False

    if current_value == 'true':
        return False  # Already configured correctly

    # Enable symlinks
    try:
        subprocess.run(
            ['git', '-C', str(target), 'config', '--local', 'core.symlinks', 'true'],
            check=True, capture_output=True
        )
        print("  Set core.symlinks = true")

        return True
    except subprocess.CalledProcessError as e:
        print(f"  Warning: Failed to configure git: {e}")
        return False


def configure_submodule_recurse(target: Path) -> bool:
    """Configure git to automatically update submodules on pull/checkout.

    Returns True if configuration was changed, False if already correct.
    """
    git_dir = target / '.git'
    if not git_dir.exists():
        return False

    try:
        result = subprocess.run(
            ['git', '-C', str(target), 'config', '--local', '--get', 'submodule.recurse'],
            capture_output=True, text=True
        )
        current_value = result.stdout.strip().lower()
    except FileNotFoundError:
        return False

    if current_value == 'true':
        return False

    try:
        subprocess.run(
            ['git', '-C', str(target), 'config', '--local', 'submodule.recurse', 'true'],
            check=True, capture_output=True
        )
        print("  Set submodule.recurse = true (git pull will auto-update submodules)")
        return True
    except subprocess.CalledProcessError:
        return False


def check_windows_symlink_support() -> bool:
    """Check if Windows can create symlinks (Developer Mode enabled).

    Returns True if symlinks are supported, False otherwise.
    """
    if platform.system() != 'Windows':
        return True

    # Try to create a test symlink in temp directory
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            test_target = Path(tmpdir) / 'test_target'
            test_link = Path(tmpdir) / 'test_link'
            test_target.mkdir()
            os.symlink(test_target, test_link, target_is_directory=True)
            return True
    except OSError:
        return False


def check_source_directories(xstory_root: Path) -> bool:
    """Verify that StoryTree source directories exist.

    Returns True if all required directories exist, False otherwise.
    """
    required_dirs = [
        xstory_root / 'claude' / 'skills',
        xstory_root / 'claude' / 'commands',
        xstory_root / 'claude' / 'scripts',
        xstory_root / 'claude' / 'data',
        xstory_root / 'github' / 'workflows',
        xstory_root / 'github' / 'actions',
    ]

    missing = [d for d in required_dirs if not d.exists()]

    if missing:
        print("\nError: StoryTree source directories not found:")
        for d in missing:
            print(f"  - {d}")
        print("\nThis usually means the submodule is not initialized.")
        print("Run: git submodule update --init --recursive")
        return False

    return True


def is_broken_symlink_file(path: Path) -> bool:
    """Check if a path is a text file containing a symlink target (broken symlink).

    When git clones with core.symlinks=false, symlinks become text files
    containing the relative path to the target.
    """
    if not path.exists():
        return False

    # Real symlinks show as symlinks
    if path.is_symlink():
        return False

    # Directories are not broken symlinks
    if path.is_dir():
        return False

    # Check if it's a small file containing a path-like string
    try:
        # Broken symlink files are typically < 200 bytes
        if path.stat().st_size > 200:
            return False

        content = path.read_text().strip()

        # Check if content looks like a relative path to StoryTree
        if '.StoryTree/' in content or '../' in content:
            return True

    except (OSError, UnicodeDecodeError):
        pass

    return False


def clean_broken_symlinks(target: Path) -> int:
    """Find and remove broken symlink files in target .claude directory.

    Returns the number of broken symlinks cleaned.
    """
    claude_dir = target / '.claude'
    if not claude_dir.exists():
        return 0

    cleaned = 0
    dirs_to_check = ['skills', 'commands', 'scripts', 'data']

    for subdir in dirs_to_check:
        check_dir = claude_dir / subdir
        if not check_dir.exists():
            continue

        for item in check_dir.iterdir():
            if is_broken_symlink_file(item):
                print(f"  Removing broken symlink: {item.name}")
                item.unlink()
                cleaned += 1

    return cleaned


def verify_symlinks(target: Path) -> tuple[int, int]:
    """Verify that created symlinks resolve to valid targets.

    Returns tuple of (valid_count, broken_count).
    """
    claude_dir = target / '.claude'
    if not claude_dir.exists():
        return (0, 0)

    valid = 0
    broken = 0
    dirs_to_check = ['skills', 'commands', 'scripts', 'data']

    for subdir in dirs_to_check:
        check_dir = claude_dir / subdir
        if not check_dir.exists():
            continue

        for item in check_dir.iterdir():
            if item.is_symlink():
                # Check if symlink target exists
                try:
                    if item.resolve().exists():
                        valid += 1
                    else:
                        print(f"  Warning: Broken symlink: {item} -> {os.readlink(item)}")
                        broken += 1
                except OSError:
                    broken += 1

    return (valid, broken)


def create_symlink(src: Path, dest: Path) -> None:
    """Create a symlink, removing existing file/link first."""
    if dest.exists() or dest.is_symlink():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()

    # On Windows, directory symlinks need special handling
    if platform.system() == 'Windows' and src.is_dir():
        os.symlink(src, dest, target_is_directory=True)
    else:
        os.symlink(src, dest)

    print(f"  Symlinked: {dest.name} -> {src}")


def copy_item(src: Path, dest: Path) -> None:
    """Copy a file or directory, removing existing first."""
    if dest.exists() or dest.is_symlink():
        if dest.is_dir() and not dest.is_symlink():
            shutil.rmtree(dest)
        else:
            dest.unlink()

    if src.is_dir():
        shutil.copytree(src, dest)
    else:
        shutil.copy2(src, dest)

    print(f"  Copied: {dest.name}")


def install_skills(xstory_root: Path, target: Path, use_symlinks: bool) -> None:
    """Install skills to target/.claude/skills/"""
    src_dir = xstory_root / 'claude' / 'skills'
    dest_dir = target / '.claude' / 'skills'
    ensure_directory(dest_dir)

    print("\nInstalling skills...")
    for skill in src_dir.iterdir():
        if skill.is_dir():
            dest = dest_dir / skill.name
            if use_symlinks:
                create_symlink(skill, dest)
            else:
                copy_item(skill, dest)


def install_commands(xstory_root: Path, target: Path, use_symlinks: bool) -> None:
    """Install commands to target/.claude/commands/"""
    src_dir = xstory_root / 'claude' / 'commands'
    dest_dir = target / '.claude' / 'commands'
    ensure_directory(dest_dir)

    print("\nInstalling commands...")
    for cmd in src_dir.iterdir():
        if cmd.is_file() and cmd.suffix == '.md':
            dest = dest_dir / cmd.name
            if use_symlinks:
                create_symlink(cmd, dest)
            else:
                copy_item(cmd, dest)


def install_scripts(xstory_root: Path, target: Path, use_symlinks: bool) -> None:
    """Install scripts to target/.claude/scripts/"""
    src_dir = xstory_root / 'claude' / 'scripts'
    dest_dir = target / '.claude' / 'scripts'
    ensure_directory(dest_dir)

    print("\nInstalling scripts...")
    for script in src_dir.iterdir():
        if script.is_file() and script.suffix == '.py':
            dest = dest_dir / script.name
            if use_symlinks:
                create_symlink(script, dest)
            else:
                copy_item(script, dest)


def install_data_scripts(xstory_root: Path, target: Path, use_symlinks: bool) -> None:
    """Install data scripts to target/.claude/data/"""
    src_dir = xstory_root / 'claude' / 'data'
    dest_dir = target / '.claude' / 'data'
    ensure_directory(dest_dir)

    print("\nInstalling data scripts...")
    for script in src_dir.iterdir():
        if script.is_file() and script.suffix == '.py':
            dest = dest_dir / script.name
            if use_symlinks:
                create_symlink(script, dest)
            else:
                copy_item(script, dest)


def install_workflows(xstory_root: Path, target: Path) -> None:
    """Install workflows to target/.github/workflows/ (always copy, never symlink)"""
    src_dir = xstory_root / 'github' / 'workflows'
    dest_dir = target / '.github' / 'workflows'
    ensure_directory(dest_dir)

    print("\nInstalling workflows (always copied, GitHub requirement)...")
    for wf in src_dir.iterdir():
        if wf.is_file() and wf.suffix in ('.yml', '.yaml'):
            copy_item(wf, dest_dir / wf.name)


def install_actions(xstory_root: Path, target: Path) -> None:
    """Install GitHub Actions to target/.github/actions/ (always copy)"""
    src_dir = xstory_root / 'github' / 'actions'
    dest_dir = target / '.github' / 'actions'
    ensure_directory(dest_dir)

    print("\nInstalling GitHub Actions...")
    for action in src_dir.iterdir():
        if action.is_dir():
            copy_item(action, dest_dir / action.name)


def init_database(xstory_root: Path, target: Path) -> None:
    """Initialize an empty story-tree.db in the target project."""
    template = xstory_root / 'templates' / 'story-tree.db.empty'
    dest = target / '.claude' / 'data' / 'story-tree.db'

    ensure_directory(dest.parent)

    if dest.exists():
        print(f"\nDatabase already exists: {dest}")
        response = input("Overwrite? [y/N]: ").strip().lower()
        if response != 'y':
            print("Skipping database initialization.")
            return

    if template.exists():
        shutil.copy2(template, dest)
        print(f"\nInitialized database from template: {dest}")
    else:
        # Create empty database with schema
        schema_file = xstory_root / 'claude' / 'skills' / 'story-tree' / 'references' / 'schema.sql'
        if schema_file.exists():
            conn = sqlite3.connect(dest)
            with open(schema_file) as f:
                conn.executescript(f.read())
            conn.close()
            print(f"\nInitialized database from schema: {dest}")
        else:
            print(f"\nError: No template or schema found to initialize database")
            sys.exit(1)


def cmd_install(args) -> None:
    """Install xstory components to target project."""
    xstory_root = get_xstory_root()
    target = Path(args.target).resolve()
    use_symlinks = not is_ci_mode(args.ci)

    print(f"StoryTree Installation")
    print(f"=" * 40)
    print(f"Source: {xstory_root}")
    print(f"Target: {target}")
    print(f"Mode: {'Copy (CI)' if not use_symlinks else 'Symlink (Local Dev)'}")

    # Pre-flight checks
    if not target.exists():
        print(f"\nError: Target directory does not exist: {target}")
        sys.exit(1)

    # Check source directories exist (submodule initialized)
    if not check_source_directories(xstory_root):
        sys.exit(1)

    # Windows-specific: Check Developer Mode before attempting symlinks
    if use_symlinks and not check_windows_symlink_support():
        print("\nError: Cannot create symlinks on Windows.")
        print("Please enable Developer Mode:")
        print("  Settings > Privacy & Security > For developers > Developer Mode: ON")
        print("\nAlternatively, run with --ci flag to copy files instead of symlinking.")
        sys.exit(1)

    # Configure git for symlinks before creating them
    if use_symlinks:
        print("\nConfiguring git...")
        symlinks_changed = configure_git_for_symlinks(target)
        recurse_changed = configure_submodule_recurse(target)
        if not symlinks_changed and not recurse_changed:
            print("  Git already configured correctly")

    # Clean up broken symlinks (text files from previous clone with core.symlinks=false)
    if use_symlinks:
        cleaned = clean_broken_symlinks(target)
        if cleaned > 0:
            print(f"\nCleaned {cleaned} broken symlink(s) from previous installation")

    # Install components
    install_skills(xstory_root, target, use_symlinks)
    install_commands(xstory_root, target, use_symlinks)
    install_scripts(xstory_root, target, use_symlinks)
    install_data_scripts(xstory_root, target, use_symlinks)
    install_workflows(xstory_root, target)
    install_actions(xstory_root, target)

    if args.init_db:
        init_database(xstory_root, target)

    # Verify symlinks if applicable
    if use_symlinks:
        print("\nVerifying installation...")
        valid, broken = verify_symlinks(target)
        if broken > 0:
            print(f"  Warning: {broken} broken symlink(s) detected")
        else:
            print(f"  All {valid} symlink(s) verified successfully")

    print(f"\n{'=' * 40}")
    print("Installation complete!")

    if use_symlinks:
        print("\nSymlinks created. Changes to StoryTree will reflect immediately.")
    else:
        print("\nFiles copied. Run 'setup.py sync-workflows' after StoryTree updates.")


def cmd_sync_workflows(args) -> None:
    """Sync workflows from xstory to target (for after xstory updates)."""
    xstory_root = get_xstory_root()
    target = Path(args.target).resolve()

    print(f"Syncing workflows to {target}")
    install_workflows(xstory_root, target)
    install_actions(xstory_root, target)
    print("Workflow sync complete!")


def cmd_init_db(args) -> None:
    """Initialize story-tree.db in target project."""
    xstory_root = get_xstory_root()
    target = Path(args.target).resolve()
    init_database(xstory_root, target)


def diagnose_git_config(target: Path) -> dict:
    """Check git configuration status.

    Returns dict with 'symlinks' and 'recurse' keys, each containing:
    - 'status': 'ok', 'warning', or 'error'
    - 'value': current value or None
    - 'message': description
    """
    results = {}
    git_dir = target / '.git'

    if not git_dir.exists():
        return {
            'symlinks': {'status': 'error', 'value': None, 'message': 'Not a git repository'},
            'recurse': {'status': 'error', 'value': None, 'message': 'Not a git repository'}
        }

    # Check core.symlinks
    try:
        result = subprocess.run(
            ['git', '-C', str(target), 'config', '--local', '--get', 'core.symlinks'],
            capture_output=True, text=True
        )
        value = result.stdout.strip().lower()
        if value == 'true':
            results['symlinks'] = {'status': 'ok', 'value': 'true', 'message': 'Symlinks enabled'}
        elif value == 'false':
            results['symlinks'] = {'status': 'error', 'value': 'false', 'message': 'Symlinks disabled - will create text files instead'}
        else:
            results['symlinks'] = {'status': 'warning', 'value': None, 'message': 'Not set (inherits from global/system)'}
    except FileNotFoundError:
        results['symlinks'] = {'status': 'error', 'value': None, 'message': 'git not found'}

    # Check submodule.recurse
    try:
        result = subprocess.run(
            ['git', '-C', str(target), 'config', '--local', '--get', 'submodule.recurse'],
            capture_output=True, text=True
        )
        value = result.stdout.strip().lower()
        if value == 'true':
            results['recurse'] = {'status': 'ok', 'value': 'true', 'message': 'Auto-update enabled'}
        else:
            results['recurse'] = {'status': 'warning', 'value': value or None, 'message': 'Not set - manual submodule updates required'}
    except FileNotFoundError:
        results['recurse'] = {'status': 'error', 'value': None, 'message': 'git not found'}

    return results


def diagnose_symlinks_detailed(target: Path, xstory_root: Path) -> dict:
    """Analyze symlink health in detail.

    Returns dict with category keys (skills, commands, scripts, data), each containing:
    - 'valid': list of valid symlink names
    - 'broken': list of broken symlink names (symlink exists but target missing)
    - 'text_files': list of text files pretending to be symlinks
    - 'missing': list of expected items not present
    - 'extra': list of non-symlink items (local files/dirs)
    """
    claude_dir = target / '.claude'
    results = {}

    categories = {
        'skills': (xstory_root / 'claude' / 'skills', lambda p: p.is_dir()),
        'commands': (xstory_root / 'claude' / 'commands', lambda p: p.is_file() and p.suffix == '.md'),
        'scripts': (xstory_root / 'claude' / 'scripts', lambda p: p.is_file() and p.suffix == '.py'),
        'data': (xstory_root / 'claude' / 'data', lambda p: p.is_file() and p.suffix == '.py'),
    }

    for category, (src_dir, filter_fn) in categories.items():
        results[category] = {
            'valid': [],
            'broken': [],
            'text_files': [],
            'missing': [],
            'extra': []
        }

        dest_dir = claude_dir / category
        if not dest_dir.exists():
            # All expected items are missing
            if src_dir.exists():
                expected = [item.name for item in src_dir.iterdir() if filter_fn(item)]
                results[category]['missing'] = expected
            continue

        # Get expected items from source
        expected_names = set()
        if src_dir.exists():
            expected_names = {item.name for item in src_dir.iterdir() if filter_fn(item)}

        # Check each item in destination
        for item in dest_dir.iterdir():
            name = item.name

            if item.is_symlink():
                # Check if symlink target exists
                try:
                    if item.resolve().exists():
                        results[category]['valid'].append(name)
                    else:
                        results[category]['broken'].append(name)
                except OSError:
                    results[category]['broken'].append(name)
            elif is_broken_symlink_file(item):
                results[category]['text_files'].append(name)
            elif name in expected_names:
                # It's a regular file/dir where we expect a symlink
                results[category]['extra'].append(name)

        # Find missing items
        present_names = set(results[category]['valid'] + results[category]['broken'] +
                          results[category]['text_files'] + results[category]['extra'])
        results[category]['missing'] = list(expected_names - present_names)

    return results


def cmd_diagnose(args) -> None:
    """Diagnose StoryTree installation health in a target project."""
    xstory_root = get_xstory_root()
    target = Path(args.target).resolve()

    # Use ASCII-safe symbols for Windows compatibility
    SYM_OK = '[OK]'
    SYM_WARN = '[!!]'
    SYM_ERR = '[X]'
    SYM_INFO = '[-]'

    print("StoryTree Health Check")
    print("=" * 50)
    print(f"Target: {target}")
    print()

    issues_found = 0

    # Check if target exists
    if not target.exists():
        print(f"Error: Target directory does not exist")
        sys.exit(1)

    # Check submodule
    print("Submodule:")
    submodule_path = target / '.StoryTree'
    if submodule_path.exists():
        # Check if it has content
        if (submodule_path / 'claude').exists():
            print(f"  {SYM_OK} .StoryTree submodule present and initialized")
        else:
            print(f"  {SYM_ERR} .StoryTree submodule present but NOT initialized")
            print("    Run: git submodule update --init --recursive")
            issues_found += 1
    else:
        print(f"  {SYM_INFO} .StoryTree submodule not present (using external StoryTree)")
    print()

    # Check git configuration
    print("Git Configuration:")
    git_config = diagnose_git_config(target)

    for setting, info in git_config.items():
        if info['status'] == 'ok':
            symbol = SYM_OK
        elif info['status'] == 'warning':
            symbol = SYM_WARN
        else:
            symbol = SYM_ERR
        setting_name = 'core.symlinks' if setting == 'symlinks' else 'submodule.recurse'
        value_str = f" = {info['value']}" if info['value'] else ""
        print(f"  {symbol} {setting_name}{value_str}")
        if info['status'] != 'ok':
            print(f"    {info['message']}")
            if info['status'] == 'error':
                issues_found += 1
    print()

    # Check Windows symlink support
    if platform.system() == 'Windows':
        print("Windows Symlink Support:")
        if check_windows_symlink_support():
            print(f"  {SYM_OK} Developer Mode enabled (symlinks work)")
        else:
            print(f"  {SYM_ERR} Developer Mode NOT enabled")
            print("    Enable at: Settings > Privacy & Security > For developers")
            issues_found += 1
        print()

    # Check symlinks
    print("Symlinks:")
    symlink_results = diagnose_symlinks_detailed(target, xstory_root)

    for category, info in symlink_results.items():
        valid_count = len(info['valid'])
        broken_count = len(info['broken'])
        text_count = len(info['text_files'])
        missing_count = len(info['missing'])
        extra_count = len(info['extra'])

        total_expected = valid_count + broken_count + text_count + missing_count
        problem_count = broken_count + text_count + missing_count

        if problem_count == 0 and valid_count > 0:
            print(f"  {SYM_OK} {category}: {valid_count} valid")
            if extra_count > 0:
                print(f"    + {extra_count} local file(s): {', '.join(info['extra'][:3])}{'...' if extra_count > 3 else ''}")
        elif valid_count == 0 and total_expected == 0:
            print(f"  {SYM_INFO} {category}: not installed")
        else:
            symbol = SYM_ERR if problem_count > 0 else SYM_OK
            print(f"  {symbol} {category}: {valid_count} valid, {problem_count} issue(s)")
            if broken_count > 0:
                print(f"    Broken: {', '.join(info['broken'])}")
                issues_found += broken_count
            if text_count > 0:
                print(f"    Text files (fake symlinks): {', '.join(info['text_files'])}")
                issues_found += text_count
            if missing_count > 0:
                print(f"    Missing: {', '.join(info['missing'][:5])}{'...' if missing_count > 5 else ''}")
                issues_found += missing_count
    print()

    # Check database
    print("Database:")
    db_path = target / '.claude' / 'data' / 'story-tree.db'
    if db_path.exists():
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM story_nodes")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"  {SYM_OK} story-tree.db exists ({count} stories)")
        except Exception as e:
            print(f"  {SYM_WARN} story-tree.db exists but may be corrupted: {e}")
    else:
        print(f"  {SYM_INFO} story-tree.db not initialized")
        print("    Run: setup.py init-db --target ...")
    print()

    # Summary
    print("=" * 50)
    if issues_found == 0:
        print(f"{SYM_OK} All checks passed - installation is healthy")
    else:
        print(f"{SYM_ERR} Found {issues_found} issue(s)")
        print()
        print("To fix, run:")
        print(f"  python setup.py install --target \"{target}\"")


def cmd_register(args) -> None:
    """Register a project as a StoryTree dependent."""
    target = Path(args.target).resolve()

    if not target.exists():
        print(f"Error: Directory does not exist: {target}")
        sys.exit(1)

    # Check if .StoryTree submodule exists
    submodule_path = target / '.StoryTree'
    if not submodule_path.exists():
        print(f"Warning: No .StoryTree submodule found in {target}")
        print("Consider running: git submodule add https://github.com/Mharbulous/StoryTree.git .StoryTree")

    dependents = load_dependents()

    # Check if already registered
    for dep in dependents:
        if dep['path'] == str(target):
            print(f"Already registered: {target}")
            return

    # Add new dependent
    name = args.name or target.name
    dependents.append({
        'name': name,
        'path': str(target)
    })

    save_dependents(dependents)
    print(f"Registered: {name} ({target})")


def cmd_unregister(args) -> None:
    """Unregister a project from StoryTree dependents."""
    target = Path(args.target).resolve()
    dependents = load_dependents()

    original_count = len(dependents)
    dependents = [d for d in dependents if d['path'] != str(target)]

    if len(dependents) == original_count:
        print(f"Not found in registry: {target}")
        return

    save_dependents(dependents)
    print(f"Unregistered: {target}")


def cmd_list_dependents(args) -> None:
    """List all registered dependent projects."""
    dependents = load_dependents()

    if not dependents:
        print("No dependent projects registered.")
        print("\nRegister a project with:")
        print("  python setup.py register --target /path/to/project")
        return

    print(f"Registered StoryTree dependents ({len(dependents)}):")
    print("-" * 50)
    for dep in dependents:
        path = Path(dep['path'])
        exists = path.exists()
        status = "" if exists else " [NOT FOUND]"
        print(f"  {dep['name']}: {dep['path']}{status}")


def cmd_update_all(args) -> None:
    """Sync workflows to all registered dependent projects."""
    xstory_root = get_xstory_root()
    dependents = load_dependents()

    if not dependents:
        print("No dependent projects registered.")
        print("\nRegister a project with:")
        print("  python setup.py register --target /path/to/project")
        return

    print(f"Updating workflows for {len(dependents)} project(s)...")
    print("=" * 50)

    success_count = 0
    for dep in dependents:
        target = Path(dep['path'])
        print(f"\n[{dep['name']}] {target}")

        if not target.exists():
            print("  SKIPPED: Directory not found")
            continue

        try:
            install_workflows(xstory_root, target)
            install_actions(xstory_root, target)
            success_count += 1
            print("  OK: Workflows synced")
        except Exception as e:
            print(f"  ERROR: {e}")

    print("\n" + "=" * 50)
    print(f"Updated {success_count}/{len(dependents)} projects")

    if success_count > 0:
        print("\nNext steps:")
        print("  1. Review changes in each project: git diff .github/")
        print("  2. Commit and push: git add .github/ && git commit -m 'chore: sync StoryTree workflows'")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Xstory setup and installation tool',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # install command
    install_parser = subparsers.add_parser('install', help='Install xstory to target project')
    install_parser.add_argument('--target', '-t', required=True, help='Target project directory')
    install_parser.add_argument('--ci', action='store_true', help='Force CI mode (copy instead of symlink)')
    install_parser.add_argument('--init-db', action='store_true', help='Initialize empty story-tree.db')
    install_parser.set_defaults(func=cmd_install)

    # sync-workflows command
    sync_parser = subparsers.add_parser('sync-workflows', help='Sync workflows to target (after xstory updates)')
    sync_parser.add_argument('--target', '-t', required=True, help='Target project directory')
    sync_parser.set_defaults(func=cmd_sync_workflows)

    # init-db command
    db_parser = subparsers.add_parser('init-db', help='Initialize story-tree.db in target project')
    db_parser.add_argument('--target', '-t', required=True, help='Target project directory')
    db_parser.set_defaults(func=cmd_init_db)

    # diagnose command
    diagnose_parser = subparsers.add_parser('diagnose', help='Check StoryTree installation health')
    diagnose_parser.add_argument('--target', '-t', required=True, help='Target project directory')
    diagnose_parser.set_defaults(func=cmd_diagnose)

    # register command
    register_parser = subparsers.add_parser('register', help='Register a project as a StoryTree dependent')
    register_parser.add_argument('--target', '-t', required=True, help='Project directory to register')
    register_parser.add_argument('--name', '-n', help='Friendly name for the project (defaults to directory name)')
    register_parser.set_defaults(func=cmd_register)

    # unregister command
    unregister_parser = subparsers.add_parser('unregister', help='Unregister a project from StoryTree dependents')
    unregister_parser.add_argument('--target', '-t', required=True, help='Project directory to unregister')
    unregister_parser.set_defaults(func=cmd_unregister)

    # list-dependents command
    list_parser = subparsers.add_parser('list-dependents', help='List all registered dependent projects')
    list_parser.set_defaults(func=cmd_list_dependents)

    # update-all command
    update_parser = subparsers.add_parser('update-all', help='Sync workflows to all registered dependents')
    update_parser.set_defaults(func=cmd_update_all)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
