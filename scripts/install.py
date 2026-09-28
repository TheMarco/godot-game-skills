#!/usr/bin/env python3
"""Install selected self-contained skills. Existing skills are preserved by default."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
IGNORED = shutil.ignore_patterns(".godot", "__pycache__", "*.pyc", ".DS_Store", "artifacts")


def available(source: Path = ROOT / "skills") -> dict[str, Path]:
    return {p.name: p for p in sorted(source.iterdir()) if p.is_dir() and (p / "SKILL.md").is_file()}


def destination(agent: str) -> Path:
    if agent == "claude":
        return Path.home() / ".claude" / "skills"
    codex_home = os.environ.get("CODEX_HOME")
    return Path(codex_home).expanduser() / "skills" if codex_home else Path.home() / ".codex" / "skills"


def install(skills: dict[str, Path], dest: Path, force=False, dry_run=False) -> list[str]:
    dest = dest.expanduser().absolute()
    actions = []
    for name, source in skills.items():
        target = dest / name
        # Avoid copying a source into itself or following target symlinks.
        if target.resolve() == source.resolve() or source.resolve() in dest.resolve().parents:
            raise ValueError("Destination must not be inside a source skill")
        if target.is_symlink():
            raise ValueError(f"Refusing symlink target: {target}")
        if target.exists() and not force:
            actions.append(f"SKIP {name}: already exists (use --force to back up and replace)")
            continue
        if dry_run:
            actions.append(f"WOULD INSTALL {name} -> {target}")
            continue
        dest.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{name}-", dir=dest))
        backup = None
        try:
            shutil.copytree(source, staging / name, ignore=IGNORED)
            if target.exists():
                backups = dest / ".godot-game-skills-backups"
                backups.mkdir(exist_ok=True)
                stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
                backup = backups / f"{name}-{stamp}"
                target.rename(backup)
            try:
                (staging / name).rename(target)
            except OSError:
                if backup and not target.exists():
                    backup.rename(target)
                raise
            actions.append(f"INSTALLED {name} -> {target}" + (f" (backup: {backup})" if backup else ""))
        finally:
            shutil.rmtree(staging)
    return actions


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--agent", choices=("codex", "claude"))
    group.add_argument("--dest", type=Path, help="Explicit skills directory for any compatible agent")
    parser.add_argument("--skill", action="append", default=[], help="Repeat to select; default all")
    parser.add_argument("--force", action="store_true", help="Back up existing selected skills before replacing")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        all_skills = available()
        unknown = set(args.skill) - set(all_skills)
        if unknown:
            raise ValueError(f"Unknown skills: {', '.join(sorted(unknown))}")
        selected = {name: path for name, path in all_skills.items() if not args.skill or name in args.skill}
        dest = args.dest if args.dest is not None else destination(args.agent)
        for action in install(selected, dest, args.force, args.dry_run):
            print(action)
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
