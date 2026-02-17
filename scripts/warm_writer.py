#!/usr/bin/env python3
"""
Warm writer: convert structured summaries into PARA Warm cards (L0/L1/L2).
"""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any


BLUEPRINT_TEMPLATE = """# Blueprint

Objective: {objective}

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
- {memory_link}
"""


WARM_TEMPLATE = """# Warm

Objective:
{objective}

Current Step:
{current_step}

Next Actions:
{next_actions}

Decision Log:
{decisions}

Pitfalls:
{pitfalls}

Key Links:
{links}

Acceptance:
{acceptance}
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


def ensure_para_dirs(obsidian_base: Path) -> dict:
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


def _sanitize_project(name: str) -> str:
    name = name.strip()
    name = re.sub(r"[\\/:*?\"<>|]", "_", name)
    return name or "Untitled"


def _split_lines(value: str) -> list[str]:
    parts = []
    for line in re.split(r"[\\n;；]", value or ""):
        item = line.strip(" -•\t")
        if item:
            parts.append(item)
    return parts


def _coerce_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    if isinstance(value, str):
        return _split_lines(value)
    return [str(value)]


def _normalize_summary(data: dict) -> dict:
    def get_any(keys: list[str]) -> Any:
        for key in keys:
            if key in data:
                return data[key]
        return None

    return {
        "core_output": get_any(["本次核心产出", "core_output", "summary", "核心产出", "output"]) or "",
        "tech_points": _coerce_list(get_any(["技术要点", "tech_points", "key_points"])),
        "code_pattern": get_any(["代码模式", "code_pattern"]) or "",
        "decision_context": get_any(["决策上下文", "decision_context", "decisions"]) or "",
        "pitfall_record": get_any(["避坑记录", "pitfall_record", "pitfalls"]) or "",
        "applicable_scene": get_any(["适用场景", "applicable_scene"]) or "",
        "search_keywords": _coerce_list(get_any(["搜索关键词", "search_keywords", "keywords"])),
        "project": get_any(["项目关联", "project关联", "project", "project_name"]) or "",
        "next_actions": _coerce_list(get_any(["next_actions", "下一步", "next_steps", "todo"]))[:3],
        "confidence": get_any(["置信度", "confidence"]) or "medium",
    }


def _summary_from_response(response: str) -> dict | None:
    try:
        from auto_summary import SummaryParser  # type: ignore
    except Exception:
        return None
    _reply, summary = SummaryParser.parse(response)
    if summary is None:
        return None
    return _normalize_summary(summary.to_dict())


def load_summary(source: Path) -> dict | None:
    if not source.exists():
        return None
    if source.suffix.lower() == ".json":
        data = json.loads(source.read_text(encoding="utf-8"))
        if "full_response" in data or "response" in data:
            response = data.get("full_response") or data.get("response") or ""
            summary = _summary_from_response(response)
            if summary:
                return summary
        return _normalize_summary(data)
    content = source.read_text(encoding="utf-8")
    match = re.search(r"```json\\s*([\\s\\S]*?)```", content, re.MULTILINE)
    if match:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return None
        return _normalize_summary(data)
    return None


def write_l0_l1(project_dir: Path, objective: str, decisions: list[str], next_actions: list[str], keywords: list[str]) -> None:
    abstract_path = project_dir / ".abstract.md"
    overview_path = project_dir / ".overview.md"
    abstract = f"{objective}".strip() or "Project update"
    if keywords:
        abstract = f"{abstract} | {'/'.join(keywords[:3])}"
    abstract_path.write_text(abstract + "\n", encoding="utf-8")

    overview_lines = [
        "# Overview",
        f"- Objective: {objective or '未填写'}",
    ]
    if decisions:
        overview_lines.append(f"- Decisions: {'; '.join(decisions[:3])}")
    if next_actions:
        overview_lines.append(f"- Next: {'; '.join(next_actions[:3])}")
    overview_path.write_text("\n".join(overview_lines) + "\n", encoding="utf-8")


def ensure_project(projects_dir: Path, project: str, objective: str, memory_link: str, force_blueprint: bool) -> Path:
    project_dir = projects_dir / _sanitize_project(project)
    project_dir.mkdir(parents=True, exist_ok=True)
    blueprint = project_dir / "Blueprint.md"
    if force_blueprint or not blueprint.exists():
        blueprint.write_text(
            BLUEPRINT_TEMPLATE.format(objective=objective or "TBD", memory_link=memory_link),
            encoding="utf-8",
        )
    return project_dir


def format_block(lines: list[str]) -> str:
    if not lines:
        return "-"
    return "\n".join(f"- {line}" for line in lines)


def write_warm(project_dir: Path, summary: dict, memory_link: str, acceptance: str) -> None:
    objective = summary.get("core_output") or "TBD"
    decisions = _split_lines(summary.get("decision_context", "")) + summary.get("tech_points", [])
    decisions = [d for d in decisions if d][:7]
    next_actions = summary.get("next_actions") or []
    pitfalls = _split_lines(summary.get("pitfall_record", ""))
    links = [memory_link]
    if summary.get("code_pattern"):
        links.append("Code pattern: " + summary["code_pattern"])

    warm_content = WARM_TEMPLATE.format(
        objective=objective,
        current_step=next_actions[0] if next_actions else "TBD",
        next_actions=format_block(next_actions),
        decisions=format_block(decisions),
        pitfalls=format_block(pitfalls),
        links=format_block(links),
        acceptance=acceptance,
    )
    (project_dir / "Warm.md").write_text(warm_content, encoding="utf-8")

    write_l0_l1(project_dir, objective, decisions, next_actions, summary.get("search_keywords", []))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), help="Deep-Sea Nexus root")
    parser.add_argument("--obsidian", default=None, help="Obsidian vault path")
    parser.add_argument("--from", dest="source", required=True, help="Summary JSON or markdown file")
    parser.add_argument("--project", default=None, help="Override project name")
    parser.add_argument("--force-blueprint", action="store_true", help="Overwrite Blueprint.md if exists")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    obsidian_base = resolve_obsidian_base(repo_root, args.obsidian)
    dirs = ensure_para_dirs(obsidian_base)

    summary = load_summary(Path(args.source).expanduser())
    if not summary:
        raise SystemExit("No structured summary found.")

    project = args.project or summary.get("project") or "Untitled"
    project = _sanitize_project(project)

    today = datetime.now().strftime("%Y-%m-%d")
    memory_link = f"[[90_Memory/{today}]]"
    acceptance = "TEST_CMD 通过"  # default acceptance

    if args.dry_run:
        print(f"Project: {project}")
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return

    project_dir = ensure_project(dirs["projects"], project, summary.get("core_output", ""), memory_link, args.force_blueprint)
    write_warm(project_dir, summary, memory_link, acceptance)

    print(f"✅ Warm updated: {project_dir / 'Warm.md'}")


if __name__ == "__main__":
    main()
