#!/usr/bin/env python3
"""
PARA recall: directory-recursive retrieval with L0/L1/L2 minimization.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


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


def tokenize(text: str) -> list[str]:
    tokens = re.split(r"[^0-9A-Za-z\\u4e00-\\u9fff]+", text.lower())
    return [t for t in tokens if t]


def score_text(text: str, query_tokens: list[str]) -> float:
    score = 0.0
    if not text:
        return score
    lower = text.lower()
    for token in query_tokens:
        score += lower.count(token)
    return score


def read_text(path: Path, max_chars: int = 800) -> str:
    if not path.exists():
        return ""
    content = path.read_text(encoding="utf-8")
    return content[:max_chars]


def project_score(project_dir: Path, query_tokens: list[str]) -> dict:
    abstract = read_text(project_dir / ".abstract.md", 300)
    overview = read_text(project_dir / ".overview.md", 1200)
    warm = read_text(project_dir / "Warm.md", 1600)
    score = score_text(abstract, query_tokens) * 2.0 + score_text(overview, query_tokens) * 1.2 + score_text(warm, query_tokens)
    mtime = max((project_dir / ".abstract.md").stat().st_mtime if (project_dir / ".abstract.md").exists() else 0,
                (project_dir / "Warm.md").stat().st_mtime if (project_dir / "Warm.md").exists() else 0)
    recency_bonus = 0.0
    if mtime:
        days = max(0.0, (datetime.now().timestamp() - mtime) / 86400.0)
        recency_bonus = max(0.0, 5.0 - days) * 0.1
    return {
        "project": project_dir.name,
        "score": score + recency_bonus,
        "abstract": abstract.strip(),
        "overview": overview.strip(),
        "warm": warm.strip(),
        "path": str(project_dir),
    }


def collect_projects(projects_dir: Path) -> list[Path]:
    if not projects_dir.exists():
        return []
    return [p for p in projects_dir.iterdir() if p.is_dir()]


def write_trace(repo_root: Path, trace: dict[str, Any]) -> None:
    log_dir = repo_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    trace_path = log_dir / "para_recall_trace.jsonl"
    with trace_path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(trace, ensure_ascii=False) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), help="Deep-Sea Nexus root")
    parser.add_argument("--obsidian", default=None, help="Obsidian vault path")
    parser.add_argument("--query", required=True, help="Query text")
    parser.add_argument("--top-projects", type=int, default=3)
    parser.add_argument("--max-warm-lines", type=int, default=18)
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    obsidian_base = resolve_obsidian_base(repo_root, args.obsidian)
    projects_dir = obsidian_base / "10_Projects"
    query_tokens = tokenize(args.query)

    projects = [project_score(p, query_tokens) for p in collect_projects(projects_dir)]
    projects.sort(key=lambda x: x["score"], reverse=True)
    selected = projects[: args.top_projects]

    trace = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "query": args.query,
        "tokens": query_tokens,
        "candidates": [{k: v for k, v in item.items() if k in ("project", "score", "path")} for item in projects],
        "selected": [{k: v for k, v in item.items() if k in ("project", "score", "path")} for item in selected],
    }
    write_trace(repo_root, trace)

    if args.json:
        print(json.dumps({"query": args.query, "projects": selected}, ensure_ascii=False, indent=2))
        return

    lines = [f"# PARA Recall", f"Query: {args.query}", ""]
    for idx, item in enumerate(selected, 1):
        lines.append(f"{idx}. {item['project']} (score={item['score']:.2f})")
        if item["abstract"]:
            lines.append(f"   L0: {item['abstract']}")
        if item["overview"]:
            lines.append("   L1:")
            for ln in item["overview"].splitlines()[:6]:
                lines.append(f"     {ln}")
        if item["warm"]:
            lines.append("   Warm:")
            for ln in item["warm"].splitlines()[: args.max_warm_lines]:
                lines.append(f"     {ln}")
        lines.append(f"   Path: {item['path']}")
        lines.append("")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
