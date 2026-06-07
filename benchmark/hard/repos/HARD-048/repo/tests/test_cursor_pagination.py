import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cursor_pagination import CursorError, list_page


class CursorPaginationTest(unittest.TestCase):
    def test_first_page_descending(self):
        items = [
            {"id": "a", "created_at": 10},
            {"id": "b", "created_at": 30},
            {"id": "c", "created_at": 20},
        ]

        page = list_page(items, 2)

        self.assertEqual([item["id"] for item in page.items], ["b", "c"])
        self.assertIsNotNone(page.next_cursor)

    def test_next_page_uses_cursor(self):
        items = [
            {"id": "a", "created_at": 10},
            {"id": "b", "created_at": 30},
            {"id": "c", "created_at": 20},
        ]

        first = list_page(items, 1)
        second = list_page(items, 2, first.next_cursor)

        self.assertEqual([item["id"] for item in second.items], ["c", "a"])
        self.assertIsNone(second.next_cursor)

    def test_bad_cursor_raises(self):
        with self.assertRaises(CursorError):
            list_page([], 10, "not-a-valid-cursor")


if __name__ == "__main__":
    unittest.main()
