import tempfile
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT.parent
if str(SKILLS) not in sys.path:
    sys.path.insert(0, str(SKILLS))

from deepsea_nexus.brain.api import configure_brain, brain_write, brain_retrieve, checkpoint, rollback, backfill_embeddings
from deepsea_nexus.brain.vector_scorer import VectorScorer


class TestBrainIntegration(unittest.TestCase):
    def test_write_attaches_embedding_when_vector_enabled(self):
        class _FakeEmb:
            def __init__(self, vec):
                self._vec = vec

            def tolist(self):
                return list(self._vec)

        class _FakeModel:
            def encode(self, texts, normalize_embeddings=True):
                return [_FakeEmb([0.1, 0.2, 0.3])]

        with tempfile.TemporaryDirectory() as td:
            scorer = VectorScorer(dim=3, use_sentence_transformers=False)
            scorer._st_model = _FakeModel()
            scorer.use_sentence_transformers = True

            configure_brain(enabled=True, base_path=td, scorer=scorer)
            rec = brain_write(
                {
                    "id": "emb1",
                    "kind": "fact",
                    "priority": "P1",
                    "source": "itest",
                    "tags": ["embed"],
                    "content": "Embedding should be stored",
                }
            )
            self.assertIsNotNone(rec)
            meta = rec.metadata
            self.assertIsInstance(meta.get("embedding"), list)
            self.assertEqual(meta.get("embedding_dim"), 3)
            self.assertEqual(meta.get("embedding_kind"), "sentence-transformers")
            self.assertEqual(meta.get("embedding_hash"), rec.hash)

    def test_write_skips_embedding_when_hashed_vector(self):
        with tempfile.TemporaryDirectory() as td:
            configure_brain(enabled=True, base_path=td, scorer_type="hashed-vector")
            rec = brain_write(
                {
                    "id": "emb2",
                    "kind": "fact",
                    "priority": "P1",
                    "source": "itest",
                    "tags": ["embed"],
                    "content": "Hashed vector should not be stored",
                }
            )
            self.assertIsNotNone(rec)
            self.assertFalse("embedding" in (rec.metadata or {}))

    def test_write_then_retrieve_smoke(self):
        with tempfile.TemporaryDirectory() as td:
            configure_brain(enabled=True, base_path=td)
            brain_write(
                {
                    "id": "a1",
                    "kind": "fact",
                    "priority": "P0",
                    "source": "itest",
                    "tags": ["python", "jsonl"],
                    "content": "JSONL append is cheap and robust",
                }
            )
            brain_write(
                {
                    "id": "a2",
                    "kind": "strategy",
                    "priority": "P1",
                    "source": "itest",
                    "tags": ["pipeline"],
                    "content": "Checkpoint periodically to compact records",
                }
            )
            stats = checkpoint()

            out = brain_retrieve("jsonl robust", mode="facts", limit=3, min_score=0.1)
            self.assertTrue(len(out) >= 1)
            self.assertEqual(out[0]["kind"], "fact")

            # rollback should succeed to the last checkpoint version
            self.assertTrue(stats.get("version"))
            self.assertTrue(rollback(stats["version"]))

    def test_backfill_embeddings_appends_updates(self):
        class _FakeEmb:
            def __init__(self, vec):
                self._vec = vec

            def tolist(self):
                return list(self._vec)

        class _FakeModel:
            def encode(self, texts, normalize_embeddings=True):
                return [_FakeEmb([0.2, 0.1, 0.0])]

        with tempfile.TemporaryDirectory() as td:
            # First run with hashed-vector (no embedding stored)
            configure_brain(enabled=True, base_path=td, scorer_type="hashed-vector")
            rec = brain_write(
                {
                    "id": "bf1",
                    "kind": "fact",
                    "priority": "P1",
                    "source": "itest",
                    "content": "Backfill me",
                }
            )
            self.assertIsNotNone(rec)
            self.assertFalse("embedding" in (rec.metadata or {}))

            # Reconfigure with real vector scorer and backfill
            scorer = VectorScorer(dim=3, use_sentence_transformers=False)
            scorer._st_model = _FakeModel()
            scorer.use_sentence_transformers = True
            configure_brain(enabled=True, base_path=td, scorer=scorer)

            stats = backfill_embeddings()
            self.assertGreaterEqual(stats.get("updated", 0), 1)

            out = brain_retrieve("backfill", mode="facts", limit=3, min_score=0.0)
            self.assertTrue(any("embedding" in (r.get("metadata") or {}) for r in out))

    def test_novelty_gate_skips_duplicate_writes(self):
        with tempfile.TemporaryDirectory() as td:
            configure_brain(
                enabled=True,
                base_path=td,
                scorer_type="keyword",
                novelty_enabled=True,
                novelty_min_similarity=0.85,
                novelty_window_seconds=3600,
            )
            brain_write(
                {
                    "id": "n1",
                    "kind": "fact",
                    "priority": "P1",
                    "source": "itest",
                    "tags": ["dup"],
                    "content": "Same content should be skipped",
                }
            )
            brain_write(
                {
                    "id": "n2",
                    "kind": "fact",
                    "priority": "P1",
                    "source": "itest",
                    "tags": ["dup"],
                    "content": "Same content should be skipped",
                }
            )
            records_path = Path(td) / "brain" / "records.jsonl"
            with records_path.open("r", encoding="utf-8") as f:
                lines = [line for line in f if line.strip()]
            self.assertEqual(len(lines), 1)

            brain_write(
                {
                    "id": "n3",
                    "kind": "fact",
                    "priority": "P1",
                    "source": "itest",
                    "tags": ["uniq"],
                    "content": "Different content should be stored",
                }
            )
            with records_path.open("r", encoding="utf-8") as f:
                lines = [line for line in f if line.strip()]
            self.assertEqual(len(lines), 2)


if __name__ == "__main__":
    unittest.main()
