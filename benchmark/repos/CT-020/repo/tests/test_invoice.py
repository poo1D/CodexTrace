import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from invoice import invoice_total


class InvoiceTest(unittest.TestCase):
    def test_total(self):
        self.assertEqual(invoice_total([{"price_cents": 1000, "quantity": 2}], 0.1), 2200)


if __name__ == "__main__":
    unittest.main()
