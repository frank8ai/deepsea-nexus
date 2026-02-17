# SOP Index

## Catalog Entries
- `P0-SOP目录 v1`
  - File: `resources/sop/2026-02/2026-02-17-p0-sop-catalog.md`
  - Scope: 12 SOP
- `P1-SOP目录 v1`
  - File: `resources/sop/2026-02/2026-02-17-p1-sop-catalog.md`
  - Scope: 8 SOP
- `P2-SOP目录 v1`
  - File: `resources/sop/2026-02/2026-02-17-p2-sop-catalog.md`
  - Scope: 6 SOP
  - Acceptance: 6/6 strict pass (`python3 scripts/validate_sop_factory.py --sop <file> --strict`)

## Toolchain Iteration (Search SOP + Research SOP)
- External evidence pack:
  - `resources/sop/2026-02/2026-02-17-sop-toolchain-research-pack.md`
- Full iteration report (29 SOP):
  - `resources/sop/2026-02/2026-02-17-all-sop-toolchain-iteration-report.md`
- Per-SOP research notes:
  - `resources/sop/2026-02/research-toolchain/`
- Acceptance:
  - 29/29 strict pass (`python3 scripts/validate_sop_factory.py --sop <file> --strict`)

## System SOP Operations Upgrade
- Active SOPs:
  - `resources/sop/2026-02/2026-02-17-postmortem-writeback-sop.md`
  - `resources/sop/2026-02/2026-02-17-multi-agent-research-merge-sop.md`
- One-page execution cards:
  - `resources/sop/2026-02/2026-02-17-postmortem-writeback-quick-card.md`
  - `resources/sop/2026-02/2026-02-17-multi-agent-research-merge-quick-card.md`
- Monthly KPI dashboard:
  - Script: `scripts/generate_sop_iteration_trends.py`
  - Output: `resources/sop/2026-02/2026-02-sop-iteration-kpi-dashboard.md`

## Governance V2 Upgrade (All SOP)
- Scope:
  - 31/31 SOP upgraded with non-compensatory highest standards and 4 hard mechanisms.
- Hard mechanisms applied:
  - Lifecycle fields (`Effective condition`, `Review cycle`, `Retirement condition`)
  - `Kill Switch` table
  - Dual-track metrics (`Result metric (primary)`, `Process metric (secondary)`, replacement rule)
  - `Auto-downgrade gate` (`active -> draft` when 2 consecutive monthly degradations)
- Retrieval-friendly layer:
  - Metadata fields: `Tags`, `Primary triggers`, `Primary outputs`
  - L0/L1 assets: 31 `.abstract.md` + 31 `.overview.md`
- Acceptance:
  - 31/31 strict pass (`python3 scripts/validate_sop_factory.py --sop <file> --strict`)
