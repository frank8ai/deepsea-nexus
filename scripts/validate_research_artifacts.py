#!/usr/bin/env python3
"""
Validate Deep Research Pack/Card artifacts for Smart Context v4.3.1.

Usage:
  python scripts/validate_research_artifacts.py --pack <pack.md> --card <card.md> --strict
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Tuple


PACK_REQUIRED_HEADINGS = [
    "## Metadata",
    "## Normalized Question",
    "## Success and Stop",
    "## Claim Map",
    "## Source Table (Dual-Track)",
    "## Evidence Matrix",
    "## Certainty Grade (GRADE-like)",
    "## Option Comparison (>=3 options)",
    "## Recommendation",
    "## Rollout",
]

CARD_REQUIRED_HEADINGS = [
    "## One-line Conclusion",
    "## Priority Roadmap",
    "## KPI Gates",
    "## Stop/rollback",
    "## Key Evidence Index",
    "## Internal Evidence Index",
]

SUMMARY_REQUIRED_FIELDS = [
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
class ValidationResult:
    ok: bool
    errors: List[str]
    warnings: List[str]
    stats: Dict[str, int]


def _read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"file not found: {path}")
    return path.read_text(encoding="utf-8")


def _missing_headings(content: str, required_headings: List[str]) -> List[str]:
    return [heading for heading in required_headings if heading not in content]


def _count_table_rows(content: str, heading: str) -> int:
    """Return data row count for markdown table under heading."""
    pattern = re.compile(rf"{re.escape(heading)}\n(?P<body>(?:\|.*\n)+)", re.MULTILINE)
    m = pattern.search(content)
    if not m:
        return 0
    rows = []
    for line in m.group("body").splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        if re.fullmatch(r"\|[-:|\s]+\|", line):
            continue
        rows.append(line)
    if len(rows) >= 2:
        # first row is header
        return len(rows) - 1
    return 0


def _count_source_track(content: str, track: str) -> int:
    pattern = re.compile(rf"\|\s*S\d+\s*\|\s*{track}\s*\|", re.IGNORECASE)
    return len(pattern.findall(content))


def _count_claim_rows(content: str) -> int:
    return len(re.findall(r"\|\s*C\d+\s*\|", content))


def _extract_json_codeblocks(content: str) -> List[str]:
    pattern = re.compile(r"```json\s*\n([\s\S]*?)\n```", re.MULTILINE)
    return [m.strip() for m in pattern.findall(content)]


def _json_has_required_fields(json_text: str) -> Tuple[bool, List[str]]:
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError:
        return False, ["invalid_json"]
    missing = [k for k in SUMMARY_REQUIRED_FIELDS if k not in data]
    return len(missing) == 0, missing


def validate_pack(path: Path, strict: bool) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []
    stats: Dict[str, int] = {}
    content = _read_text(path)

    missing = _missing_headings(content, PACK_REQUIRED_HEADINGS)
    if missing:
        errors.append("missing_headings:" + ", ".join(missing))

    source_rows = _count_table_rows(content, "## Source Table (Dual-Track)")
    external_rows = _count_source_track(content, "external")
    internal_rows = _count_source_track(content, "internal")
    option_rows = _count_table_rows(content, "## Option Comparison (>=3 options)")
    claim_rows = _count_claim_rows(content)

    stats.update(
        {
            "source_rows": source_rows,
            "external_rows": external_rows,
            "internal_rows": internal_rows,
            "option_rows": option_rows,
            "claim_rows": claim_rows,
        }
    )

    if strict and source_rows < 6:
        errors.append(f"strict: Source Table rows must be >= 6 (got {source_rows})")
    if strict and external_rows < 3:
        errors.append(f"strict: external sources must be >= 3 (got {external_rows})")
    if strict and internal_rows < 2:
        errors.append(f"strict: internal sources must be >= 2 (got {internal_rows})")
    if option_rows < 3:
        errors.append(f"Option rows must be >= 3 (got {option_rows})")
    if claim_rows < 3:
        errors.append(f"Claim rows must be >= 3 (got {claim_rows})")

    json_blocks = _extract_json_codeblocks(content)
    stats["json_blocks"] = len(json_blocks)
    if json_blocks:
        # optional warning for malformed blocks
        valid_block = False
        for block in json_blocks:
            ok, missing_fields = _json_has_required_fields(block)
            if ok:
                valid_block = True
                break
            if missing_fields != ["invalid_json"]:
                warnings.append("json_block_missing_fields:" + ",".join(missing_fields))
        if not valid_block:
            warnings.append("no_json_block_contains_full_structured_summary_v3_1_fields")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings, stats=stats)


def validate_card(path: Path) -> ValidationResult:
    errors: List[str] = []
    warnings: List[str] = []
    stats: Dict[str, int] = {}
    content = _read_text(path)

    missing = _missing_headings(content, CARD_REQUIRED_HEADINGS)
    if missing:
        errors.append("missing_headings:" + ", ".join(missing))

    roadmap_items = len(re.findall(r"^\d+\.\s+", content, flags=re.MULTILINE))
    stats["roadmap_items"] = roadmap_items
    if roadmap_items < 3:
        warnings.append(f"Priority roadmap items < 3 (got {roadmap_items})")

    return ValidationResult(ok=not errors, errors=errors, warnings=warnings, stats=stats)


def _print_result(kind: str, result: ValidationResult) -> None:
    status = "PASS" if result.ok else "FAIL"
    print(f"[{kind}] {status}")
    if result.errors:
        for item in result.errors:
            print(f"  error: {item}")
    if result.warnings:
        for item in result.warnings:
            print(f"  warn: {item}")
    if result.stats:
        print(f"  stats: {result.stats}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Deep Research Pack/Card artifacts")
    parser.add_argument("--pack", required=True, help="Path to deep research pack markdown")
    parser.add_argument("--card", required=True, help="Path to deep research card markdown")
    parser.add_argument("--strict", action="store_true", help="Enable strict dual-track thresholds")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args()

    pack_path = Path(args.pack).expanduser().resolve()
    card_path = Path(args.card).expanduser().resolve()

    pack_result = validate_pack(pack_path, strict=args.strict)
    card_result = validate_card(card_path)
    ok = pack_result.ok and card_result.ok

    if args.json:
        payload = {
            "ok": ok,
            "pack": asdict(pack_result),
            "card": asdict(card_result),
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        _print_result("PACK", pack_result)
        _print_result("CARD", card_result)
        print("OVERALL: PASS" if ok else "OVERALL: FAIL")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
