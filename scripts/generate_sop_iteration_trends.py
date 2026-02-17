#!/usr/bin/env python3
"""Generate monthly KPI trend dashboard from SOP iteration logs."""

from __future__ import annotations

import argparse
import datetime as dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


METRIC_ALIASES = {
    "cycle_time": ("cycle time",),
    "first_pass_yield": ("first-pass yield", "first pass yield"),
    "rework_rate": ("rework rate",),
}

METRIC_LABELS = {
    "cycle_time": "Cycle Time",
    "first_pass_yield": "First-pass Yield",
    "rework_rate": "Rework Rate",
}

METRIC_UNITS = {
    "cycle_time": "minutes",
    "first_pass_yield": "percent",
    "rework_rate": "percent",
}

METRIC_DIRECTIONS = {
    "cycle_time": "lower_better",
    "first_pass_yield": "higher_better",
    "rework_rate": "lower_better",
}


@dataclass
class MetricRecord:
    metric_id: str
    sop_name: str
    log_path: str
    baseline: float
    current: float
    status: str

    @property
    def delta(self) -> float:
        return self.current - self.baseline

    @property
    def improvement(self) -> float:
        direction = METRIC_DIRECTIONS[self.metric_id]
        if direction == "lower_better":
            return self.baseline - self.current
        return self.current - self.baseline


def normalize_metric(raw: str) -> str | None:
    text = raw.strip().lower()
    for metric_id, aliases in METRIC_ALIASES.items():
        if any(alias in text for alias in aliases):
            return metric_id
    return None


def first_number(value: str) -> float | None:
    m = re.search(r"-?\d+(?:\.\d+)?", value)
    if not m:
        return None
    return float(m.group(0))


def parse_sop_name(text: str) -> str:
    m = re.search(r"^- SOP Name:\s*(.+)$", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else "unknown"


def parse_table_rows(text: str) -> Iterable[tuple[str, str, str, str]]:
    pattern = re.compile(
        r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*[^|]*\|\s*[^|]*\|\s*([^|]+?)\s*\|$",
        flags=re.MULTILINE,
    )
    for m in pattern.finditer(text):
        metric_name = m.group(1).strip()
        baseline = m.group(2).strip()
        current = m.group(3).strip()
        status = m.group(4).strip().lower()
        yield metric_name, baseline, current, status


def parse_iteration_log(path: Path, repo_root: Path) -> list[MetricRecord]:
    text = path.read_text(encoding="utf-8")
    sop_name = parse_sop_name(text)
    rel_path = str(path.resolve().relative_to(repo_root))
    out: list[MetricRecord] = []
    for metric_name, baseline_raw, current_raw, status in parse_table_rows(text):
        metric_id = normalize_metric(metric_name)
        if not metric_id:
            continue
        baseline = first_number(baseline_raw)
        current = first_number(current_raw)
        if baseline is None or current is None:
            continue
        out.append(
            MetricRecord(
                metric_id=metric_id,
                sop_name=sop_name,
                log_path=rel_path,
                baseline=baseline,
                current=current,
                status=status,
            )
        )
    return out


def average(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def pass_rate(records: list[MetricRecord]) -> float:
    if not records:
        return 0.0
    passed = sum(1 for r in records if "pass" in r.status)
    return 100.0 * passed / len(records)


def percent_bar(score: float, width: int = 20) -> str:
    clamped = max(0.0, min(100.0, score))
    filled = int(round((clamped / 100.0) * width))
    return "#" * filled + "." * (width - filled)


def performance_score(record: MetricRecord, values: list[float]) -> float:
    if not values:
        return 0.0
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < 1e-9:
        return 100.0
    if METRIC_DIRECTIONS[record.metric_id] == "lower_better":
        normalized = (hi - record.current) / (hi - lo)
    else:
        normalized = (record.current - lo) / (hi - lo)
    return max(0.0, min(1.0, normalized)) * 100.0


def metric_summary(metric_id: str, records: list[MetricRecord]) -> dict[str, float]:
    baselines = [r.baseline for r in records]
    currents = [r.current for r in records]
    improvements = [r.improvement for r in records]
    return {
        "samples": float(len(records)),
        "baseline_avg": average(baselines),
        "current_avg": average(currents),
        "improvement_avg": average(improvements),
        "pass_rate": pass_rate(records),
    }


def render_dashboard(month: str, records: list[MetricRecord], repo_root: Path) -> str:
    generated = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_count = len(list((repo_root / "resources" / "sop" / month).glob("*-iteration-log.md")))
    metrics = {m: [r for r in records if r.metric_id == m] for m in METRIC_ALIASES}

    lines: list[str] = []
    lines.append("# SOP Iteration KPI Dashboard")
    lines.append("")
    lines.append(f"- Month: {month}")
    lines.append(f"- Generated on: {generated}")
    lines.append(f"- Iteration logs scanned: {log_count}")
    lines.append(f"- Metric records parsed: {len(records)}")
    lines.append("")
    lines.append("## KPI Summary")
    lines.append("| Metric | Samples | Baseline Avg | Current Avg | Improvement Avg | Pass Rate |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for metric_id in ("cycle_time", "first_pass_yield", "rework_rate"):
        group = metrics[metric_id]
        if not group:
            continue
        summary = metric_summary(metric_id, group)
        unit = METRIC_UNITS[metric_id]
        unit_suffix = "m" if unit == "minutes" else "%"
        lines.append(
            "| {label} | {samples:.0f} | {b:.2f}{u} | {c:.2f}{u} | {imp:+.2f}{u} | {pr:.1f}% |".format(
                label=METRIC_LABELS[metric_id],
                samples=summary["samples"],
                b=summary["baseline_avg"],
                c=summary["current_avg"],
                imp=summary["improvement_avg"],
                u=unit_suffix,
                pr=summary["pass_rate"],
            )
        )

    lines.append("")
    lines.append("## Trend Details")
    for metric_id in ("cycle_time", "first_pass_yield", "rework_rate"):
        group = metrics[metric_id]
        if not group:
            continue
        direction = "Lower is better" if METRIC_DIRECTIONS[metric_id] == "lower_better" else "Higher is better"
        unit = "m" if METRIC_UNITS[metric_id] == "minutes" else "%"
        values = [r.current for r in group]
        lines.append(f"### {METRIC_LABELS[metric_id]} ({direction})")
        lines.append("| SOP | Baseline | Current | Improvement | Status | Score |")
        lines.append("|---|---:|---:|---:|---|---|")
        sorted_group = sorted(group, key=lambda x: x.improvement, reverse=True)
        for record in sorted_group:
            score = performance_score(record, values)
            bar = percent_bar(score)
            lines.append(
                "| {name} | {b:.2f}{u} | {c:.2f}{u} | {i:+.2f}{u} | {status} | `{bar}` {score:.1f}% |".format(
                    name=record.sop_name,
                    b=record.baseline,
                    c=record.current,
                    i=record.improvement,
                    u=unit,
                    status=record.status,
                    bar=bar,
                    score=score,
                )
            )
        lines.append("")

    lines.append("## Data Source")
    lines.append(f"- Path: `resources/sop/{month}/*-iteration-log.md`")
    lines.append("- Fields used: `Baseline vs Current` table rows for `Cycle time`, `First-pass yield`, `Rework rate`.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SOP monthly KPI trend dashboard.")
    parser.add_argument("--month", required=True, help="Month folder under resources/sop, e.g. 2026-02")
    parser.add_argument(
        "--repo-root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root path",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Optional output file path. Default: resources/sop/<month>/<month>-sop-iteration-kpi-dashboard.md",
    )
    args = parser.parse_args()

    repo_root = Path(args.repo_root).expanduser().resolve()
    month = args.month.strip()
    month_dir = repo_root / "resources" / "sop" / month
    if not month_dir.exists():
        raise SystemExit(f"Month folder does not exist: {month_dir}")

    records: list[MetricRecord] = []
    for path in sorted(month_dir.glob("*-iteration-log.md")):
        records.extend(parse_iteration_log(path, repo_root))

    report = render_dashboard(month=month, records=records, repo_root=repo_root)
    default_output = repo_root / "resources" / "sop" / month / f"{month}-sop-iteration-kpi-dashboard.md"
    output_path = Path(args.output).expanduser().resolve() if args.output else default_output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Generated dashboard: {output_path}")
    print(f"Metric records: {len(records)}")


if __name__ == "__main__":
    main()

