#!/usr/bin/env python3
"""Validate the package's deliberately simple skill metadata and local links."""
from __future__ import annotations

import ast
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
NAMES = {
    "godot-dev-director", "godot-game-verification", "godot-procedural-worlds",
    "godot-performance-workflows", "godot-3d-prop-integration", "godot-horror-pacing",
    "godot-analog-presentation", "godot-environment-wear",
}


def validate(root: Path = ROOT) -> list[str]:
    errors = []
    directories = {p.name: p for p in (root / "skills").iterdir() if p.is_dir()}
    if set(directories) != NAMES:
        errors.append(f"Skill inventory differs: missing={NAMES - set(directories)}, extra={set(directories) - NAMES}")
    for name, folder in directories.items():
        skill_file = folder / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{name}: missing SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        if not match:
            errors.append(f"{name}: missing frontmatter")
            continue
        # This package uses two unquoted, single-line string fields only.
        fields = {}
        for line in match[1].splitlines():
            key, separator, value = line.partition(": ")
            if not separator or key in fields:
                errors.append(f"{name}: unsupported or duplicate frontmatter: {line}")
            fields[key] = value
        if fields.get("name") != name or set(fields) != {"name", "description"}:
            errors.append(f"{name}: invalid name or fields")
        description = fields.get("description", "")
        if not description.strip() or len(description) > 1024 or ": " in description:
            errors.append(f"{name}: invalid one-line description")
        metadata = folder / "agents" / "openai.yaml"
        if not metadata.is_file():
            errors.append(f"{name}: missing agent metadata")
        else:
            values = {}
            for key, value in re.findall(r"^  (display_name|short_description|default_prompt): (.+)$", metadata.read_text(), re.M):
                try:
                    values[key] = json.loads(value)
                except ValueError:
                    errors.append(f"{name}: quote metadata string {key}")
            if set(values) != {"display_name", "short_description", "default_prompt"}:
                errors.append(f"{name}: missing interface fields")
            if not 25 <= len(values.get("short_description", "")) <= 64:
                errors.append(f"{name}: short description must be 25–64 characters")
            if f"${name}" not in values.get("default_prompt", ""):
                errors.append(f"{name}: prompt must name its skill")
        for doc in folder.rglob("*.md"):
            if ".godot" in doc.parts or "artifacts" in doc.parts:
                continue
            body = doc.read_text(encoding="utf-8")
            if re.search(r"/Users/|/private/tmp/|\[TODO:|INSERT[_ ]HERE", body):
                errors.append(f"{doc.relative_to(root)}: personal path or unfinished scaffold")
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", body):
                if "://" in link or link.startswith("#"):
                    continue
                target = (doc.parent / link.split("#", 1)[0]).resolve()
                if not target.is_relative_to(folder.resolve()):
                    errors.append(f"{doc.relative_to(root)}: link escapes installed skill: {link}")
                elif not target.exists():
                    errors.append(f"{doc.relative_to(root)}: broken local link: {link}")
    for file in root.rglob("*.py"):
        if any(part in {".git", "__pycache__", ".godot", "artifacts"} for part in file.parts):
            continue
        try:
            ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        except SyntaxError as exc:
            errors.append(str(exc))
    return errors


if __name__ == "__main__":
    problems = validate()
    for problem in problems:
        print(f"ERROR: {problem}")
    if not problems:
        print(f"PASS: {len(NAMES)} skills; metadata, self-contained links and Python syntax")
    raise SystemExit(bool(problems))
