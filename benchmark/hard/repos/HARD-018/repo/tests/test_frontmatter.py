import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import frontmatter


class FrontmatterTest(unittest.TestCase):
    def test_simple_frontmatter(self):
        metadata, body = frontmatter.parse_frontmatter("---\ntitle: Hello\n---\nBody\n")
        self.assertEqual(metadata, {"title": "Hello"})
        self.assertEqual(body, "Body\n")

    def test_missing_closing_delimiter_raises_domain_error(self):
        with self.assertRaises(frontmatter.FrontmatterError) as ctx:
            frontmatter.parse_frontmatter("---\ntitle: Hello\nBody\n")
        self.assertIn("closing", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
