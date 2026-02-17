#!/usr/bin/env python3
"""Batch upgrade SOPs to governance v2 and generate L0/L1 retrieval layers."""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOP_GLOB = "resources/sop/2026-02/*-sop.md"


def section_bounds(text: str, heading: str) -> tuple[int, int, int] | None:
    m = re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE)
    if not m:
        return None
    content_start = m.end()
    rest = text[content_start:]
    n = re.search(r"^## ", rest, flags=re.MULTILINE)
    end = content_start + n.start() if n else len(text)
    return (m.start(), content_start, end)


def get_section(text: str, heading: str) -> str:
    b = section_bounds(text, heading)
    if not b:
        return ""
    _, start, end = b
    return text[start:end]


def replace_section(text: str, heading: str, new_content: str) -> str:
    b = section_bounds(text, heading)
    if not b:
        return text
    hstart, cstart, end = b
    prefix = text[:cstart]
    suffix = text[end:]
    body = "\n" + new_content.strip("\n") + "\n\n"
    if suffix.startswith("\n"):
        body = "\n" + new_content.strip("\n") + "\n"
    return prefix + body + suffix.lstrip("\n")


def insert_section_before(text: str, before_heading: str, heading: str, content: str) -> str:
    if section_bounds(text, heading):
        return replace_section(text, heading, content)
    b = section_bounds(text, before_heading)
    if not b:
        return text.rstrip() + f"\n\n## {heading}\n{content.strip()}\n"
    hstart, _, _ = b
    before = text[:hstart].rstrip("\n")
    after = text[hstart:]
    return before + f"\n\n## {heading}\n{content.strip()}\n\n" + after.lstrip("\n")


def parse_bullets(section: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in section.splitlines():
        m = re.match(r"^- ([^:]+):\s*(.*)$", line.strip())
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


def slug_from_path(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"^\d{4}-\d{2}-\d{2}-", "", stem)
    stem = stem.replace("-sop", "")
    return stem


def derive_tags(path: Path, existing: str) -> str:
    if existing:
        return existing
    parts = [p for p in slug_from_path(path).split("-") if p]
    return ", ".join(parts)


def derive_primary_triggers(text: str, existing: str) -> str:
    if existing:
        return existing
    sec = get_section(text, "Trigger Conditions (if/then)")
    items: list[str] = []
    for line in sec.splitlines():
        s = line.strip()
        if s.startswith("- IF "):
            items.append(s[5:].rstrip(".,"))
    return "; ".join(items[:3]) if items else "trigger conditions in this SOP are met"


def derive_primary_outputs(text: str, existing: str) -> str:
    if existing:
        return existing
    sec = get_section(text, "Outputs")
    items: list[str] = []
    for line in sec.splitlines():
        m = re.match(r"^- Output \d+:\s*(.+)$", line.strip())
        if m:
            items.append(m.group(1).strip().rstrip("."))
    if not items:
        for line in sec.splitlines():
            if line.strip().startswith("- "):
                items.append(line.strip()[2:].strip().rstrip("."))
    return "; ".join(items[:3]) if items else "documented outputs in this SOP"


def build_metadata(text: str, path: Path) -> str:
    sec = get_section(text, "Metadata")
    meta = parse_bullets(sec)
    name = meta.get("Name", "")
    owner = meta.get("Owner", "yizhi")

    tags = derive_tags(path, meta.get("Tags", ""))
    primary_triggers = derive_primary_triggers(text, meta.get("Primary triggers", ""))
    primary_outputs = derive_primary_outputs(text, meta.get("Primary outputs", ""))

    defaults = {
        "Effective condition": "all hard gates checked; strict validation passes; release approved",
        "Review cycle": "monthly",
        "Retirement condition": "primary result metric degrades for 2 consecutive monthly cycles, workflow obsolete, or compliance change",
    }

    ordered_keys = [
        "SOP ID",
        "Name",
        "Tags",
        "Primary triggers",
        "Primary outputs",
        "Owner",
        "Team",
        "Version",
        "Status",
        "Risk tier",
        "Reversibility class",
        "Evidence tier at release",
        "Effective condition",
        "Review cycle",
        "Retirement condition",
        "Created on",
        "Last reviewed on",
    ]

    out: list[str] = []
    for key in ordered_keys:
        if key == "Tags":
            value = tags
        elif key == "Primary triggers":
            value = primary_triggers
        elif key == "Primary outputs":
            value = primary_outputs
        else:
            value = meta.get(key, defaults.get(key, ""))
        if not value:
            if key == "Owner":
                value = owner
            elif key == "Name":
                value = name
            elif key in defaults:
                value = defaults[key]
        out.append(f"- {key}: {value}")

    for key, value in meta.items():
        if key not in ordered_keys:
            out.append(f"- {key}: {value}")
    return "\n".join(out)


def build_principle_section(text: str) -> str:
    sec = get_section(text, "Principle Compliance Declaration")
    fields = parse_bullets(sec)
    defaults = {
        "Non-negotiables check": "non-negotiable constraints are explicitly checked and enforced before execution",
        "Outcome metric and baseline": "baseline and target delta are defined in SLA and Metrics section",
        "Reversibility and blast radius": "reversibility class and blast radius are declared with rollback path",
        "Evidence tier justification": "evidence tier aligns with risk and reversibility matrix",
        "Best Practice compliance": "practice selection follows source-backed best practice with failure modes",
        "Best Method compliance": "method selection follows weighted score and hard constraints",
        "Best Tool compliance": "tools are minimum viable and justified with measurable gains plus rollback",
        "Simplicity and maintainability check": "workflow keeps minimum necessary steps and avoids tool/process bloat",
        "Closed-loop writeback check": "each cycle writes back 1-3 rules with source links and review date",
        "Compliance reviewer": fields.get("Compliance reviewer", "yizhi") or "yizhi",
    }
    order = [
        "Non-negotiables check",
        "Outcome metric and baseline",
        "Reversibility and blast radius",
        "Evidence tier justification",
        "Best Practice compliance",
        "Best Method compliance",
        "Best Tool compliance",
        "Simplicity and maintainability check",
        "Closed-loop writeback check",
        "Compliance reviewer",
    ]
    lines: list[str] = []
    for key in order:
        value = fields.get(key, "").strip() or defaults[key]
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)


def ensure_sla_lines(text: str) -> str:
    sec = get_section(text, "SLA and Metrics")
    lines = [ln for ln in sec.strip().splitlines() if ln.strip()]
    keys = {m.group(1).strip() for ln in lines if (m := re.match(r"^- ([^:]+):", ln.strip()))}
    additions = []
    if "Result metric (primary)" not in keys:
        additions.append(
            "- Result metric (primary): first-pass yield target and adoption target are primary release and downgrade metrics."
        )
    if "Process metric (secondary)" not in keys:
        additions.append(
            "- Process metric (secondary): cycle time target and rework rate ceiling are secondary diagnostic metrics."
        )
    if "Replacement rule" not in keys:
        additions.append(
            "- Replacement rule: process metrics cannot replace result metrics for release decisions."
        )
    if additions:
        sec_new = sec.rstrip("\n") + "\n" + "\n".join(additions) + "\n"
        return replace_section(text, "SLA and Metrics", sec_new.strip("\n"))
    return text


def ensure_release_auto_gate(text: str) -> str:
    sec = get_section(text, "Release Readiness")
    if re.search(r"^- Auto-downgrade gate:\s*.+$", sec, flags=re.MULTILINE):
        return text
    line = (
        "- Auto-downgrade gate: if monthly KPI trend shows primary result metric degradation for 2 consecutive cycles, "
        "set `Status: draft` and rerun pilot + strict validation."
    )
    if re.search(r"^- Release decision:", sec, flags=re.MULTILINE):
        sec = re.sub(r"(^- Release decision:)", line + "\n" + r"\1", sec, flags=re.MULTILINE, count=1)
    else:
        sec = sec.rstrip("\n") + "\n" + line + "\n"
    return replace_section(text, "Release Readiness", sec.strip("\n"))


def ensure_links_l0_l1(text: str, sop_path: Path) -> str:
    sec = get_section(text, "Links")
    rel = str(sop_path.relative_to(REPO_ROOT))
    l0 = rel.replace(".md", ".abstract.md")
    l1 = rel.replace(".md", ".overview.md")
    lines = sec.strip().splitlines()
    if not any(ln.strip().startswith("- L0 abstract:") for ln in lines):
        lines.append(f"- L0 abstract: {l0}")
    if not any(ln.strip().startswith("- L1 overview:") for ln in lines):
        lines.append(f"- L1 overview: {l1}")
    return replace_section(text, "Links", "\n".join(lines))


def generate_l0_l1(text: str, sop_path: Path) -> None:
    meta = parse_bullets(get_section(text, "Metadata"))
    name = meta.get("Name", sop_path.name)
    triggers = meta.get("Primary triggers", "trigger conditions in SOP")
    outputs = meta.get("Primary outputs", "outputs defined in SOP")
    objective = get_section(text, "Objective").strip().splitlines()
    objective_line = objective[0].strip() if objective else "Standardize execution with explicit outputs and gates."

    inputs_sec = get_section(text, "Inputs")
    inputs = [ln.strip()[2:] for ln in inputs_sec.splitlines() if ln.strip().startswith("- ")]
    outputs_sec = get_section(text, "Outputs")
    outputs_list = [ln.strip()[2:] for ln in outputs_sec.splitlines() if ln.strip().startswith("- ")]

    proc_sec = get_section(text, "Procedure")
    actions: list[str] = []
    for line in proc_sec.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        if s.startswith("|---") or s.startswith("| Step "):
            continue
        parts = [p.strip() for p in s.strip("|").split("|")]
        if len(parts) >= 2:
            actions.append(parts[1])
    actions = actions[:8]

    gate_sec = get_section(text, "Hard Gates (must pass before activation)")
    gates = []
    for line in gate_sec.splitlines():
        m = re.match(r"^- \[[ xX]\] (.+)$", line.strip())
        if m:
            gates.append(m.group(1).strip())
    gates = gates[:3]

    l0 = [
        f"# L0 Abstract - {name}",
        "",
        f"{objective_line} 触发条件：{triggers}。核心产出：{outputs}。",
    ]
    l0_path = sop_path.with_suffix(".abstract.md")
    l0_path.write_text("\n".join(l0).strip() + "\n", encoding="utf-8")

    l1_lines: list[str] = []
    l1_lines.append(f"# L1 Overview - {name}")
    l1_lines.append("")
    l1_lines.append("## When to use")
    for item in [x.strip() for x in triggers.split(";") if x.strip()]:
        l1_lines.append(f"- {item}")
    l1_lines.append("")
    l1_lines.append("## Inputs")
    for item in inputs[:5]:
        l1_lines.append(f"- {item}")
    l1_lines.append("")
    l1_lines.append("## Outputs")
    for item in outputs_list[:5]:
        l1_lines.append(f"- {item}")
    l1_lines.append("")
    l1_lines.append("## Minimal procedure")
    for idx, action in enumerate(actions, start=1):
        l1_lines.append(f"{idx}) {action}")
    l1_lines.append("")
    l1_lines.append("## Quality gates")
    for item in gates:
        l1_lines.append(f"- {item}")
    l1_lines.append("")
    l1_lines.append("## Invocation")
    l1_lines.append(f"`按SOP执行：{name} <输入>`")
    l1_lines.append("")

    l1_path = sop_path.with_suffix(".overview.md")
    l1_path.write_text("\n".join(l1_lines), encoding="utf-8")


def ensure_kill_switch(text: str) -> str:
    kill = "\n".join(
        [
            "| Trigger threshold | Immediate stop | Rollback action |",
            "|---|---|---|",
            "| Non-negotiable breach (legal/safety/security/data integrity) | Stop execution immediately and block release | Revert to last approved SOP version and open incident record |",
            "| Primary result metric degrades for 2 consecutive monthly cycles | Downgrade SOP status to `draft` and stop rollout | Restore previous stable SOP and rerun pilot >= 5 with strict validation |",
        ]
    )
    return insert_section_before(text, "Rollback and Stop Conditions", "Kill Switch", kill)


def upgrade_file(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = replace_section(text, "Metadata", build_metadata(text, path))
    text = replace_section(text, "Principle Compliance Declaration", build_principle_section(text))
    text = ensure_kill_switch(text)
    text = ensure_sla_lines(text)
    text = ensure_release_auto_gate(text)
    text = ensure_links_l0_l1(text, path)
    path.write_text(text, encoding="utf-8")
    generate_l0_l1(text, path)


def main() -> None:
    paths = sorted(REPO_ROOT.glob(SOP_GLOB))
    for path in paths:
        upgrade_file(path)
    print(f"Upgraded SOP files: {len(paths)}")


if __name__ == "__main__":
    main()

