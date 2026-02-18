"""
Tests for Smart Context v4.3.1 upgrade artifacts.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import importlib.util
from pathlib import Path


# Ensure workspace `skills/` import path is available.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
REPO_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_SCRIPT = REPO_ROOT / "scripts" / "validate_research_artifacts.py"

_spec = importlib.util.spec_from_file_location("validate_research_artifacts", VALIDATOR_SCRIPT)
assert _spec and _spec.loader
_validator = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _validator
_spec.loader.exec_module(_validator)
validate_pack = _validator.validate_pack
validate_card = _validator.validate_card


class TestResearchArtifactValidator(unittest.TestCase):
    def _write(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_validate_pack_and_card_strict_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            pack = tmp_path / "pack.md"
            card = tmp_path / "card.md"

            self._write(
                pack,
                """
## Metadata
## Normalized Question
## Success and Stop
## Claim Map
| Claim ID | Statement | Why It Matters | Evidence Needed | Status |
|---|---|---|---|---|
| C1 | a | b | c | Supported |
| C2 | a | b | c | Supported |
| C3 | a | b | c | Supported |
## Source Table (Dual-Track)
| Source | Track (external/internal) | URL or File Ref | Authority | Date/Version | Supports Claim IDs |
|---|---|---|---|---|---|
| S1 | external | u | a | d | C1 |
| S2 | external | u | a | d | C2 |
| S3 | external | u | a | d | C3 |
| S4 | internal | f | a | d | C1 |
| S5 | internal | f | a | d | C2 |
| S6 | external | u | a | d | C3 |
## Evidence Matrix
| Claim ID | Supporting Evidence | Opposing Evidence | Caveat (scope/version) | Status |
|---|---|---|---|---|
| C1 | a | b | c | Supported |
| C2 | a | b | c | Supported |
| C3 | a | b | c | Supported |
## Certainty Grade (GRADE-like)
| Claim ID | Certainty (High/Moderate/Low/Very Low) | Reason |
|---|---|---|
| C1 | High | r |
| C2 | Moderate | r |
| C3 | High | r |
## Option Comparison (>=3 options)
| Option | Quality | Risk | Complexity | Cost/Latency | Migration Effort | Operability | Verdict |
|---|---|---|---|---|---|---|---|
| A | 1 | 1 | 1 | 1 | 1 | 1 | x |
| B | 2 | 2 | 2 | 2 | 2 | 2 | x |
| C | 3 | 3 | 3 | 3 | 3 | 3 | x |
## Recommendation
## Rollout
                """.strip(),
            )

            self._write(
                card,
                """
## One-line Conclusion
## Priority Roadmap
1. a
2. b
3. c
## KPI Gates
## Stop/rollback
## Key Evidence Index
## Internal Evidence Index
                """.strip(),
            )

            pack_result = validate_pack(pack, strict=True)
            card_result = validate_card(card)
            self.assertTrue(pack_result.ok)
            self.assertTrue(card_result.ok)

    def test_validate_pack_fail_missing_headings(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "pack.md"
            pack.write_text("## Metadata\n", encoding="utf-8")
            result = validate_pack(pack, strict=True)
            self.assertFalse(result.ok)
            self.assertTrue(any("missing_headings" in e for e in result.errors))


class TestSmartContextDigestScript(unittest.TestCase):
    def test_digest_report_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            day = "2026-02-18"
            day_dir = workspace / "90_Memory" / day
            day_dir.mkdir(parents=True, exist_ok=True)

            (day_dir / "_DAILY_INDEX.md").write_text("# today\n- #GOLD decision\n- #PAUSED session\n", encoding="utf-8")
            (day_dir / "session_1200_Test.md").write_text(
                "## 📋 总结\n- done\n```json\n{\"本次核心产出\":\"x\",\"技术要点\":[],\"代码模式\":\"\",\"决策上下文\":\"\",\"避坑记录\":\"\",\"适用场景\":\"\",\"搜索关键词\":[],\"项目关联\":\"\",\"置信度\":\"medium\"}\n```\n",
                encoding="utf-8",
            )
            (day_dir / "topic-deep-research-pack.md").write_text("x", encoding="utf-8")
            (day_dir / "topic-deep-research-card.md").write_text("x", encoding="utf-8")

            repo_root = REPO_ROOT
            script = repo_root / "scripts" / "smart_context_digest.py"
            cmd = [
                sys.executable,
                str(script),
                "--workspace",
                str(workspace),
                "--mode",
                "nightly",
                "--date",
                day,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root)
            self.assertEqual(result.returncode, 0, msg=result.stderr)

            out_dir = workspace / "logs" / "digests" / day
            self.assertTrue(out_dir.exists())
            reports = list(out_dir.glob("nightly-*.md"))
            self.assertTrue(reports)


if __name__ == "__main__":
    unittest.main(verbosity=2)
