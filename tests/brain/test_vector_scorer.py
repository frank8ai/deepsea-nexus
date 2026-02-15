import unittest

from deepsea_nexus.brain.models import BrainRecord
from deepsea_nexus.brain.vector_scorer import VectorScorer


class TestVectorScorer(unittest.TestCase):
    def test_vector_scorer_orders_more_similar_higher(self):
        scorer = VectorScorer(dim=128)

        r1 = BrainRecord(id="1", kind="fact", priority="P1", source="t", tags=["python"], content="JSONL append only storage")
        r2 = BrainRecord(id="2", kind="fact", priority="P1", source="t", tags=["go"], content="Kubernetes controllers reconcile loops")

        s1 = scorer.score("jsonl storage", r1, mode="facts")
        s2 = scorer.score("jsonl storage", r2, mode="facts")

        self.assertGreaterEqual(s1, s2)

    def test_vector_scorer_empty_query(self):
        scorer = VectorScorer()
        r = BrainRecord(id="1", kind="fact", priority="P1", source="t", content="anything")
        self.assertEqual(scorer.score(" ", r, mode="facts"), 0.0)


if __name__ == "__main__":
    unittest.main()
