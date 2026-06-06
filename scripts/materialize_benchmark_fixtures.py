from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "benchmark"
REPOS = BENCHMARK / "repos"
TASKS = BENCHMARK / "tasks.jsonl"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def python_grader(body: str) -> str:
    preamble = """
    import importlib
    import subprocess
    import sys
    from pathlib import Path

    ROOT = Path.cwd()
    sys.path.insert(0, str(ROOT / "src"))


    def run_visible_tests():
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        if result.returncode != 0:
            print(result.stdout)
            raise SystemExit(result.returncode)
    """
    return textwrap.dedent(preamble).lstrip() + "\n\n" + textwrap.dedent(body).strip() + "\n"


def node_package(extra_scripts: dict[str, str] | None = None) -> str:
    scripts = {"test": "node --test tests/*.test.mjs"}
    if extra_scripts:
        scripts.update(extra_scripts)
    return json.dumps({"type": "module", "scripts": scripts}, indent=2) + "\n"


def node_grader(body: str) -> str:
    preamble = """
    import assert from 'node:assert/strict';
    import { spawnSync } from 'node:child_process';
    import { pathToFileURL } from 'node:url';
    import path from 'node:path';
    import fs from 'node:fs';

    const root = process.cwd();

    function run(command, args) {
      const result = spawnSync(command, args, { cwd: root, encoding: 'utf8' });
      if (result.status !== 0) {
        process.stdout.write(result.stdout || '');
        process.stdout.write(result.stderr || '');
        process.exit(result.status || 1);
      }
    }

    async function loadModule(relPath) {
      return import(pathToFileURL(path.join(root, relPath)).href + `?v=${Date.now()}`);
    }
    """
    return textwrap.dedent(preamble).lstrip() + "\n\n" + textwrap.dedent(body).strip() + "\n"


TASK_DEFS = [
    {
        "task_id": "CT-001",
        "category": "bug_fix",
        "repo_hint": "python/toy_calc",
        "instruction": "Fix an off-by-one bug in a list summation helper without changing its public API.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/calc.py": """
                def sum_prefix(items, n):
                    \"\"\"Return the sum of the first n items.\"\"\"
                    return sum(items[: n + 1])
            """,
            "tests/test_sum.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from calc import sum_prefix


                class SumPrefixTest(unittest.TestCase):
                    def test_n_is_count_not_last_index(self):
                        self.assertEqual(sum_prefix([1, 2, 3, 4], 2), 3)

                    def test_zero_items(self):
                        self.assertEqual(sum_prefix([10, 20], 0), 0)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            calc = importlib.import_module("calc")
            assert calc.sum_prefix([5, 7, 9], 3) == 21
            assert calc.sum_prefix([5, 7, 9], 1) == 5
        """),
    },
    {
        "task_id": "CT-002",
        "category": "bug_fix",
        "repo_hint": "python/toy_cart",
        "instruction": "Fix discount rounding so totals match the documented cents behavior.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/cart.py": """
                def discounted_total_cents(item_cents, discount_percent):
                    \"\"\"Apply a percentage discount and round to nearest cent, half up.\"\"\"
                    return round(sum(item_cents) * (100 - discount_percent) / 100)
            """,
            "tests/test_cart.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from cart import discounted_total_cents


                class CartTest(unittest.TestCase):
                    def test_half_cent_rounds_up(self):
                        self.assertEqual(discounted_total_cents([101], 50), 51)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            cart = importlib.import_module("cart")
            assert cart.discounted_total_cents([333, 333, 333], 15) == 849
            assert cart.discounted_total_cents([101], 50) == 51
        """),
    },
    {
        "task_id": "CT-003",
        "category": "bug_fix",
        "repo_hint": "python/date_utils",
        "instruction": "Fix timezone parsing for ISO strings that end with Z.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/date_utils.py": """
                from datetime import datetime


                def parse_iso_datetime(value):
                    return datetime.fromisoformat(value)
            """,
            "tests/test_dates.py": """
                import sys
                import unittest
                from datetime import timezone
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from date_utils import parse_iso_datetime


                class DateTest(unittest.TestCase):
                    def test_z_suffix_is_utc(self):
                        parsed = parse_iso_datetime("2026-06-05T12:30:00Z")
                        self.assertEqual(parsed.tzinfo, timezone.utc)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            date_utils = importlib.import_module("date_utils")
            parsed = date_utils.parse_iso_datetime("2026-01-02T03:04:05Z")
            assert parsed.utcoffset().total_seconds() == 0
            assert date_utils.parse_iso_datetime("2026-01-02T03:04:05+02:00").utcoffset().total_seconds() == 7200
        """),
    },
    {
        "task_id": "CT-004",
        "category": "bug_fix",
        "repo_hint": "typescript/todo_store",
        "instruction": "Fix a reducer bug that drops existing todo metadata when toggling completion.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/todoStore.mjs": """
                export function reducer(state, action) {
                  if (action.type !== 'toggle') return state;
                  return {
                    ...state,
                    todos: state.todos.map((todo) =>
                      todo.id === action.id
                        ? { id: todo.id, title: todo.title, completed: !todo.completed }
                        : todo
                    ),
                  };
                }
            """,
            "tests/todo-store.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { reducer } from '../src/todoStore.mjs';

                test('toggle preserves metadata', () => {
                  const state = { todos: [{ id: 'a', title: 'Ship', completed: false, priority: 'high' }] };
                  const next = reducer(state, { type: 'toggle', id: 'a' });
                  assert.equal(next.todos[0].priority, 'high');
                  assert.equal(next.todos[0].completed, true);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { reducer } = await loadModule('src/todoStore.mjs');
            const state = { todos: [{ id: 'x', title: 'One', completed: true, tags: ['work'], due: 'today' }] };
            const next = reducer(state, { type: 'toggle', id: 'x' });
            assert.deepEqual(next.todos[0].tags, ['work']);
            assert.equal(next.todos[0].due, 'today');
            assert.equal(next.todos[0].completed, false);
        """),
    },
    {
        "task_id": "CT-005",
        "category": "bug_fix",
        "repo_hint": "typescript/url_parser",
        "instruction": "Fix query parsing so repeated keys are preserved as arrays.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/urlParser.mjs": """
                export function parseQuery(query) {
                  const clean = query.startsWith('?') ? query.slice(1) : query;
                  const result = {};
                  for (const part of clean.split('&')) {
                    if (!part) continue;
                    const [rawKey, rawValue = ''] = part.split('=');
                    result[decodeURIComponent(rawKey)] = decodeURIComponent(rawValue);
                  }
                  return result;
                }
            """,
            "tests/url-parser.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { parseQuery } from '../src/urlParser.mjs';

                test('preserves repeated keys', () => {
                  assert.deepEqual(parseQuery('?tag=a&tag=b'), { tag: ['a', 'b'] });
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { parseQuery } = await loadModule('src/urlParser.mjs');
            assert.deepEqual(parseQuery('?tag=a&tag=b&sort=asc'), { tag: ['a', 'b'], sort: 'asc' });
            assert.deepEqual(parseQuery('q=hello%20world&q=bye'), { q: ['hello world', 'bye'] });
        """),
    },
    {
        "task_id": "CT-006",
        "category": "feature",
        "repo_hint": "python/text_stats",
        "instruction": "Add a word-frequency function that ignores case and punctuation.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/text_stats.py": """
                def word_frequency(text):
                    words = text.split()
                    return {word: words.count(word) for word in words}
            """,
            "tests/test_text_stats.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from text_stats import word_frequency


                class TextStatsTest(unittest.TestCase):
                    def test_case_and_punctuation(self):
                        self.assertEqual(word_frequency("Hello, hello world!"), {"hello": 2, "world": 1})


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            text_stats = importlib.import_module("text_stats")
            assert text_stats.word_frequency("A a, b; B? c.") == {"a": 2, "b": 2, "c": 1}
        """),
    },
    {
        "task_id": "CT-007",
        "category": "feature",
        "repo_hint": "python/config_loader",
        "instruction": "Add environment-variable override support for a JSON config loader.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/config_loader.py": """
                import json


                def load_config(path, environ=None):
                    with open(path, "r", encoding="utf-8") as handle:
                        return json.load(handle)
            """,
            "tests/test_config_loader.py": """
                import json
                import sys
                import tempfile
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from config_loader import load_config


                class ConfigLoaderTest(unittest.TestCase):
                    def test_environment_override(self):
                        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
                            json.dump({"port": 8000, "debug": False}, handle)
                            path = handle.name
                        self.assertEqual(load_config(path, {"APP_PORT": "9000"})["port"], 9000)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            import json
            import tempfile
            run_visible_tests()
            loader = importlib.import_module("config_loader")
            with tempfile.NamedTemporaryFile("w", delete=False) as handle:
                json.dump({"port": 8000, "debug": False, "name": "local"}, handle)
                path = handle.name
            loaded = loader.load_config(path, {"APP_PORT": "7000", "APP_DEBUG": "true", "APP_NAME": "prod"})
            assert loaded == {"port": 7000, "debug": True, "name": "prod"}
        """),
    },
    {
        "task_id": "CT-008",
        "category": "feature",
        "repo_hint": "typescript/color_utils",
        "instruction": "Add hex-to-rgb conversion with validation errors for malformed input.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/colorUtils.mjs": """
                export function hexToRgb(hex) {
                  const clean = hex.replace('#', '');
                  return {
                    r: parseInt(clean.slice(0, 2), 16),
                    g: parseInt(clean.slice(2, 4), 16),
                    b: parseInt(clean.slice(4, 6), 16),
                  };
                }
            """,
            "tests/color-utils.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { hexToRgb } from '../src/colorUtils.mjs';

                test('converts valid hex', () => {
                  assert.deepEqual(hexToRgb('#0a1b2c'), { r: 10, g: 27, b: 44 });
                });

                test('rejects malformed input', () => {
                  assert.throws(() => hexToRgb('#xyz'), /invalid/i);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { hexToRgb } = await loadModule('src/colorUtils.mjs');
            assert.deepEqual(hexToRgb('ffffff'), { r: 255, g: 255, b: 255 });
            assert.throws(() => hexToRgb('#1234'), /invalid/i);
        """),
    },
    {
        "task_id": "CT-009",
        "category": "feature",
        "repo_hint": "python/rate_limiter",
        "instruction": "Add a sliding-window allowlist check to the rate limiter.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/rate_limiter.py": """
                class SlidingWindowLimiter:
                    def __init__(self, limit, window_seconds, allowlist=None):
                        self.limit = limit
                        self.window_seconds = window_seconds
                        self.allowlist = set(allowlist or [])
                        self.events = {}

                    def allow(self, user_id, timestamp):
                        events = [
                            t for t in self.events.get(user_id, [])
                            if timestamp - t < self.window_seconds
                        ]
                        allowed = len(events) < self.limit
                        if allowed:
                            events.append(timestamp)
                        self.events[user_id] = events
                        return allowed
            """,
            "tests/test_rate_limiter.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from rate_limiter import SlidingWindowLimiter


                class RateLimiterTest(unittest.TestCase):
                    def test_allowlisted_user_bypasses_limit(self):
                        limiter = SlidingWindowLimiter(1, 60, allowlist={"admin"})
                        self.assertTrue(limiter.allow("admin", 1))
                        self.assertTrue(limiter.allow("admin", 2))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            mod = importlib.import_module("rate_limiter")
            limiter = mod.SlidingWindowLimiter(2, 10, allowlist={"vip"})
            assert all(limiter.allow("vip", t) for t in range(5))
            assert limiter.allow("user", 1)
            assert limiter.allow("user", 2)
            assert not limiter.allow("user", 3)
        """),
    },
    {
        "task_id": "CT-010",
        "category": "feature",
        "repo_hint": "typescript/markdown_links",
        "instruction": "Add extraction of markdown links while ignoring image links.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/markdownLinks.mjs": """
                export function extractLinks(markdown) {
                  const matches = [...markdown.matchAll(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g)];
                  return matches.map((match) => ({ text: match[1], href: match[2] }));
                }
            """,
            "tests/markdown-links.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { extractLinks } from '../src/markdownLinks.mjs';

                test('ignores image links', () => {
                  assert.deepEqual(extractLinks('![logo](logo.png) [docs](https://x.test)'), [
                    { text: 'docs', href: 'https://x.test' },
                  ]);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { extractLinks } = await loadModule('src/markdownLinks.mjs');
            assert.deepEqual(extractLinks('[a](/a) ![b](/b.png) [c](/c)'), [
              { text: 'a', href: '/a' },
              { text: 'c', href: '/c' },
            ]);
        """),
    },
    {
        "task_id": "CT-011",
        "category": "test_writing",
        "repo_hint": "python/email_validator",
        "instruction": "Add regression tests for uppercase domains and plus-addressing.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/email_validator.py": """
                import re


                EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$")


                def is_valid_email(value):
                    return bool(EMAIL_RE.match(value))
            """,
            "tests/test_email_validator.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from email_validator import is_valid_email


                class EmailValidatorTest(unittest.TestCase):
                    def test_basic_email(self):
                        self.assertTrue(is_valid_email("person@example.com"))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            test_source = (ROOT / "tests" / "test_email_validator.py").read_text(encoding="utf-8")
            assert "+" in test_source, "missing plus-addressing regression test"
            assert "EXAMPLE.COM" in test_source or "Example.COM" in test_source or "uppercase" in test_source.lower()
        """),
    },
    {
        "task_id": "CT-012",
        "category": "test_writing",
        "repo_hint": "typescript/debounce",
        "instruction": "Add tests for leading-edge debounce behavior without changing implementation.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/debounce.mjs": """
                export function debounce(fn, delayMs, options = {}) {
                  let timer = null;
                  return (...args) => {
                    const shouldCallNow = options.leading && timer === null;
                    clearTimeout(timer);
                    timer = setTimeout(() => {
                      timer = null;
                      if (!options.leading) fn(...args);
                    }, delayMs);
                    if (shouldCallNow) fn(...args);
                  };
                }
            """,
            "tests/debounce.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { debounce } from '../src/debounce.mjs';

                test('debounced function waits before trailing call', async () => {
                  let count = 0;
                  const fn = debounce(() => { count += 1; }, 5);
                  fn();
                  assert.equal(count, 0);
                  await new Promise((resolve) => setTimeout(resolve, 10));
                  assert.equal(count, 1);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const testSource = fs.readFileSync(path.join(root, 'tests/debounce.test.mjs'), 'utf8');
            assert.match(testSource, /leading/i);
            assert.match(testSource, /equal\\(count,\\s*1\\)/);
        """),
    },
    {
        "task_id": "CT-013",
        "category": "test_writing",
        "repo_hint": "python/cache",
        "instruction": "Add tests proving expired cache entries are removed lazily on read.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/cache.py": """
                class TTLCache:
                    def __init__(self, now):
                        self.now = now
                        self._items = {}

                    def set(self, key, value, ttl):
                        self._items[key] = (value, self.now() + ttl)

                    def get(self, key):
                        if key not in self._items:
                            return None
                        value, expires_at = self._items[key]
                        if self.now() >= expires_at:
                            del self._items[key]
                            return None
                        return value
            """,
            "tests/test_cache.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from cache import TTLCache


                class CacheTest(unittest.TestCase):
                    def test_hit_before_expiry(self):
                        now = [10]
                        cache = TTLCache(lambda: now[0])
                        cache.set("a", 1, ttl=5)
                        self.assertEqual(cache.get("a"), 1)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            test_source = (ROOT / "tests" / "test_cache.py").read_text(encoding="utf-8").lower()
            assert "expired" in test_source or "expiry" in test_source
            assert "_items" in test_source, "test should prove lazy removal from the backing store"
        """),
    },
    {
        "task_id": "CT-014",
        "category": "test_writing",
        "repo_hint": "typescript/table_sort",
        "instruction": "Add tests for stable sort when rows have equal keys.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/tableSort.mjs": """
                export function sortRows(rows, key) {
                  return [...rows].sort((a, b) => {
                    if (a[key] < b[key]) return -1;
                    if (a[key] > b[key]) return 1;
                    return 0;
                  });
                }
            """,
            "tests/table-sort.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { sortRows } from '../src/tableSort.mjs';

                test('sorts rows by key', () => {
                  assert.deepEqual(sortRows([{ n: 2 }, { n: 1 }], 'n'), [{ n: 1 }, { n: 2 }]);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const testSource = fs.readFileSync(path.join(root, 'tests/table-sort.test.mjs'), 'utf8');
            assert.match(testSource, /stable|equal/i);
            assert.match(testSource, /id|original|order/i);
        """),
    },
    {
        "task_id": "CT-015",
        "category": "test_writing",
        "repo_hint": "python/password_policy",
        "instruction": "Add tests for minimum length, digit, and symbol validation errors.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/password_policy.py": """
                def validation_errors(password):
                    errors = []
                    if len(password) < 12:
                        errors.append("minimum length")
                    if not any(char.isdigit() for char in password):
                        errors.append("digit required")
                    if not any(not char.isalnum() for char in password):
                        errors.append("symbol required")
                    return errors
            """,
            "tests/test_password_policy.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from password_policy import validation_errors


                class PasswordPolicyTest(unittest.TestCase):
                    def test_valid_password(self):
                        self.assertEqual(validation_errors("VeryGood123!"), [])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            test_source = (ROOT / "tests" / "test_password_policy.py").read_text(encoding="utf-8").lower()
            for word in ("length", "digit", "symbol"):
                assert word in test_source, f"missing test for {word}"
        """),
    },
    {
        "task_id": "CT-016",
        "category": "refactor",
        "repo_hint": "python/csv_importer",
        "instruction": "Refactor duplicated row-validation logic into a helper while preserving behavior.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/csv_importer.py": """
                def import_users(rows):
                    users = []
                    for row in rows:
                        if not row.get("name"):
                            raise ValueError("missing name")
                        if "@" not in row.get("email", ""):
                            raise ValueError("invalid email")
                        users.append({"name": row["name"], "email": row["email"]})
                    return users


                def import_admins(rows):
                    admins = []
                    for row in rows:
                        if not row.get("name"):
                            raise ValueError("missing name")
                        if "@" not in row.get("email", ""):
                            raise ValueError("invalid email")
                        admins.append({"name": row["name"], "email": row["email"], "role": "admin"})
                    return admins
            """,
            "tests/test_csv_importer.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from csv_importer import import_admins, import_users


                class CsvImporterTest(unittest.TestCase):
                    def test_imports_users_and_admins(self):
                        row = {"name": "Aubrey", "email": "a@example.com"}
                        self.assertEqual(import_users([row])[0]["name"], "Aubrey")
                        self.assertEqual(import_admins([row])[0]["role"], "admin")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            source = (ROOT / "src" / "csv_importer.py").read_text(encoding="utf-8")
            assert "def validate_row" in source or "def _validate_row" in source
            assert source.count("missing name") == 1
            assert source.count("invalid email") == 1
        """),
    },
    {
        "task_id": "CT-017",
        "category": "refactor",
        "repo_hint": "typescript/form_state",
        "instruction": "Refactor nested conditionals in form validation without changing error messages.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/formState.mjs": """
                export function validateForm(values) {
                  const errors = {};
                  if (values.name !== undefined) {
                    if (values.name.trim() === '') {
                      errors.name = 'Name is required';
                    }
                  } else {
                    errors.name = 'Name is required';
                  }
                  if (values.email !== undefined) {
                    if (!values.email.includes('@')) {
                      errors.email = 'Email is invalid';
                    }
                  } else {
                    errors.email = 'Email is invalid';
                  }
                  return errors;
                }
            """,
            "tests/form-state.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { validateForm } from '../src/formState.mjs';

                test('keeps validation messages', () => {
                  assert.deepEqual(validateForm({ name: '', email: 'bad' }), {
                    name: 'Name is required',
                    email: 'Email is invalid',
                  });
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const source = fs.readFileSync(path.join(root, 'src/formState.mjs'), 'utf8');
            assert.match(source, /validateField|validators|rules/);
            assert.ok((source.match(/if \\(/g) || []).length <= 3);
        """),
    },
    {
        "task_id": "CT-018",
        "category": "refactor",
        "repo_hint": "python/path_matcher",
        "instruction": "Refactor glob matching into smaller functions while keeping all tests green.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/path_matcher.py": """
                def matches_path(pattern, path):
                    pattern_parts = pattern.split("/")
                    path_parts = path.split("/")
                    if len(pattern_parts) != len(path_parts):
                        return False
                    for pattern_part, path_part in zip(pattern_parts, path_parts):
                        if pattern_part == "*":
                            continue
                        if pattern_part != path_part:
                            return False
                    return True
            """,
            "tests/test_path_matcher.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from path_matcher import matches_path


                class PathMatcherTest(unittest.TestCase):
                    def test_star_segment(self):
                        self.assertTrue(matches_path("src/*/test.py", "src/unit/test.py"))
                        self.assertFalse(matches_path("src/*/test.py", "src/unit/other.py"))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            source = (ROOT / "src" / "path_matcher.py").read_text(encoding="utf-8")
            assert "def split_pattern" in source or "def _split_pattern" in source
            assert "def segment_matches" in source or "def _segment_matches" in source
        """),
    },
    {
        "task_id": "CT-019",
        "category": "refactor",
        "repo_hint": "typescript/event_bus",
        "instruction": "Refactor listener cleanup to reduce duplication without changing subscriptions.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/eventBus.mjs": """
                export class EventBus {
                  constructor() {
                    this.listeners = new Map();
                  }

                  on(name, listener) {
                    if (!this.listeners.has(name)) this.listeners.set(name, []);
                    this.listeners.get(name).push(listener);
                    return () => {
                      const next = this.listeners.get(name).filter((item) => item !== listener);
                      this.listeners.set(name, next);
                    };
                  }

                  once(name, listener) {
                    const wrapped = (...args) => {
                      const next = this.listeners.get(name).filter((item) => item !== wrapped);
                      this.listeners.set(name, next);
                      listener(...args);
                    };
                    if (!this.listeners.has(name)) this.listeners.set(name, []);
                    this.listeners.get(name).push(wrapped);
                  }

                  emit(name, value) {
                    for (const listener of this.listeners.get(name) || []) listener(value);
                  }
                }
            """,
            "tests/event-bus.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { EventBus } from '../src/eventBus.mjs';

                test('unsubscribe removes listener', () => {
                  const bus = new EventBus();
                  let count = 0;
                  const off = bus.on('x', () => { count += 1; });
                  off();
                  bus.emit('x');
                  assert.equal(count, 0);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const source = fs.readFileSync(path.join(root, 'src/eventBus.mjs'), 'utf8');
            assert.match(source, /removeListener|unsubscribe|cleanupListener/);
            assert.ok((source.match(/filter\\(/g) || []).length <= 1);
        """),
    },
    {
        "task_id": "CT-020",
        "category": "refactor",
        "repo_hint": "python/invoice",
        "instruction": "Extract invoice tax calculation into a pure helper while preserving totals.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/invoice.py": """
                def invoice_total(items, tax_rate):
                    subtotal = sum(item["price_cents"] * item.get("quantity", 1) for item in items)
                    tax = round(subtotal * tax_rate)
                    return subtotal + tax
            """,
            "tests/test_invoice.py": """
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
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            invoice = importlib.import_module("invoice")
            assert hasattr(invoice, "calculate_tax") or hasattr(invoice, "_calculate_tax")
            assert invoice.invoice_total([{"price_cents": 333, "quantity": 3}], 0.07) == 1069
        """),
    },
    {
        "task_id": "CT-021",
        "category": "ci_failure",
        "repo_hint": "python/package_metadata",
        "instruction": "Fix the package metadata issue causing editable install to fail.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "pyproject.toml": """
                [build-system]
                requires = ["setuptools"]
                build-backend = "setuptools.build_meta"

                [project]
                name = ""
                version = "0.1.0"
            """,
            "src/package_metadata/__init__.py": """
                def package_name():
                    return "package-metadata-demo"
            """,
            "tests/test_package_metadata.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from package_metadata import package_name


                class PackageMetadataTest(unittest.TestCase):
                    def test_name(self):
                        self.assertEqual(package_name(), "package-metadata-demo")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            source = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
            assert 'name = "package-metadata-demo"' in source
        """),
    },
    {
        "task_id": "CT-022",
        "category": "ci_failure",
        "repo_hint": "typescript/vite_app",
        "instruction": "Fix the TypeScript build failure caused by missing React type declarations.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package({"build": "node scripts/build.mjs"}),
            "src/App.tsx": """
                export function App() {
                  return <main>Hello CodexTrace</main>;
                }
            """,
            "scripts/build.mjs": """
                import fs from 'node:fs';

                if (!fs.existsSync('src/react-shim.d.ts')) {
                  console.error('Cannot find React JSX type declarations');
                  process.exit(1);
                }
                const app = fs.readFileSync('src/App.tsx', 'utf8');
                if (!app.includes('<main>')) {
                  console.error('App markup missing');
                  process.exit(1);
                }
                console.log('build ok');
            """,
            "tests/app.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import fs from 'node:fs';

                test('app source exists', () => {
                  assert.ok(fs.existsSync('src/App.tsx'));
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['run', 'build']);
            assert.ok(fs.existsSync(path.join(root, 'src/react-shim.d.ts')));
            const shim = fs.readFileSync(path.join(root, 'src/react-shim.d.ts'), 'utf8');
            assert.match(shim, /JSX|IntrinsicElements|react/i);
        """),
    },
    {
        "task_id": "CT-023",
        "category": "ci_failure",
        "repo_hint": "python/lint",
        "instruction": "Fix ruff lint failures without changing runtime behavior.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/lint_target.py": """
                def normalize_name(value):
                    print("normalizing", value)
                    try:
                        return value.strip().lower()
                    except:
                        return ""
            """,
            "tests/test_lint_target.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from lint_target import normalize_name


                class LintTargetTest(unittest.TestCase):
                    def test_normalize(self):
                        self.assertEqual(normalize_name("  Aubrey "), "aubrey")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            source = (ROOT / "src" / "lint_target.py").read_text(encoding="utf-8")
            assert "print(" not in source
            assert "except:" not in source
        """),
    },
    {
        "task_id": "CT-024",
        "category": "ci_failure",
        "repo_hint": "typescript/eslint",
        "instruction": "Fix lint failures in a utility module while preserving tests.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package({"lint": "node scripts/lint.mjs"}),
            "src/format.mjs": """
                export function formatUser(user) {
                  var label = user.name == '' ? 'Anonymous' : user.name;
                  return label.trim();
                }
            """,
            "scripts/lint.mjs": """
                import fs from 'node:fs';
                const source = fs.readFileSync('src/format.mjs', 'utf8');
                if (/\\bvar\\b/.test(source)) {
                  console.error('no-var violation');
                  process.exit(1);
                }
                if (/[^=!]==[^=]/.test(source)) {
                  console.error('eqeqeq violation');
                  process.exit(1);
                }
            """,
            "tests/format.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { formatUser } from '../src/format.mjs';

                test('formats fallback user', () => {
                  assert.equal(formatUser({ name: '' }), 'Anonymous');
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['run', 'lint']);
            run('npm', ['test']);
            const source = fs.readFileSync(path.join(root, 'src/format.mjs'), 'utf8');
            assert.doesNotMatch(source, /\\bvar\\b/);
            assert.doesNotMatch(source, /[^=!]==[^=]/);
        """),
    },
    {
        "task_id": "CT-025",
        "category": "ci_failure",
        "repo_hint": "python/typing",
        "instruction": "Fix mypy errors in a small dataclass parser.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/parser_model.py": """
                from dataclasses import dataclass


                @dataclass
                class Item:
                    name: str
                    count: int


                def parse_item(data: dict[str, str]) -> Item:
                    return Item(name=data["name"], count=data["count"])
            """,
            "tests/test_parser_model.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from parser_model import parse_item


                class ParserModelTest(unittest.TestCase):
                    def test_count_is_int(self):
                        self.assertEqual(parse_item({"name": "a", "count": "2"}).count, 2)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            mod = importlib.import_module("parser_model")
            item = mod.parse_item({"name": "box", "count": "7"})
            assert item.count == 7
            assert isinstance(item.count, int)
        """),
    },
    {
        "task_id": "CT-026",
        "category": "error_localization",
        "repo_hint": "python/json_reader",
        "instruction": "Use the traceback to identify and fix a JSON decode edge case.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/json_reader.py": """
                import json


                def read_json(path):
                    with open(path, "r", encoding="utf-8") as handle:
                        return json.load(handle)
            """,
            "tests/test_json_reader.py": """
                import sys
                import tempfile
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from json_reader import read_json


                class JsonReaderTest(unittest.TestCase):
                    def test_empty_file_is_empty_object(self):
                        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
                            path = handle.name
                        self.assertEqual(read_json(path), {})


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            import tempfile
            run_visible_tests()
            reader = importlib.import_module("json_reader")
            with tempfile.NamedTemporaryFile("w", delete=False) as handle:
                handle.write("   ")
                empty_path = handle.name
            assert reader.read_json(empty_path) == {}
            with tempfile.NamedTemporaryFile("w", delete=False) as handle:
                handle.write('{"ok": true}')
                data_path = handle.name
            assert reader.read_json(data_path) == {"ok": True}
        """),
    },
    {
        "task_id": "CT-027",
        "category": "error_localization",
        "repo_hint": "typescript/api_client",
        "instruction": "Use the failing test output to fix incorrect HTTP error mapping.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/apiClient.mjs": """
                export function errorForStatus(status) {
                  if (status >= 500) return 'server_error';
                  if (status === 401) return 'unauthorized';
                  if (status === 404) return 'server_error';
                  return 'unknown_error';
                }
            """,
            "tests/api-client.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { errorForStatus } from '../src/apiClient.mjs';

                test('maps not found separately', () => {
                  assert.equal(errorForStatus(404), 'not_found');
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { errorForStatus } = await loadModule('src/apiClient.mjs');
            assert.equal(errorForStatus(500), 'server_error');
            assert.equal(errorForStatus(401), 'unauthorized');
            assert.equal(errorForStatus(404), 'not_found');
            assert.equal(errorForStatus(418), 'unknown_error');
        """),
    },
    {
        "task_id": "CT-028",
        "category": "multi_turn_change",
        "repo_hint": "python/search_index",
        "instruction": "First add prefix search; then update behavior so exact matches rank first.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/search_index.py": """
                class SearchIndex:
                    def __init__(self, terms):
                        self.terms = list(terms)

                    def search(self, query):
                        return [term for term in self.terms if query in term]
            """,
            "tests/test_search_index.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from search_index import SearchIndex


                class SearchIndexTest(unittest.TestCase):
                    def test_prefix_and_exact_ranking(self):
                        index = SearchIndex(["carpet", "car", "cart", "dog"])
                        self.assertEqual(index.search("car"), ["car", "carpet", "cart"])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            mod = importlib.import_module("search_index")
            index = mod.SearchIndex(["alpha", "alphabet", "beta", "alp"])
            assert index.search("alp") == ["alp", "alpha", "alphabet"]
            assert index.search("ph") == []
        """),
    },
    {
        "task_id": "CT-029",
        "category": "multi_turn_change",
        "repo_hint": "typescript/settings_panel",
        "instruction": "First add default theme support; then make explicit user settings override defaults.",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/settingsPanel.mjs": """
                export function resolveSettings(defaults, userSettings) {
                  return {
                    theme: 'light',
                    notifications: true,
                    ...userSettings,
                    ...defaults,
                  };
                }
            """,
            "tests/settings-panel.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { resolveSettings } from '../src/settingsPanel.mjs';

                test('user settings override defaults', () => {
                  assert.deepEqual(resolveSettings({ theme: 'dark' }, { theme: 'light' }).theme, 'light');
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { resolveSettings } = await loadModule('src/settingsPanel.mjs');
            assert.deepEqual(resolveSettings({ theme: 'dark', pageSize: 50 }, { pageSize: 20 }), {
              theme: 'dark',
              notifications: true,
              pageSize: 20,
            });
        """),
    },
    {
        "task_id": "CT-030",
        "category": "multi_turn_change",
        "repo_hint": "python/booking_rules",
        "instruction": "First fix weekend booking validation; then add an exception for admin users.",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/booking_rules.py": """
                def can_book(user, day_name):
                    if day_name.lower() in {"saturday", "sunday"}:
                        return False
                    return True
            """,
            "tests/test_booking_rules.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from booking_rules import can_book


                class BookingRulesTest(unittest.TestCase):
                    def test_admin_can_book_weekend(self):
                        self.assertTrue(can_book({"role": "admin"}, "Saturday"))

                    def test_member_cannot_book_weekend(self):
                        self.assertFalse(can_book({"role": "member"}, "Sunday"))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": python_grader("""
            run_visible_tests()
            mod = importlib.import_module("booking_rules")
            assert mod.can_book({"role": "admin"}, "Sunday")
            assert not mod.can_book({"role": "member"}, "Saturday")
            assert mod.can_book({"role": "member"}, "Monday")
        """),
    },
]


def materialize() -> None:
    if REPOS.exists():
        shutil.rmtree(REPOS)
    rows = []
    for task in TASK_DEFS:
        task_id = task["task_id"]
        repo_dir = REPOS / task_id / "repo"
        grader_dir = REPOS / task_id / "grader"
        for rel_path, content in task["files"].items():
            write(repo_dir / rel_path, content)
        grader_name = "check.mjs" if task["success_check"].startswith("node ") else "check.py"
        write(grader_dir / grader_name, task["grader"])
        rows.append({
            "task_id": task_id,
            "category": task["category"],
            "repo_hint": task["repo_hint"],
            "fixture_path": f"repos/{task_id}/repo",
            "grader_path": f"repos/{task_id}/grader",
            "instruction": task["instruction"],
            "success_check": task["success_check"],
        })
    TASKS.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


if __name__ == "__main__":
    materialize()
