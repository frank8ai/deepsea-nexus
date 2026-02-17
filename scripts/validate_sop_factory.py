#!/usr/bin/env python3
"""
Validate SOP Factory artifacts against three-optimal release gates.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REQUIRED_SOP_SECTIONS = [
    "Metadata",
    "Hard Gates (must pass before activation)",
    "Principle Compliance Declaration",
    "Objective",
    "Scope and Boundaries",
    "Trigger Conditions (if/then)",
    "Inputs",
    "Outputs",
    "Three-Optimal Decision",
    "Procedure",
    "Rollback and Stop Conditions",
    "SLA and Metrics",
    "Change Control",
    "Release Readiness",
    "Links",
]

REQUIRED_SCORECARD_SECTIONS = [
    "Metadata",
    "Candidate Options",
    "Weighted Dimensions",
    "Scoring Table (1-5 for each dimension)",
    "Best Practice Evidence",
    "Best Method Decision",
    "Best Tool Decision",
    "Hard Constraint Check",
    "Final Selection",
]

DEFAULT_WEIGHTS = [0.35, 0.20, 0.20, 0.15, 0.10]
ALLOWED_RISK_TIERS = {"low", "medium", "high"}
ALLOWED_REVERSIBILITY = {"R1": 2, "R2": 3, "R3": 4}
ALLOWED_EVIDENCE = {"E1": 1, "E2": 2, "E3": 3, "E4": 4}
REQUIRED_DECLARATION_LINES = [
    "Non-negotiables check:",
    "Outcome metric and baseline:",
    "Reversibility and blast radius:",
    "Evidence tier justification:",
    "Best Practice compliance:",
    "Best Method compliance:",
    "Best Tool compliance:",
]


def extract_section(text: str, heading: str) -> str:
    pattern = rf"^## {re.escape(heading)}\s*$"
    start_match = re.search(pattern, text, flags=re.MULTILINE)
    if not start_match:
        return ""
    start = start_match.end()
    rest = text[start:]
    next_match = re.search(r"^## ", rest, flags=re.MULTILINE)
    if next_match:
        return rest[: next_match.start()]
    return rest


def has_heading(text: str, heading: str) -> bool:
    return bool(re.search(rf"^## {re.escape(heading)}\s*$", text, flags=re.MULTILINE))


def parse_checkbox_lines(section: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for m in re.finditer(r"^- \[( |x|X)\] (.+)$", section, flags=re.MULTILINE):
        items.append((m.group(1), m.group(2).strip()))
    return items


def parse_path_value(line_value: str, repo_root: Path) -> Path | None:
    value = line_value.strip()
    if not value:
        return None
    backtick = re.search(r"`([^`]+)`", value)
    raw = backtick.group(1).strip() if backtick else value
    if raw in {"n/a", "N/A", "<none>"}:
        return None
    p = Path(raw)
    if not p.is_absolute():
        p = (repo_root / p).resolve()
    return p


def find_line_value(text: str, label: str) -> str:
    m = re.search(rf"^- {re.escape(label)}[ \t]*([^\n]*)$", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else ""


def parse_status(text: str) -> str:
    m = re.search(r"^- Status:\s*(.+)$", text, flags=re.MULTILINE)
    return m.group(1).strip().lower() if m else ""


def normalize_token(value: str, upper: bool = True) -> str:
    token = value.strip().split()[0] if value.strip() else ""
    return token.upper() if upper else token.lower()


def parse_weighted_scores(scorecard_text: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    for line in scorecard_text.splitlines():
        if not line.strip().startswith("|"):
            continue
        if re.search(r"^\|\s*Option\s*\|", line):
            continue
        if re.search(r"^\|\s*---", line):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) != 7:
            continue
        option = parts[0]
        try:
            dims = [float(parts[i]) for i in range(1, 6)]
        except ValueError:
            continue
        weighted = sum(d * w for d, w in zip(dims, DEFAULT_WEIGHTS))
        scores[option] = round(weighted, 2)
    return scores


def parse_number_field(text: str, label: str) -> float | None:
    m = re.search(
        rf"^- {re.escape(label)}[ \t]*([0-9]+(?:\.[0-9]+)?)\s*$",
        text,
        flags=re.MULTILINE,
    )
    if not m:
        return None
    return float(m.group(1))


def parse_text_field(text: str, label: str) -> str:
    m = re.search(rf"^- {re.escape(label)}[ \t]*([^\n]*)$", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else ""


def count_nonempty_rule_updates(section: str) -> int:
    count = 0
    for m in re.finditer(r"^\d\.\s+When \(condition\):\s*(.+)$", section, flags=re.MULTILINE):
        payload = m.group(1).strip().lower()
        if payload and payload not in {".", "tbd", "<condition>"}:
            count += 1
    return count


def parse_int_field(text: str, label: str) -> int | None:
    m = re.search(rf"^- {re.escape(label)}[ \t]*([0-9]+)\s*$", text, flags=re.MULTILINE)
    if not m:
        return None
    return int(m.group(1))


def validate_sop(repo_root: Path, sop_path: Path, strict: bool) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    if not sop_path.exists():
        return {"ok": False, "errors": [f"SOP file not found: {sop_path}"], "warnings": []}

    sop_text = sop_path.read_text(encoding="utf-8")
    for heading in REQUIRED_SOP_SECTIONS:
        if not has_heading(sop_text, heading):
            errors.append(f"Missing SOP section: {heading}")

    hard_gate_section = extract_section(sop_text, "Hard Gates (must pass before activation)")
    hard_gate_items = parse_checkbox_lines(hard_gate_section)
    if strict and hard_gate_items:
        unchecked = [item for state, item in hard_gate_items if state.lower() != "x"]
        if unchecked:
            errors.append(f"Unchecked SOP hard gates: {', '.join(unchecked)}")

    status = parse_status(sop_text)
    metadata_section = extract_section(sop_text, "Metadata")
    risk_tier_raw = parse_text_field(metadata_section, "Risk tier:")
    reversibility_raw = parse_text_field(metadata_section, "Reversibility class:")
    evidence_raw = parse_text_field(metadata_section, "Evidence tier at release:")

    risk_tier = normalize_token(risk_tier_raw, upper=False)
    reversibility = normalize_token(reversibility_raw, upper=True)
    evidence_tier = normalize_token(evidence_raw, upper=True)

    if strict:
        if risk_tier not in ALLOWED_RISK_TIERS:
            errors.append(
                "Metadata `Risk tier` must be one of: low, medium, high."
            )
        if reversibility not in ALLOWED_REVERSIBILITY:
            errors.append(
                "Metadata `Reversibility class` must be one of: R1, R2, R3."
            )
        if evidence_tier not in ALLOWED_EVIDENCE:
            errors.append(
                "Metadata `Evidence tier at release` must be one of: E1, E2, E3, E4."
            )
        if reversibility in ALLOWED_REVERSIBILITY and evidence_tier in ALLOWED_EVIDENCE:
            required_evidence = ALLOWED_REVERSIBILITY[reversibility]
            actual_evidence = ALLOWED_EVIDENCE[evidence_tier]
            if actual_evidence < required_evidence:
                errors.append(
                    f"Evidence tier {evidence_tier} is insufficient for {reversibility}; "
                    f"requires at least E{required_evidence}."
                )
    else:
        if not risk_tier_raw:
            warnings.append("Missing `Risk tier` in metadata.")
        if not reversibility_raw:
            warnings.append("Missing `Reversibility class` in metadata.")
        if not evidence_raw:
            warnings.append("Missing `Evidence tier at release` in metadata.")

    principle_section = extract_section(sop_text, "Principle Compliance Declaration")
    for label in REQUIRED_DECLARATION_LINES:
        value = parse_text_field(principle_section, label)
        if strict and not value:
            errors.append(f"Missing declaration value: `{label}`")
        elif not strict and not value:
            warnings.append(f"Missing declaration value: `{label}`")

    rollback_section = extract_section(sop_text, "Rollback and Stop Conditions")
    blast_radius = parse_text_field(rollback_section, "Blast radius limit:")
    if strict and not blast_radius:
        errors.append("Missing `Blast radius limit` in rollback section.")

    release_section = extract_section(sop_text, "Release Readiness")
    release_decision = parse_text_field(release_section, "Release decision:")
    if strict and status == "active" and release_decision.lower() != "approve":
        errors.append("Active SOP requires `Release decision: approve`.")

    score_ref = find_line_value(sop_text, "Scorecard reference:")
    if not score_ref:
        if strict:
            errors.append("Missing `Scorecard reference` in SOP.")
        else:
            warnings.append("Missing `Scorecard reference` in SOP.")
        scorecard_path = None
    else:
        scorecard_path = parse_path_value(score_ref, repo_root)
        if not scorecard_path or not scorecard_path.exists():
            if strict:
                errors.append(f"Scorecard file not found: {score_ref}")
            else:
                warnings.append(f"Scorecard file not found: {score_ref}")

    iter_ref = find_line_value(sop_text, "Iteration log:")
    if not iter_ref:
        if strict:
            errors.append("Missing `Iteration log` link in SOP.")
        else:
            warnings.append("Missing `Iteration log` link in SOP.")
        iter_path = None
    else:
        iter_path = parse_path_value(iter_ref, repo_root)
        if not iter_path or not iter_path.exists():
            if strict:
                errors.append(f"Iteration log file not found: {iter_ref}")
            else:
                warnings.append(f"Iteration log file not found: {iter_ref}")

    scorecard_result: dict[str, Any] = {}
    if scorecard_path and scorecard_path.exists():
        score_text = scorecard_path.read_text(encoding="utf-8")
        for heading in REQUIRED_SCORECARD_SECTIONS:
            if not has_heading(score_text, heading):
                errors.append(f"Missing scorecard section: {heading}")

        hard_constraint_section = extract_section(score_text, "Hard Constraint Check")
        hc_items = parse_checkbox_lines(hard_constraint_section)
        if strict and hc_items:
            unchecked = [item for state, item in hc_items if state.lower() != "x"]
            if unchecked:
                errors.append(f"Unchecked scorecard hard constraints: {', '.join(unchecked)}")

        weighted_scores = parse_weighted_scores(score_text)
        winner_option = parse_text_field(score_text, "Winner option:")
        winner_score = parse_number_field(score_text, "Winner weighted score:")
        runner_score = parse_number_field(score_text, "Runner-up weighted score:")
        margin = parse_number_field(score_text, "Margin:")
        override_reason = parse_text_field(score_text, "Override reason (required when margin < 0.20):")

        if strict:
            if not winner_option:
                errors.append("Missing winner option in scorecard final selection.")
            if winner_score is None:
                errors.append("Missing winner weighted score in scorecard final selection.")
            if runner_score is None:
                warnings.append("Runner-up weighted score missing.")
            if margin is None:
                warnings.append("Margin missing.")
            if winner_score is not None and winner_score < 3.5:
                errors.append(f"Winner score below threshold 3.50: {winner_score:.2f}")
            if margin is not None and margin < 0.20 and not override_reason:
                errors.append("Margin < 0.20 requires override reason.")

        if winner_option and weighted_scores:
            if winner_option not in weighted_scores:
                errors.append(f"Winner option `{winner_option}` not found in scoring table.")
            else:
                computed = weighted_scores[winner_option]
                if winner_score is not None and abs(computed - winner_score) > 0.06:
                    warnings.append(
                        f"Winner score mismatch: table={computed:.2f} final={winner_score:.2f}"
                    )
                top_option = max(weighted_scores, key=weighted_scores.get)
                if strict and top_option != winner_option:
                    if not override_reason or override_reason.lower() in {"n/a", "none", "no"}:
                        errors.append(
                            f"Winner option `{winner_option}` is not top score `{top_option}` and override is missing."
                        )

        scorecard_result = {
            "path": str(scorecard_path),
            "winner_option": winner_option,
            "winner_score": winner_score,
            "scores": weighted_scores,
        }

    iteration_result: dict[str, Any] = {}
    if iter_path and iter_path.exists():
        iter_text = iter_path.read_text(encoding="utf-8")
        runs = parse_int_field(iter_text, "Total runs in window:")
        rule_section = extract_section(iter_text, "Rule Updates (1-3 only)")
        rule_count = count_nonempty_rule_updates(rule_section)

        if strict:
            if runs is None:
                errors.append("Missing `Total runs in window` in iteration log.")
            elif runs < 5:
                errors.append(f"Pilot run count below threshold 5: {runs}")
            if rule_count < 1 or rule_count > 3:
                errors.append(f"Rule update count must be 1-3, got: {rule_count}")

        gate_section = extract_section(iter_text, "Version Decision")
        gate_items = parse_checkbox_lines(gate_section)
        if strict and gate_items:
            unchecked = [item for state, item in gate_items if state.lower() != "x"]
            if unchecked:
                errors.append(f"Unchecked iteration release gate items: {', '.join(unchecked)}")

        iteration_result = {
            "path": str(iter_path),
            "total_runs": runs,
            "rule_update_count": rule_count,
        }

    return {
        "ok": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "sop_path": str(sop_path),
        "status": status,
        "scorecard": scorecard_result,
        "iteration": iteration_result,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate SOP Factory artifacts")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root path",
    )
    parser.add_argument("--sop", required=True, help="Path to SOP markdown file")
    parser.add_argument("--strict", action="store_true", help="Apply release-gate checks")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    sop_path = Path(args.sop).expanduser()
    if not sop_path.is_absolute():
        sop_path = (repo_root / sop_path).resolve()

    result = validate_sop(repo_root=repo_root, sop_path=sop_path, strict=args.strict)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"SOP: {result['sop_path']}")
        print(f"Status: {result['status'] or 'unknown'}")
        if result["errors"]:
            print("Errors:")
            for err in result["errors"]:
                print(f"- {err}")
        else:
            print("Errors: none")
        if result["warnings"]:
            print("Warnings:")
            for warn in result["warnings"]:
                print(f"- {warn}")
        else:
            print("Warnings: none")
        print("OK" if result["ok"] else "NOT OK")

    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
