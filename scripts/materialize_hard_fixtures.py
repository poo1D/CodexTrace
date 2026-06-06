from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARD = ROOT / "benchmark" / "hard"
REPOS = HARD / "repos"
TASKS = HARD / "tasks.jsonl"


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
        "task_id": "HARD-001",
        "category": "bug_fix",
        "repo_hint": "python/interval_merge",
        "instruction": "Fix interval merging for half-open intervals: overlapping intervals merge, touching intervals stay separate, invalid intervals raise ValueError, and output remains sorted.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/intervals.py": """
                def merge_intervals(intervals):
                    ordered = sorted(intervals)
                    merged = []
                    for start, end in ordered:
                        if not merged or start > merged[-1][1]:
                            merged.append([start, end])
                        else:
                            merged[-1][1] = max(merged[-1][1], end)
                    return [tuple(item) for item in merged]
            """,
            "tests/test_intervals.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from intervals import merge_intervals


                class IntervalTest(unittest.TestCase):
                    def test_touching_half_open_intervals_stay_separate(self):
                        self.assertEqual(merge_intervals([(1, 3), (3, 5)]), [(1, 3), (3, 5)])

                    def test_overlap_merges(self):
                        self.assertEqual(merge_intervals([(5, 7), (1, 4), (3, 6)]), [(1, 7)])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            intervals = importlib.import_module("intervals")
            assert intervals.merge_intervals([(0, 1), (1, 2), (2, 2), (2, 3)]) == [(0, 1), (1, 2), (2, 2), (2, 3)]
            assert intervals.merge_intervals([(4, 9), (1, 5), (2, 3), (9, 10)]) == [(1, 9), (9, 10)]
            try:
                intervals.merge_intervals([(3, 1)])
            except ValueError:
                pass
            else:
                raise AssertionError("invalid interval should raise ValueError")
        """),
    },
    {
        "task_id": "HARD-002",
        "category": "bug_fix",
        "repo_hint": "python/csv_records",
        "instruction": "Fix the CSV reader so quoted commas, escaped double quotes, blank lines, and quoted newlines are parsed correctly without changing the public function.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/csv_records.py": """
                def parse_records(text):
                    rows = []
                    for line in text.splitlines():
                        if not line.strip():
                            continue
                        rows.append(line.split(","))
                    return rows
            """,
            "tests/test_csv_records.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from csv_records import parse_records


                class CsvRecordTest(unittest.TestCase):
                    def test_quoted_comma(self):
                        self.assertEqual(parse_records('name,note\\nAda,"ships, fast"'), [["name", "note"], ["Ada", "ships, fast"]])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("csv_records")
            text = "name,note\\nAda,\\\"quote \\\"\\\"inside\\\"\\\"\\\"\\n\\nGrace,\\\"line one\\nline two\\\""
            assert mod.parse_records(text) == [
                ["name", "note"],
                ["Ada", 'quote "inside"'],
                ["Grace", "line one\\nline two"],
            ]
        """),
    },
    {
        "task_id": "HARD-003",
        "category": "feature",
        "repo_hint": "python/cent_allocation",
        "instruction": "Implement fair proportional cent allocation: floor raw shares, distribute leftover cents by largest fractional remainder, keep ties stable by input order, and reject negative weights.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/allocation.py": """
                def allocate_cents(total_cents, weights):
                    total_weight = sum(weights)
                    if total_weight == 0:
                        return [0 for _ in weights]
                    return [round(total_cents * weight / total_weight) for weight in weights]
            """,
            "tests/test_allocation.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from allocation import allocate_cents


                class AllocationTest(unittest.TestCase):
                    def test_largest_remainder(self):
                        self.assertEqual(allocate_cents(10, [1, 1, 1]), [4, 3, 3])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            allocation = importlib.import_module("allocation")
            assert allocation.allocate_cents(5, [1, 1, 1, 1]) == [2, 1, 1, 1]
            assert allocation.allocate_cents(0, [5, 0, 2]) == [0, 0, 0]
            assert allocation.allocate_cents(7, [0, 3, 3]) == [0, 4, 3]
            try:
                allocation.allocate_cents(10, [1, -1])
            except ValueError:
                pass
            else:
                raise AssertionError("negative weights should raise ValueError")
        """),
    },
    {
        "task_id": "HARD-004",
        "category": "error_localization",
        "repo_hint": "python/toposort",
        "instruction": "Fix topological sorting so dependency-only nodes are included, output is stable by first appearance, and cycles raise CycleError with the cycle path.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/toposort.py": """
                class CycleError(Exception):
                    pass


                def topological_sort(graph):
                    result = []
                    seen = set()
                    for node, deps in graph.items():
                        if node in seen:
                            continue
                        seen.add(node)
                        result.extend(dep for dep in deps if dep not in seen)
                        seen.update(deps)
                        result.append(node)
                    return result
            """,
            "tests/test_toposort.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from toposort import topological_sort


                class ToposortTest(unittest.TestCase):
                    def test_dependency_only_node_is_included_before_user(self):
                        self.assertEqual(topological_sort({"app": ["core"]}), ["core", "app"])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("toposort")
            assert mod.topological_sort({"b": ["a"], "c": ["a"], "d": ["b", "c"]}) == ["a", "b", "c", "d"]
            try:
                mod.topological_sort({"a": ["b"], "b": ["c"], "c": ["a"]})
            except mod.CycleError as exc:
                text = " ".join(str(part) for part in exc.args)
                assert "a" in text and "b" in text and "c" in text
            else:
                raise AssertionError("cycle should raise CycleError")
        """),
    },
    {
        "task_id": "HARD-005",
        "category": "bug_fix",
        "repo_hint": "typescript/router",
        "instruction": "Fix route matching so it supports named params, URL decoding, wildcard rest segments, and trailing slash normalization.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/router.mjs": """
                export function matchRoute(pattern, path) {
                  if (pattern === path) return { matched: true, params: {} };
                  return { matched: false, params: {} };
                }
            """,
            "tests/router.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { matchRoute } from '../src/router.mjs';

                test('matches named params', () => {
                  assert.deepEqual(matchRoute('/users/:id', '/users/42'), { matched: true, params: { id: '42' } });
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { matchRoute } = await loadModule('src/router.mjs');
            assert.deepEqual(matchRoute('/users/:id', '/users/a%20b/'), { matched: true, params: { id: 'a b' } });
            assert.deepEqual(matchRoute('/files/*path', '/files/a/b/c.txt'), { matched: true, params: { path: 'a/b/c.txt' } });
            assert.deepEqual(matchRoute('/files/*path', '/other/a'), { matched: false, params: {} });
        """),
    },
    {
        "task_id": "HARD-006",
        "category": "feature",
        "repo_hint": "typescript/retry",
        "instruction": "Implement async retry with maxAttempts, a shouldRetry classifier, injected sleep, and stable attempt numbering passed to the operation.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/retry.mjs": """
                export async function retry(operation, options = {}) {
                  const maxAttempts = options.maxAttempts ?? 3;
                  let lastError;
                  for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
                    try {
                      return await operation();
                    } catch (error) {
                      lastError = error;
                    }
                  }
                  throw lastError;
                }
            """,
            "tests/retry.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { retry } from '../src/retry.mjs';

                test('retries until success', async () => {
                  let calls = 0;
                  const value = await retry(async () => {
                    calls += 1;
                    if (calls < 2) throw new Error('temporary');
                    return 'ok';
                  }, { maxAttempts: 3 });
                  assert.equal(value, 'ok');
                  assert.equal(calls, 2);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { retry } = await loadModule('src/retry.mjs');
            const slept = [];
            const attempts = [];
            const value = await retry(async (attempt) => {
              attempts.push(attempt);
              if (attempt < 3) throw Object.assign(new Error('retryable'), { code: 'E_TEMP' });
              return 'done';
            }, {
              maxAttempts: 4,
              shouldRetry: (error) => error.code === 'E_TEMP',
              sleep: async (delayMs) => slept.push(delayMs),
              delays: [5, 10, 20],
            });
            assert.equal(value, 'done');
            assert.deepEqual(attempts, [1, 2, 3]);
            assert.deepEqual(slept, [5, 10]);
            await assert.rejects(
              retry(async () => { throw Object.assign(new Error('no'), { code: 'E_NO' }); }, {
                maxAttempts: 3,
                shouldRetry: (error) => error.code === 'E_TEMP',
                sleep: async () => {},
              }),
              /no/
            );
        """),
    },
    {
        "task_id": "HARD-007",
        "category": "refactor",
        "repo_hint": "python/config_merge",
        "instruction": "Refactor config merging into a deep merge helper: dictionaries merge recursively, lists replace, None deletes keys, and inputs must not be mutated.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/config_merge.py": """
                def merge_config(base, override):
                    result = dict(base)
                    result.update(override)
                    return result
            """,
            "tests/test_config_merge.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from config_merge import merge_config


                class ConfigMergeTest(unittest.TestCase):
                    def test_deep_dict_merge(self):
                        self.assertEqual(
                            merge_config({"db": {"host": "local", "port": 1}}, {"db": {"port": 2}}),
                            {"db": {"host": "local", "port": 2}},
                        )


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy
            run_visible_tests()
            mod = importlib.import_module("config_merge")
            base = {"db": {"host": "local", "ports": [1]}, "debug": True, "keep": "yes"}
            override = {"db": {"ports": [2, 3]}, "debug": None}
            original_base = copy.deepcopy(base)
            original_override = copy.deepcopy(override)
            assert mod.merge_config(base, override) == {"db": {"host": "local", "ports": [2, 3]}, "keep": "yes"}
            assert base == original_base
            assert override == original_override
            assert hasattr(mod, "deep_merge") or hasattr(mod, "_deep_merge")
        """),
    },
    {
        "task_id": "HARD-008",
        "category": "bug_fix",
        "repo_hint": "typescript/undo_redo",
        "instruction": "Fix the editor reducer so undo and redo preserve history correctly, redo is cleared after a new edit, and unknown actions preserve object identity.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/editorReducer.mjs": """
                export function reducer(state, action) {
                  if (action.type === 'edit') {
                    return { text: action.text, past: [...state.past, state.text], future: state.future };
                  }
                  if (action.type === 'undo') {
                    const previous = state.past.pop();
                    return { text: previous, past: state.past, future: [state.text, ...state.future] };
                  }
                  if (action.type === 'redo') {
                    const next = state.future.shift();
                    return { text: next, past: [...state.past, state.text], future: state.future };
                  }
                  return { ...state };
                }
            """,
            "tests/editor-reducer.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { reducer } from '../src/editorReducer.mjs';

                test('new edit clears redo', () => {
                  const state = { text: 'b', past: ['a'], future: ['c'] };
                  assert.deepEqual(reducer(state, { type: 'edit', text: 'x' }).future, []);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { reducer } = await loadModule('src/editorReducer.mjs');
            const start = { text: 'a', past: [], future: [] };
            const b = reducer(start, { type: 'edit', text: 'b' });
            const c = reducer(b, { type: 'edit', text: 'c' });
            const back = reducer(c, { type: 'undo' });
            assert.deepEqual(back, { text: 'b', past: ['a'], future: ['c'] });
            assert.deepEqual(reducer(back, { type: 'redo' }), { text: 'c', past: ['a', 'b'], future: [] });
            assert.deepEqual(c, { text: 'c', past: ['a', 'b'], future: [] }, 'state must not be mutated');
            assert.strictEqual(reducer(start, { type: 'unknown' }), start);
        """),
    },
    {
        "task_id": "HARD-009",
        "category": "multi_turn_change",
        "repo_hint": "python/booking_policy",
        "instruction": "First support blackout date ranges; then add an override that lets admins book blackout dates only when capacity remains positive.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/booking_policy.py": """
                def can_book(user, date, capacity, blackout_ranges=None):
                    if capacity <= 0:
                        return False
                    return True
            """,
            "tests/test_booking_policy.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from booking_policy import can_book


                class BookingPolicyTest(unittest.TestCase):
                    def test_member_cannot_book_blackout(self):
                        self.assertFalse(can_book({"role": "member"}, "2026-07-04", 3, [("2026-07-01", "2026-07-10")]))

                    def test_admin_can_book_blackout_when_capacity_positive(self):
                        self.assertTrue(can_book({"role": "admin"}, "2026-07-04", 1, [("2026-07-01", "2026-07-10")]))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("booking_policy")
            ranges = [("2026-07-01", "2026-07-10"), ("2026-12-24", "2026-12-31")]
            assert not mod.can_book({"role": "member"}, "2026-12-25", 4, ranges)
            assert mod.can_book({"role": "admin"}, "2026-12-25", 4, ranges)
            assert not mod.can_book({"role": "admin"}, "2026-12-25", 0, ranges)
            assert mod.can_book({"role": "member"}, "2026-07-10", 1, ranges), "ranges are end-exclusive"
        """),
    },
    {
        "task_id": "HARD-010",
        "category": "feature",
        "repo_hint": "typescript/markdown_table",
        "instruction": "Implement markdown table parsing with escaped pipes, optional alignment rows, trimmed cells, and rejection of ragged rows.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/markdownTable.mjs": """
                export function parseTable(markdown) {
                  return markdown.trim().split('\\n').map((line) =>
                    line.replace(/^\\||\\|$/g, '').split('|').map((cell) => cell.trim())
                  );
                }
            """,
            "tests/markdown-table.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { parseTable } from '../src/markdownTable.mjs';

                test('ignores alignment row', () => {
                  assert.deepEqual(parseTable('| A | B |\\n|---|---|\\n| 1 | 2 |'), [['A', 'B'], ['1', '2']]);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { parseTable } = await loadModule('src/markdownTable.mjs');
            assert.deepEqual(parseTable('| A | B |\\n|---|:---:|\\n| a\\\\|b | c |'), [['A', 'B'], ['a|b', 'c']]);
            assert.throws(() => parseTable('| A | B |\\n|---|---|\\n| only one |'), /ragged|column/i);
        """),
    },
    {
        "task_id": "HARD-011",
        "category": "error_recovery",
        "repo_hint": "python/json_patch",
        "instruction": "Fix JSON Patch application so add, replace, remove, move, and copy handle JSON Pointer escaping and invalid paths correctly without mutating the input document.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/json_patch.py": """
                import copy


                class PatchError(Exception):
                    pass


                def apply_patch(document, operations):
                    result = copy.deepcopy(document)
                    for operation in operations:
                        op = operation["op"]
                        path = operation["path"].strip("/").split("/") if operation["path"] else []
                        target = result
                        for part in path[:-1]:
                            target = target[int(part)] if isinstance(target, list) else target[part]
                        key = path[-1] if path else None
                        if op in {"add", "replace"}:
                            if key is None:
                                result = operation["value"]
                            elif isinstance(target, list):
                                target[int(key)] = operation["value"]
                            else:
                                target[key] = operation["value"]
                        elif op == "remove":
                            if isinstance(target, list):
                                target.pop(int(key))
                            else:
                                del target[key]
                    return result
            """,
            "tests/test_json_patch.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from json_patch import apply_patch


                class JsonPatchTest(unittest.TestCase):
                    def test_add_replace_remove_without_mutating_input(self):
                        document = {"name": "Ada", "tags": ["math"]}
                        patched = apply_patch(document, [
                            {"op": "add", "path": "/tags/1", "value": "code"},
                            {"op": "replace", "path": "/name", "value": "Grace"},
                            {"op": "remove", "path": "/tags/0"},
                        ])
                        self.assertEqual(patched, {"name": "Grace", "tags": ["code"]})
                        self.assertEqual(document, {"name": "Ada", "tags": ["math"]})


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("json_patch")
            document = {"a/b": {"~key": ["x", "y"]}, "target": {}}
            patched = mod.apply_patch(document, [
                {"op": "copy", "from": "/a~1b/~0key/1", "path": "/target/copied"},
                {"op": "move", "from": "/a~1b/~0key/0", "path": "/target/moved"},
                {"op": "add", "path": "/a~1b/~0key/-", "value": "z"},
            ])
            assert patched == {"a/b": {"~key": ["y", "z"]}, "target": {"copied": "y", "moved": "x"}}
            assert document == {"a/b": {"~key": ["x", "y"]}, "target": {}}
            try:
                mod.apply_patch({"items": []}, [{"op": "remove", "path": "/items/0"}])
            except mod.PatchError:
                pass
            else:
                raise AssertionError("invalid remove path should raise PatchError")
        """),
    },
    {
        "task_id": "HARD-012",
        "category": "dependency_friction",
        "repo_hint": "python/http_client",
        "instruction": "Fix the retrying HTTP helper so 429 responses honor Retry-After, injected client and sleep hooks are used, HTTP-date retry delays are parsed, and non-retryable statuses return immediately without network dependencies.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/http_client.py": """
                from dataclasses import dataclass, field


                @dataclass
                class Response:
                    status: int
                    body: str = ""
                    headers: dict[str, str] = field(default_factory=dict)


                def request_with_retry(url, client, max_attempts=3, sleep=None, now=None):
                    return client(url)
            """,
            "tests/test_http_client.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from http_client import Response, request_with_retry


                class HttpClientTest(unittest.TestCase):
                    def test_retries_429_with_retry_after_delta(self):
                        calls = []
                        slept = []

                        def client(url):
                            calls.append(url)
                            if len(calls) == 1:
                                return Response(429, headers={"Retry-After": "2"})
                            return Response(200, "ok")

                        response = request_with_retry(
                            "https://example.invalid/data",
                            client=client,
                            max_attempts=3,
                            sleep=slept.append,
                        )

                        self.assertEqual(response.status, 200)
                        self.assertEqual(response.body, "ok")
                        self.assertEqual(calls, ["https://example.invalid/data", "https://example.invalid/data"])
                        self.assertEqual(slept, [2])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            from datetime import datetime, timezone

            run_visible_tests()
            mod = importlib.import_module("http_client")
            slept = []
            statuses = [mod.Response(503, headers={"Retry-After": "Wed, 21 Oct 2030 07:28:00 GMT"}), mod.Response(200, "done")]

            def client(url):
                return statuses.pop(0)

            response = mod.request_with_retry(
                "https://example.invalid/no-network",
                client=client,
                max_attempts=3,
                sleep=slept.append,
                now=lambda: datetime(2030, 10, 21, 7, 27, 30, tzinfo=timezone.utc),
            )
            assert response.status == 200
            assert response.body == "done"
            assert slept == [30]

            calls = []
            response = mod.request_with_retry(
                "https://example.invalid/not-found",
                client=lambda url: calls.append(url) or mod.Response(404, "missing"),
                max_attempts=5,
                sleep=lambda delay: (_ for _ in ()).throw(AssertionError("should not sleep")),
            )
            assert response.status == 404
            assert calls == ["https://example.invalid/not-found"]

            try:
                mod.request_with_retry(
                    "https://example.invalid/always-429",
                    client=lambda url: mod.Response(429, headers={"Retry-After": "bad"}),
                    max_attempts=2,
                    sleep=lambda delay: None,
                )
            except mod.RetryError as exc:
                assert "exhausted" in str(exc).lower()
            else:
                raise AssertionError("exhausted retries should raise RetryError")
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
        })
    HARD.mkdir(parents=True, exist_ok=True)
    TASKS.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


if __name__ == "__main__":
    materialize()
