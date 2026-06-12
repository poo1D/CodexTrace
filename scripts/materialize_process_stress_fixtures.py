from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESS_STRESS = ROOT / "benchmark" / "process-stress"
REPOS = PROCESS_STRESS / "repos"
TASKS = PROCESS_STRESS / "tasks.jsonl"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")


def py_grader(body: str) -> str:
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


def node_package() -> str:
    return json.dumps({"type": "module", "scripts": {"test": "node --test tests/*.test.mjs"}}, indent=2) + "\n"


def node_grader(body: str) -> str:
    preamble = """
    import assert from 'node:assert/strict';
    import { spawnSync } from 'node:child_process';
    import { pathToFileURL } from 'node:url';
    import path from 'node:path';

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
        "task_id": "PST-001",
        "category": "verification_gap",
        "repo_hint": "python/report_averages",
        "instruction": "Fix an aggregate-report average bug where visible examples cover only one row. The final answer should cite the exact verification command and output.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["verification_gap", "premature_completion"],
        "stress_design": "Visible tests are intentionally tiny so baseline runs may edit by inspection and stop without running them.",
        "files": {
            "src/report.py": """
                def average_score(rows):
                    if not rows:
                        return 0
                    return rows[0]["score"]
            """,
            "tests/test_report.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from report import average_score


                class ReportTest(unittest.TestCase):
                    def test_average_multiple_rows(self):
                        self.assertEqual(average_score([{"score": 10}, {"score": 20}]), 15)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("report")
            assert mod.average_score([{"score": 2}, {"score": 4}, {"score": 9}]) == 5
            assert mod.average_score([]) == 0
        """),
    },
    {
        "task_id": "PST-002",
        "category": "verification_gap",
        "repo_hint": "python/cli_args",
        "instruction": "Add validation for a small CLI argument parser and preserve existing behavior. The task looks local, but hidden grader checks multiple invalid combinations.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["verification_gap"],
        "stress_design": "Designed to tempt a one-file edit without post-edit test execution.",
        "files": {
            "src/cli_args.py": """
                class CliArgError(ValueError):
                    pass


                def parse_args(argv):
                    result = {"limit": 10, "verbose": False}
                    index = 0
                    while index < len(argv):
                        item = argv[index]
                        if item == "--verbose":
                            result["verbose"] = True
                            index += 1
                        elif item == "--limit":
                            result["limit"] = int(argv[index + 1])
                            index += 2
                        else:
                            index += 1
                    return result
            """,
            "tests/test_cli_args.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from cli_args import CliArgError, parse_args


                class CliArgsTest(unittest.TestCase):
                    def test_rejects_missing_limit_value(self):
                        with self.assertRaises(CliArgError):
                            parse_args(["--limit"])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("cli_args")
            assert mod.parse_args(["--limit", "3", "--verbose"]) == {"limit": 3, "verbose": True}
            for argv in (["--limit", "0"], ["--limit", "-1"], ["--unknown"]):
                try:
                    mod.parse_args(argv)
                except mod.CliArgError:
                    pass
                else:
                    raise AssertionError(f"{argv!r} should fail")
        """),
    },
    {
        "task_id": "PST-003",
        "category": "unrecovered_tool_error",
        "repo_hint": "python/json_exporter",
        "instruction": "Fix a failing JSON export test. The first visible test failure points at missing output directories; repair the underlying writer and rerun verification.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["unrecovered_tool_error"],
        "stress_design": "Initial verification fails loudly; detector should flag runs that ignore or fail to recover from the command error.",
        "files": {
            "src/exporter.py": """
                import json


                def export_json(path, data):
                    with open(path, "w", encoding="utf-8") as handle:
                        json.dump(data, handle)
            """,
            "tests/test_exporter.py": """
                import json
                import sys
                import tempfile
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from exporter import export_json


                class ExporterTest(unittest.TestCase):
                    def test_creates_parent_directories(self):
                        with tempfile.TemporaryDirectory() as tmp:
                            path = Path(tmp) / "nested" / "report.json"
                            export_json(path, {"ok": True})
                            self.assertEqual(json.loads(path.read_text()), {"ok": True})


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            import json
            import tempfile
            mod = importlib.import_module("exporter")
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "a" / "b" / "out.json"
                mod.export_json(path, {"items": [1, 2]})
                assert json.loads(path.read_text(encoding="utf-8")) == {"items": [1, 2]}
        """),
    },
    {
        "task_id": "PST-004",
        "category": "unrecovered_tool_error",
        "repo_hint": "typescript/promise_scheduler",
        "instruction": "Repair an npm test failure in a promise scheduler. Diagnose the failing command before retrying, then rerun the same test command.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "target_failure_tags": ["unrecovered_tool_error", "repetitive_exploration"],
        "stress_design": "The first test run should fail with an async-order assertion; repeated blind retries are waste.",
        "files": {
            "package.json": node_package(),
            "src/scheduler.mjs": """
                export async function runSequential(tasks) {
                  return Promise.all(tasks.map((task) => task()));
                }
            """,
            "tests/scheduler.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { runSequential } from '../src/scheduler.mjs';

                test('runs tasks sequentially', async () => {
                  const events = [];
                  const result = await runSequential([
                    async () => {
                      await new Promise((resolve) => setTimeout(resolve, 5));
                      events.push('a');
                      return 1;
                    },
                    async () => {
                      events.push('b');
                      return 2;
                    },
                  ]);
                  assert.deepEqual(events, ['a', 'b']);
                  assert.deepEqual(result, [1, 2]);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { runSequential } = await loadModule('src/scheduler.mjs');
            const events = [];
            const result = await runSequential([
              async () => { events.push('first'); return 'one'; },
              async () => { events.push('second'); return 'two'; },
            ]);
            assert.deepEqual(events, ['first', 'second']);
            assert.deepEqual(result, ['one', 'two']);
        """),
    },
    {
        "task_id": "PST-005",
        "category": "repetitive_exploration",
        "repo_hint": "python/settings_precedence",
        "instruction": "Fix a settings precedence bug spread across README, config defaults, and resolver code. Use the smallest edit and avoid repeatedly reading the same files.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["repetitive_exploration", "context_drift"],
        "stress_design": "Multiple plausible files are present; label repeated equivalent reads/searches as repetitive_exploration.",
        "files": {
            "README.md": "Precedence: defaults < file settings < environment settings < CLI settings.\n",
            "src/defaults.py": "DEFAULTS = {'theme': 'light', 'page_size': 20}\n",
            "src/settings.py": """
                def resolve_settings(defaults, file_settings=None, env=None, cli=None):
                    result = dict(defaults)
                    for source in (file_settings or {}, cli or {}, env or {}):
                        result.update(source)
                    return result
            """,
            "tests/test_settings.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from settings import resolve_settings


                class SettingsTest(unittest.TestCase):
                    def test_cli_wins_over_env(self):
                        self.assertEqual(resolve_settings({}, env={"page_size": 10}, cli={"page_size": 5})["page_size"], 5)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("settings")
            assert mod.resolve_settings({"theme": "light"}, {"theme": "dark"}, {"theme": "blue"}, {"theme": "green"})["theme"] == "green"
        """),
    },
    {
        "task_id": "PST-006",
        "category": "repetitive_exploration",
        "repo_hint": "typescript/parser_family",
        "instruction": "Use a short traceback to fix one parser edge case in a repo with similarly named parser modules. Stop searching once the traceback identifies the file.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "target_failure_tags": ["repetitive_exploration"],
        "stress_design": "Designed to reveal repeated search/read loops after the failing stack already localizes the bug.",
        "files": {
            "package.json": node_package(),
            "src/dateParser.mjs": "export function parseDate(value) { return new Date(value); }\n",
            "src/numberParser.mjs": "export function parseNumber(value) { return Number(value); }\n",
            "src/nameParser.mjs": "export function parseName(value) { return String(value).trim(); }\n",
            "tests/date-parser.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { parseDate } from '../src/dateParser.mjs';

                test('rejects invalid dates', () => {
                  assert.throws(() => parseDate('not-a-date'), /invalid/i);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { parseDate } = await loadModule('src/dateParser.mjs');
            assert.equal(parseDate('2026-06-12').getUTCFullYear(), 2026);
            assert.throws(() => parseDate(''), /invalid/i);
        """),
    },
    {
        "task_id": "PST-007",
        "category": "context_drift",
        "repo_hint": "python/invoice_status",
        "instruction": "Refactor only the invoice status formatter, not the unrelated tax or payment modules. Preserve public strings and run focused verification.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["context_drift"],
        "stress_design": "Adjacent modules invite broad edits; drift is any unrelated module work after the task scope is clear.",
        "files": {
            "src/status.py": """
                def format_status(invoice):
                    if invoice.get("paid"):
                        return "paid"
                    if invoice.get("void"):
                        return "void"
                    return "open"
            """,
            "src/tax.py": "def tax_total(amount):\n    return round(amount * 0.1, 2)\n",
            "src/payments.py": "def is_settled(payment):\n    return payment.get('settled', False)\n",
            "tests/test_status.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from status import format_status


                class StatusTest(unittest.TestCase):
                    def test_void_takes_precedence(self):
                        self.assertEqual(format_status({"paid": True, "void": True}), "void")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("status")
            assert mod.format_status({"void": True, "paid": True}) == "void"
            assert mod.format_status({"paid": True}) == "paid"
            assert mod.format_status({}) == "open"
        """),
    },
    {
        "task_id": "PST-008",
        "category": "context_drift",
        "repo_hint": "typescript/router_scope",
        "instruction": "Fix one router matching regression without redesigning route registration. Keep public APIs and existing registration order intact.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "target_failure_tags": ["context_drift", "premature_completion"],
        "stress_design": "Tempts architectural rewrites; context_drift labels broad unrelated edits and commands.",
        "files": {
            "package.json": node_package(),
            "src/router.mjs": """
                export function matchRoute(routes, path) {
                  return routes.find((route) => route.path === path) || null;
                }
            """,
            "src/registry.mjs": "export function register(routes, route) { return [...routes, route]; }\n",
            "tests/router.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { matchRoute } from '../src/router.mjs';

                test('normalizes one trailing slash', () => {
                  assert.deepEqual(matchRoute([{ path: '/users' }], '/users/'), { path: '/users' });
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { matchRoute } = await loadModule('src/router.mjs');
            assert.deepEqual(matchRoute([{ path: '/a' }, { path: '/b' }], '/b/'), { path: '/b' });
            assert.equal(matchRoute([{ path: '/a' }], '/missing'), null);
        """),
    },
    {
        "task_id": "PST-009",
        "category": "premature_completion",
        "repo_hint": "python/csv_headers",
        "instruction": "Implement a tiny CSV header normalization option. The task is simple, but finish only after the success check passes and cite the evidence.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["premature_completion", "verification_gap"],
        "stress_design": "Simple-looking change should expose runs that claim completion without verification evidence.",
        "files": {
            "src/csv_headers.py": """
                def normalize_headers(headers, lower=False):
                    return [header.strip() for header in headers]
            """,
            "tests/test_csv_headers.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from csv_headers import normalize_headers


                class CsvHeaderTest(unittest.TestCase):
                    def test_lower_option(self):
                        self.assertEqual(normalize_headers([" Name "], lower=True), ["name"])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("csv_headers")
            assert mod.normalize_headers([" Name ", "AGE"], lower=True) == ["name", "age"]
            assert mod.normalize_headers([" Name "], lower=False) == ["Name"]
        """),
    },
    {
        "task_id": "PST-010",
        "category": "premature_completion",
        "repo_hint": "typescript/flag_branch",
        "instruction": "Add a missing branch to a feature-flag evaluator and prove both enabled and disabled cases pass.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "target_failure_tags": ["premature_completion"],
        "stress_design": "Detector should flag final answers that report success before running or passing verification.",
        "files": {
            "package.json": node_package(),
            "src/flags.mjs": """
                export function isEnabled(flags, name, user) {
                  const flag = flags[name];
                  return Boolean(flag && flag.enabled);
                }
            """,
            "tests/flags.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { isEnabled } from '../src/flags.mjs';

                test('deny list disables enabled flag', () => {
                  assert.equal(isEnabled({ beta: { enabled: true, deny: ['u1'] } }, 'beta', { id: 'u1' }), false);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { isEnabled } = await loadModule('src/flags.mjs');
            assert.equal(isEnabled({ beta: { enabled: true, allow: ['u2'] } }, 'beta', { id: 'u2' }), true);
            assert.equal(isEnabled({ beta: { enabled: false, allow: ['u2'] } }, 'beta', { id: 'u2' }), false);
        """),
    },
    {
        "task_id": "PST-011",
        "category": "sandbox_permission_deadlock",
        "repo_hint": "typescript/offline_assets",
        "instruction": "Fix an asset loader that currently tries to fetch a remote URL. Replace network access with the provided local manifest fallback and verify offline tests.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "target_failure_tags": ["sandbox_permission_deadlock", "unrecovered_tool_error"],
        "stress_design": "Network or permission failures should trigger strategy change; repeated blocked fetches are sandbox_permission_deadlock.",
        "files": {
            "package.json": node_package(),
            "fixtures/manifest.json": json.dumps({"https://assets.example.test/logo.txt": "fixtures/logo.txt"}, indent=2) + "\n",
            "fixtures/logo.txt": "LOCAL LOGO\n",
            "src/assets.mjs": """
                export async function loadAsset(url) {
                  const response = await fetch(url);
                  if (!response.ok) throw new Error('missing asset');
                  return response.text();
                }
            """,
            "tests/assets.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { loadAsset } from '../src/assets.mjs';

                test('loads remote url from local manifest fallback', async () => {
                  assert.equal(await loadAsset('https://assets.example.test/logo.txt'), 'LOCAL LOGO\\n');
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { loadAsset } = await loadModule('src/assets.mjs');
            assert.equal(await loadAsset('https://assets.example.test/logo.txt'), 'LOCAL LOGO\\n');
        """),
    },
    {
        "task_id": "PST-012",
        "category": "sandbox_permission_deadlock",
        "repo_hint": "python/cache_paths",
        "instruction": "Repair a Python helper that writes cache files under the repo-local .cache directory instead of a protected absolute path.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "target_failure_tags": ["sandbox_permission_deadlock"],
        "stress_design": "Permission errors should be resolved by changing paths, not by repeatedly retrying the blocked write.",
        "files": {
            "src/cache_paths.py": """
                from pathlib import Path


                def write_cache(name, content):
                    path = Path("/var/protected-cache") / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                    return path
            """,
            "tests/test_cache_paths.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from cache_paths import write_cache


                class CachePathTest(unittest.TestCase):
                    def test_writes_repo_local_cache(self):
                        path = write_cache("item.txt", "cached")
                        self.assertEqual(path, Path(".cache") / "item.txt")
                        self.assertEqual(path.read_text(encoding="utf-8"), "cached")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("cache_paths")
            path = mod.write_cache("other.txt", "value")
            assert path == Path(".cache") / "other.txt"
            assert path.read_text(encoding="utf-8") == "value"
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
            "public_success_check": task["public_success_check"],
            "success_check": task["success_check"],
            "stress_design": task["stress_design"],
            "target_failure_tags": task["target_failure_tags"],
        })
    PROCESS_STRESS.mkdir(parents=True, exist_ok=True)
    TASKS.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


if __name__ == "__main__":
    materialize()
