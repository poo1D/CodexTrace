import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from search_ranker import rank_results


class SearchRankerTest(unittest.TestCase):
    def test_more_term_matches_rank_first(self):
        docs = [
            {"id": "one", "title": "Billing", "body": "receipt", "updated_at": "2026-01-01T00:00:00Z"},
            {"id": "two", "title": "Billing invoice", "body": "refund", "updated_at": "2025-01-01T00:00:00Z"},
        ]
        self.assertEqual([doc["id"] for doc in rank_results("billing invoice", docs)], ["two", "one"])

    def test_recency_breaks_equal_relevance_ties(self):
        docs = [
            {"id": "old", "title": "Deploy notes", "body": "", "updated_at": "2025-01-01T00:00:00Z"},
            {"id": "new", "title": "Deploy notes", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
        ]
        self.assertEqual([doc["id"] for doc in rank_results("deploy", docs)], ["new", "old"])


if __name__ == "__main__":
    unittest.main()
