#!/usr/bin/env python3
"""
Initialize Obsidian PARA structure and templates for Deep-Sea Nexus.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


BLUEPRINT_TEMPLATE = """# Blueprint

Objective:

Milestones:
- 

Acceptance:
- 

Current Step:

Blockers:
- 

Rollback Points:
- 

Links:
- 
"""


WARM_TEMPLATE = """# Warm

Objective:

Current Step:

Next Actions:
- 

Decision Log:
- 

Pitfalls:
- 

Key Links:
- 

Acceptance:
- 
"""


def load_config(repo_root: Path) -> dict:
    config_path = repo_root / "config.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def resolve_obsidian_base(repo_root: Path, override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    config = load_config(repo_root)
    base = Path(config.get("paths", {}).get("base", repo_root)).expanduser().resolve()
    obsidian = config.get("paths", {}).get("obsidian", "Obsidian")
    obsidian_path = Path(obsidian)
    if not obsidian_path.is_absolute():
        obsidian_path = base / obsidian_path
    return obsidian_path


def ensure_dirs(obsidian_base: Path) -> dict:
    projects = obsidian_base / "10_Projects"
    knowledge = obsidian_base / "20_Knowledge"
    areas = knowledge / "Areas"
    resources = knowledge / "Resources"
    archive = knowledge / "Archive"
    memory = obsidian_base / "90_Memory"
    for path in (projects, areas, resources, archive, memory):
        path.mkdir(parents=True, exist_ok=True)
    return {
        "projects": projects,
        "areas": areas,
        "resources": resources,
        "archive": archive,
        "memory": memory,
    }


def init_project(project_dir: Path, force: bool) -> None:
    blueprint = project_dir / "Blueprint.md"
    warm = project_dir / "Warm.md"
    if force or not blueprint.exists():
        blueprint.write_text(BLUEPRINT_TEMPLATE, encoding="utf-8")
    if force or not warm.exists():
        warm.write_text(WARM_TEMPLATE, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), help="Deep-Sea Nexus root")
    parser.add_argument("--obsidian", default=None, help="Obsidian vault path")
    parser.add_argument("--project", default=None, help="Initialize a project directory")
    parser.add_argument("--force", action="store_true", help="Overwrite templates if they exist")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    obsidian_base = resolve_obsidian_base(repo_root, args.obsidian)
    dirs = ensure_dirs(obsidian_base)

    if args.project:
        project_dir = dirs["projects"] / args.project
        project_dir.mkdir(parents=True, exist_ok=True)
        init_project(project_dir, args.force)

    print(f"✅ Obsidian PARA initialized at: {obsidian_base}")


if __name__ == "__main__":
    main()
