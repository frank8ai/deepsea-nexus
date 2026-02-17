#!/usr/bin/env python3
"""
Validate PARA Warm readiness: ensure Warm + Blueprint exist and are fresh.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path


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


def check_project(project_dir: Path, max_age_minutes: int) -> dict:
    warm = project_dir / "Warm.md"
    blueprint = project_dir / "Blueprint.md"
    abstract = project_dir / ".abstract.md"
    overview = project_dir / ".overview.md"
    now = datetime.now().timestamp()
    max_age = max_age_minutes * 60

    def age_ok(path: Path) -> bool:
        if not path.exists():
            return False
        return (now - path.stat().st_mtime) <= max_age

    return {
        "project": project_dir.name,
        "warm_exists": warm.exists(),
        "blueprint_exists": blueprint.exists(),
        "l0_exists": abstract.exists(),
        "l1_exists": overview.exists(),
        "warm_fresh": age_ok(warm),
        "blueprint_fresh": age_ok(blueprint),
        "warm_path": str(warm),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), help="Deep-Sea Nexus root")
    parser.add_argument("--obsidian", default=None, help="Obsidian vault path")
    parser.add_argument("--project", required=True, help="Project name")
    parser.add_argument("--max-age-minutes", type=int, default=120)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    obsidian_base = resolve_obsidian_base(repo_root, args.obsidian)
    project_dir = (obsidian_base / "10_Projects" / args.project).resolve()

    if not project_dir.exists():
        raise SystemExit(f"Project not found: {project_dir}")

    result = check_project(project_dir, args.max_age_minutes)
    ok = result["warm_exists"] and result["blueprint_exists"] and result["warm_fresh"]
    if args.json:
        print(json.dumps({"ok": ok, "result": result}, ensure_ascii=False, indent=2))
        return

    print(f"Project: {result['project']}")
    print(f"Warm exists: {result['warm_exists']}, fresh: {result['warm_fresh']}")
    print(f"Blueprint exists: {result['blueprint_exists']}, fresh: {result['blueprint_fresh']}")
    print(f"L0/L1 exists: {result['l0_exists']}/{result['l1_exists']}")
    print("OK" if ok else "NOT READY")


if __name__ == "__main__":
    main()
