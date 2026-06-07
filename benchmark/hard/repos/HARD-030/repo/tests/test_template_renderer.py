import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import template_renderer


class TemplateRendererTest(unittest.TestCase):
    def test_renders_simple_placeholders(self):
        result = template_renderer.render_template(
            "Hello {name}, you have {count} messages.",
            {"name": "Ada", "count": 3},
        )
        self.assertEqual(result, "Hello Ada, you have 3 messages.")

    def test_missing_variable_raises_template_error(self):
        with self.assertRaises(template_renderer.TemplateRenderError) as ctx:
            template_renderer.render_template("Hello {name}", {})
        self.assertIn("name", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
