#!/usr/bin/env python3
"""Batch-upgrade SOP files to stronger three-optimal compliance wording."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def bump_version(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        major = int(match.group(1))
        minor = int(match.group(2))
        return f"- Version: v{major}.{minor + 1}"

    return re.sub(r"^- Version:\s*v(\d+)\.(\d+)\s*$", repl, text, flags=re.MULTILINE)


def upgrade_line(
    text: str,
    label: str,
    marker: str,
    suffix: str,
) -> str:
    pattern = re.compile(rf"^- {re.escape(label)}\s*(.+)$", flags=re.MULTILINE)

    def repl(match: re.Match[str]) -> str:
        content = match.group(1).strip()
        if marker in content:
            return match.group(0)
        return f"- {label} {content}{suffix}"

    return pattern.sub(repl, text, count=1)


def upgrade_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    updated = text

    updated = bump_version(updated)

    updated = upgrade_line(
        updated,
        "Best Practice compliance:",
        "Scorecard的Best Practice Evidence",
        "；来源见对应Scorecard的Best Practice Evidence；预期收益：提升关键指标并降低偏差；失效模式：场景误配或机械套用。",
    )
    updated = upgrade_line(
        updated,
        "Best Method compliance:",
        "胜出分>=3.50",
        "；方法选择遵循加权评分（胜出分>=3.50，且领先>=0.20或有覆盖理由）；失效模式：只看分数忽略硬约束。",
    )
    updated = upgrade_line(
        updated,
        "Best Tool compliance:",
        "增益阈值",
        "；仅在满足增益阈值时引入工具（周期缩短>=20% 或 错误率下降>=30% 或 人工下降>=30%）；并保留回滚路径。",
    )

    updated = upgrade_line(
        updated,
        "Best Practice selected:",
        "见Scorecard",
        "（证据来源/预期收益/失效模式见Scorecard）",
    )
    updated = upgrade_line(
        updated,
        "Best Method selected:",
        "加权评分与硬约束共同决策",
        "（按加权评分与硬约束共同决策）",
    )
    updated = upgrade_line(
        updated,
        "Best Tool selected:",
        "最小工具链优先",
        "（最小工具链优先，新增工具需达到增益阈值并可回滚）",
    )

    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Upgrade SOP docs with stronger three-optimal wording.")
    parser.add_argument(
        "--glob",
        default="resources/sop/2026-02/*-sop.md",
        help="Glob pattern for target SOP markdown files.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    targets = sorted(repo_root.glob(args.glob))
    if not targets:
        raise SystemExit(f"No files matched: {args.glob}")

    changed = 0
    for p in targets:
        if upgrade_file(p):
            changed += 1

    print(f"targets={len(targets)} changed={changed}")


if __name__ == "__main__":
    main()
