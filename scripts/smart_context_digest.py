#!/usr/bin/env python3
"""
Generate safe Smart Context digests (report-only) for morning/progress/nightly runs.

No external side effects:
- reads memory/session/research files
- writes a markdown report under logs/digests/YYYY-MM-DD/
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


SUMMARY_FIELDS = [
    "本次核心产出",
    "技术要点",
    "代码模式",
    "决策上下文",
    "避坑记录",
    "适用场景",
    "搜索关键词",
    "项目关联",
    "置信度",
]


@dataclass
class DigestStats:
    session_files: int
    paused_sessions: int
    gold_hits: int
    pack_files: int
    card_files: int
    sessions_missing_summary: int
    sessions_missing_json: int


def load_config(repo_root: Path) -> dict:
    config_path = repo_root / "config.json"
    if not config_path.exists():
        return {}
    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def resolve_workspace(repo_root: Path, override: str | None) -> Path:
    if override:
        return Path(override).expanduser().resolve()
    cfg = load_config(repo_root)
    base = cfg.get("paths", {}).get("base")
    if base:
        return Path(base).expanduser().resolve()
    return repo_root.parent


def _extract_gold_and_paused(text: str) -> Tuple[int, int]:
    gold_hits = len(re.findall(r"#GOLD", text, flags=re.IGNORECASE))
    paused_hits = len(re.findall(r"#PAUSED", text, flags=re.IGNORECASE))
    return gold_hits, paused_hits


def _json_blocks(content: str) -> List[str]:
    return re.findall(r"```json\s*\n([\s\S]*?)\n```", content, flags=re.MULTILINE)


def _has_structured_summary_json(content: str) -> bool:
    for block in _json_blocks(content):
        try:
            data = json.loads(block)
        except json.JSONDecodeError:
            continue
        if all(k in data for k in SUMMARY_FIELDS):
            return True
    return False


def collect_stats(workspace: Path, day: datetime) -> Tuple[DigestStats, List[str], List[str]]:
    day_dir = workspace / "90_Memory" / day.strftime("%Y-%m-%d")
    daily_index = day_dir / "_DAILY_INDEX.md"

    session_files = sorted(day_dir.glob("session_*.md")) if day_dir.exists() else []
    pack_files = sorted(day_dir.glob("*deep-research-pack.md"))
    card_files = sorted(day_dir.glob("*deep-research-card.md"))

    daily_text = daily_index.read_text(encoding="utf-8") if daily_index.exists() else ""
    gold_hits_daily, paused_hits_daily = _extract_gold_and_paused(daily_text)

    missing_summary: List[str] = []
    missing_json: List[str] = []

    for session in session_files:
        txt = session.read_text(encoding="utf-8")
        if "## 📋 总结" not in txt:
            missing_summary.append(session.name)
        if not _has_structured_summary_json(txt):
            missing_json.append(session.name)

    stats = DigestStats(
        session_files=len(session_files),
        paused_sessions=paused_hits_daily,
        gold_hits=gold_hits_daily,
        pack_files=len(pack_files),
        card_files=len(card_files),
        sessions_missing_summary=len(missing_summary),
        sessions_missing_json=len(missing_json),
    )
    return stats, missing_summary, missing_json


def render_digest(mode: str, workspace: Path, day: datetime, stats: DigestStats, missing_summary: List[str], missing_json: List[str]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    day_str = day.strftime("%Y-%m-%d")

    focus_line = {
        "morning": "今天优先推进：活跃会话与研究工件完整性。",
        "progress": "进度检查：确认新增决策是否已写入 #GOLD 与 session slice。",
        "nightly": "夜间沉淀：归档今日产出并标注可复用资产。",
    }.get(mode, "Smart Context digest")

    suggestions = []
    if stats.sessions_missing_summary > 0:
        suggestions.append(f"补齐 {stats.sessions_missing_summary} 个 session 的 `## 📋 总结`。")
    if stats.sessions_missing_json > 0:
        suggestions.append(f"补齐 {stats.sessions_missing_json} 个 session 的结构化 JSON v3.1。")
    if stats.pack_files == 0 and stats.card_files == 0:
        suggestions.append("今日尚无 Pack/Card，至少产出 1 组研究工件。")
    if not suggestions:
        suggestions = ["当前沉淀完整，继续按双轨证据推进下一任务。"]

    missing_summary_block = "\n".join(f"- {name}" for name in missing_summary[:20]) or "- 无"
    missing_json_block = "\n".join(f"- {name}" for name in missing_json[:20]) or "- 无"
    suggestions_block = "\n".join(f"- {item}" for item in suggestions)

    return f"""# Smart Context Digest ({mode})

- Generated at: {now}
- Workspace: `{workspace}`
- Date scope: `{day_str}`

## Focus
{focus_line}

## Snapshot
- Session slices: {stats.session_files}
- #PAUSED marks (daily index): {stats.paused_sessions}
- #GOLD marks (daily index): {stats.gold_hits}
- Deep Research Pack: {stats.pack_files}
- Deep Research Card: {stats.card_files}

## Quality Gates
- Sessions missing `## 📋 总结`: {stats.sessions_missing_summary}
- Sessions missing structured JSON v3.1: {stats.sessions_missing_json}

## Missing Summary Files
{missing_summary_block}

## Missing JSON Files
{missing_json_block}

## Recommended Next Actions
{suggestions_block}
"""


def write_report(workspace: Path, mode: str, content: str, day: datetime) -> Path:
    out_dir = workspace / "logs" / "digests" / day.strftime("%Y-%m-%d")
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%H%M%S")
    out_path = out_dir / f"{mode}-{ts}.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate safe Smart Context digest")
    parser.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]), help="Deep-Sea Nexus repo root")
    parser.add_argument("--workspace", default=None, help="Override workspace path")
    parser.add_argument("--mode", choices=["morning", "progress", "nightly"], default="nightly")
    parser.add_argument("--date", default=None, help="Date in YYYY-MM-DD, default today")
    parser.add_argument("--dry-run", action="store_true", help="Print report, do not write file")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    workspace = resolve_workspace(repo_root, args.workspace)

    if args.date:
        day = datetime.strptime(args.date, "%Y-%m-%d")
    else:
        day = datetime.now()

    stats, missing_summary, missing_json = collect_stats(workspace, day)
    report = render_digest(args.mode, workspace, day, stats, missing_summary, missing_json)

    if args.dry_run:
        print(report)
        return 0

    out_path = write_report(workspace, args.mode, report, day)
    print(f"[digest] mode={args.mode} output={out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
