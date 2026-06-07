import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from window_join import WindowJoiner


class WindowJoinerTest(unittest.TestCase):
    def test_left_then_right_join(self):
        joiner = WindowJoiner(tolerance_ms=10)
        self.assertEqual(joiner.add_left({"id": "l1", "time": 100, "value": "L"}), [])

        emitted = joiner.add_right({"id": "r1", "time": 105, "value": "R"})

        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0][0]["id"], "l1")
        self.assertEqual(emitted[0][1]["id"], "r1")

    def test_late_event_is_counted(self):
        joiner = WindowJoiner(tolerance_ms=10)
        joiner.advance_watermark(100)

        self.assertEqual(joiner.add_left({"id": "l1", "time": 90, "value": "L"}), [])
        self.assertEqual(joiner.snapshot()["late_count"], 1)


if __name__ == "__main__":
    unittest.main()
