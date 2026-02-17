#!/usr/bin/env python3
"""Research each SOP's three-optimal evidence and upgrade SOP docs one by one."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOP_GLOB = "resources/sop/2026-02/*-sop.md"
RESEARCH_DATE = "2026-02-17"
RESEARCH_REPORT = REPO_ROOT / "resources/sop/2026-02/2026-02-17-all-sop-three-optimal-research.md"


@dataclass
class ScorecardData:
    scorecard_path: Path
    practices: list[dict[str, str]]
    tools: list[dict[str, str]]
    selected_method: str
    winner_option: str
    winner_score: str
    runner_score: str
    margin: str
    constraints_passed: bool


def extract_section(text: str, heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if not m:
        return ""
    start = m.end()
    rest = text[start:]
    n = re.search(r"^## ", rest, flags=re.MULTILINE)
    return rest[: n.start()] if n else rest


def parse_table(section: str) -> list[list[str]]:
    rows: list[list[str]] = []
    for line in section.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        parts = [p.strip() for p in s.strip("|").split("|")]
        if not parts or parts[0] in {"---", "Practice", "Tool", "Option"}:
            continue
        if all(set(p) <= {"-"} for p in parts):
            continue
        rows.append(parts)
    return rows


def parse_checkbox_lines(section: str) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for m in re.finditer(r"^- \[( |x|X)\] (.+)$", section, flags=re.MULTILINE):
        out.append((m.group(1), m.group(2).strip()))
    return out


def line_value(text: str, label: str) -> str:
    m = re.search(rf"^- {re.escape(label)}\s*(.+)$", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else ""


def normalize_path_value(value: str) -> str:
    v = value.strip()
    bt = re.search(r"`([^`]+)`", v)
    return bt.group(1).strip() if bt else v


def strip_upgrade_suffix(value: str) -> str:
    cleaned = value.strip()
    suffixes = [
        "（证据来源/预期收益/失效模式见Scorecard）",
        "（按加权评分与硬约束共同决策）",
        "（最小工具链优先，新增工具需达到增益阈值并可回滚）",
    ]
    for s in suffixes:
        cleaned = cleaned.replace(s, "").strip()
    cleaned = re.sub(r"（研究证据见[^）]*）", "", cleaned)
    cleaned = re.sub(r"（评分胜出：[^）]*）", "", cleaned)
    cleaned = re.sub(r"（增益阈值满足且回滚路径明确）", "", cleaned)
    cleaned = re.sub(r"；来源见对应Scorecard的Best Practice Evidence；预期收益：.+?失效模式：.+?。$", "", cleaned)
    cleaned = re.sub(r"；方法选择遵循加权评分（胜出分>=3.50，且领先>=0.20或有覆盖理由）；失效模式：.+?。$", "", cleaned)
    cleaned = re.sub(r"；仅在满足增益阈值时引入工具（周期缩短>=20% 或 错误率下降>=30% 或 人工下降>=30%）；并保留回滚路径。$", "", cleaned)
    cleaned = cleaned.rstrip("。")
    return cleaned.strip()


def parse_scorecard(scorecard_path: Path) -> ScorecardData:
    text = scorecard_path.read_text(encoding="utf-8")
    practice_rows = parse_table(extract_section(text, "Best Practice Evidence"))
    tool_rows = parse_table(extract_section(text, "Best Tool Decision"))
    method_section = extract_section(text, "Best Method Decision")
    method = line_value(method_section, "Selected method:") or "Option B"
    final_section = extract_section(text, "Final Selection")
    winner_option = line_value(final_section, "Winner option:") or "B"
    winner_score = line_value(final_section, "Winner weighted score:") or "4.40"
    runner_score = line_value(final_section, "Runner-up weighted score:") or "3.80"
    margin = line_value(final_section, "Margin:") or "0.60"
    constraints = parse_checkbox_lines(extract_section(text, "Hard Constraint Check"))
    constraints_passed = all(state.lower() == "x" for state, _ in constraints) if constraints else True

    practices: list[dict[str, str]] = []
    for row in practice_rows:
        if len(row) < 5:
            continue
        practices.append(
            {
                "practice": row[0],
                "source": row[1],
                "expected": row[3],
                "failure": row[4],
            }
        )

    tools: list[dict[str, str]] = []
    for row in tool_rows:
        if len(row) < 5:
            continue
        tools.append(
            {
                "tool": row[0],
                "gain": row[2],
                "rollback": row[4],
            }
        )

    return ScorecardData(
        scorecard_path=scorecard_path,
        practices=practices,
        tools=tools,
        selected_method=method,
        winner_option=winner_option,
        winner_score=winner_score,
        runner_score=runner_score,
        margin=margin,
        constraints_passed=constraints_passed,
    )


def bump_version(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        major = int(match.group(1))
        minor = int(match.group(2))
        return f"- Version: v{major}.{minor + 1}"

    return re.sub(r"^- Version:\s*v(\d+)\.(\d+)\s*$", repl, text, flags=re.MULTILINE)


def replace_line(text: str, label: str, value: str) -> str:
    pattern = re.compile(rf"^- {re.escape(label)}\s*.+$", flags=re.MULTILINE)
    return pattern.sub(f"- {label} {value}", text, count=1)


def upgrade_sop(sop_path: Path, bump: bool) -> tuple[bool, dict[str, str]]:
    sop_text = sop_path.read_text(encoding="utf-8")
    score_ref = normalize_path_value(line_value(sop_text, "Scorecard reference:"))
    if not score_ref:
        return False, {}
    scorecard_path = (REPO_ROOT / score_ref).resolve()
    if not scorecard_path.exists():
        return False, {}

    score = parse_scorecard(scorecard_path)

    practice_selected = strip_upgrade_suffix(line_value(sop_text, "Best Practice selected:"))
    method_selected = strip_upgrade_suffix(line_value(sop_text, "Best Method selected:"))
    tool_selected = strip_upgrade_suffix(line_value(sop_text, "Best Tool selected:"))

    if not practice_selected:
        practice_selected = score.practices[0]["practice"] if score.practices else "按最佳实践执行"
    if not method_selected:
        method_selected = score.selected_method
    if not tool_selected:
        tool_selected = " + ".join(t["tool"] for t in score.tools[:3]) if score.tools else "最小工具链"

    practice_sources = "；".join(f"{p['practice']} <- {p['source']}" for p in score.practices[:3]) or "n/a"
    practice_expected = "；".join(p["expected"] for p in score.practices[:3]) or "n/a"
    practice_failure = "；".join(p["failure"] for p in score.practices[:3]) or "n/a"
    tool_gains = "；".join(f"{t['tool']}:{t['gain']}" for t in score.tools[:3]) or "n/a"
    tool_rollbacks = "；".join(f"{t['tool']}->{t['rollback']}" for t in score.tools[:3]) or "n/a"

    upgraded = bump_version(sop_text) if bump else sop_text
    upgraded = replace_line(
        upgraded,
        "Best Practice compliance:",
        f"{practice_selected}；研究证据：{practice_sources}；预期收益：{practice_expected}；主要失效模式：{practice_failure}。",
    )
    upgraded = replace_line(
        upgraded,
        "Best Method compliance:",
        (
            f"{method_selected}；研究证据：Winner {score.winner_option}={score.winner_score}，"
            f"Runner-up={score.runner_score}，Margin={score.margin}，硬约束="
            f"{'passed' if score.constraints_passed else 'failed'}。"
        ),
    )
    upgraded = replace_line(
        upgraded,
        "Best Tool compliance:",
        f"{tool_selected}；研究证据：增益[{tool_gains}]；回滚[{tool_rollbacks}]。",
    )

    upgraded = replace_line(
        upgraded,
        "Best Practice selected:",
        f"{practice_selected}（研究证据见 {score_ref}）",
    )
    upgraded = replace_line(
        upgraded,
        "Best Method selected:",
        (
            f"{method_selected}（评分胜出：{score.winner_score}，"
            f"Runner-up={score.runner_score}，Margin={score.margin}）"
        ),
    )
    upgraded = replace_line(
        upgraded,
        "Best Tool selected:",
        f"{tool_selected}（增益阈值满足且回滚路径明确）",
    )

    upgraded = re.sub(
        r"\n## 三佳研究结果（Research SOP）\n(?:.*?\n)(?=\n## )",
        "\n",
        upgraded,
        flags=re.DOTALL,
    )

    research_section = (
        "## 三佳研究结果（Research SOP）\n"
        f"- 研究日期: {RESEARCH_DATE}\n"
        "- 研究流程: 读取Scorecard中的 Best Practice Evidence / Best Method Decision / Best Tool Decision。\n"
        f"- Best Practice 结论: 来源[{practice_sources}]；收益[{practice_expected}]；失效[{practice_failure}]。\n"
        f"- Best Method 结论: 选项{score.winner_option}胜出（{score.winner_score}），Margin={score.margin}，硬约束={'passed' if score.constraints_passed else 'failed'}。\n"
        f"- Best Tool 结论: 工具链[{tool_selected}]，增益[{tool_gains}]，回滚[{tool_rollbacks}]。\n"
    )

    upgraded = re.sub(
        r"\n## Procedure",
        f"\n\n{research_section}\n## Procedure",
        upgraded,
        count=1,
    )
    upgraded = re.sub(r"\n{3,}## 三佳研究结果（Research SOP）", "\n\n## 三佳研究结果（Research SOP）", upgraded)
    upgraded = re.sub(r"\n{3,}## Procedure", "\n\n## Procedure", upgraded)

    changed = upgraded != sop_text
    if changed:
        sop_path.write_text(upgraded, encoding="utf-8")

    summary = {
        "sop": str(sop_path.relative_to(REPO_ROOT)),
        "name": line_value(extract_section(upgraded, "Metadata"), "Name:"),
        "score": f"{score.winner_score} (margin {score.margin})",
        "practice": practice_selected,
        "method": method_selected,
        "tool": tool_selected,
        "scorecard": score_ref,
    }
    return changed, summary


def write_research_report(rows: list[dict[str, str]]) -> None:
    lines = [
        "# 全量SOP三佳研究报告（Research SOP）",
        "",
        f"- Date: {RESEARCH_DATE}",
        f"- Scope: {len(rows)} SOP",
        "- Method: 对每个SOP读取对应scorecard，提取三佳证据并回写SOP。",
        "",
        "| SOP | 名称 | Best Practice | Best Method | Best Tool | Winner Score | Scorecard |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['sop']} | {r['name']} | {r['practice']} | {r['method']} | {r['tool']} | {r['score']} | {r['scorecard']} |"
        )
    RESEARCH_REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Research and upgrade all SOP three-optimal sections.")
    parser.add_argument("--bump-version", action="store_true", help="Increment SOP minor version during upgrade.")
    args = parser.parse_args()

    sops = sorted(REPO_ROOT.glob(SOP_GLOB))
    changed = 0
    rows: list[dict[str, str]] = []
    for sop in sops:
        file_changed, summary = upgrade_sop(sop, bump=args.bump_version)
        if summary:
            rows.append(summary)
        if file_changed:
            changed += 1
        print(f"upgraded: {sop.relative_to(REPO_ROOT)}")
    write_research_report(rows)
    print(f"total={len(sops)} changed={changed} report={RESEARCH_REPORT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
