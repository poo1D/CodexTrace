import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from sharder import ShardError, plan_shards


class SharderTest(unittest.TestCase):
    def test_returns_requested_shards(self):
        tests = [
            {"id": "test_a", "estimated_seconds": 1},
            {"id": "test_b", "estimated_seconds": 1},
            {"id": "test_c", "estimated_seconds": 1},
        ]

        shards = plan_shards(tests, 2)

        self.assertEqual([shard["index"] for shard in shards], [0, 1])
        assigned = [test_id for shard in shards for test_id in shard["tests"]]
        self.assertEqual(sorted(assigned), ["test_a", "test_b", "test_c"])

    def test_estimated_seconds_are_summed(self):
        tests = [
            {"id": "test_a", "estimated_seconds": 2},
            {"id": "test_b", "estimated_seconds": 3},
        ]

        shards = plan_shards(tests, 1)

        self.assertEqual(shards[0]["estimated_seconds"], 5)

    def test_invalid_shard_count_raises(self):
        with self.assertRaises(ShardError):
            plan_shards([], 0)


if __name__ == "__main__":
    unittest.main()
