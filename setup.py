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
import sys
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

    print(f"Xstory Installation")
    print(f"=" * 40)
    print(f"Source: {xstory_root}")
    print(f"Target: {target}")
    print(f"Mode: {'Copy (CI)' if not use_symlinks else 'Symlink (Local Dev)'}")

    if not target.exists():
        print(f"\nError: Target directory does not exist: {target}")
        sys.exit(1)

    install_skills(xstory_root, target, use_symlinks)
    install_commands(xstory_root, target, use_symlinks)
    install_scripts(xstory_root, target, use_symlinks)
    install_data_scripts(xstory_root, target, use_symlinks)
    install_workflows(xstory_root, target)
    install_actions(xstory_root, target)

    if args.init_db:
        init_database(xstory_root, target)

    print(f"\n{'=' * 40}")
    print("Installation complete!")

    if use_symlinks:
        print("\nSymlinks created. Changes to xstory will reflect immediately.")
    else:
        print("\nFiles copied. Run 'setup.py sync-workflows' after xstory updates.")


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
