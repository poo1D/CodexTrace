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
    {
        "task_id": "HARD-013",
        "category": "multi_turn_change",
        "repo_hint": "typescript/filter_builder",
        "instruction": "First add nested filter groups for and/or expressions; then add negation while preserving existing equality, range, and contains filters.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/filterBuilder.mjs": """
                export function buildFilter(input) {
                  if (input.op === 'eq') {
                    return `${input.field} = ${quote(input.value)}`;
                  }
                  if (input.op === 'range') {
                    return `${input.field} BETWEEN ${quote(input.min)} AND ${quote(input.max)}`;
                  }
                  if (input.op === 'contains') {
                    return `${input.field} CONTAINS ${quote(input.value)}`;
                  }
                  throw new Error(`unknown filter op: ${input.op}`);
                }

                function quote(value) {
                  if (typeof value === 'number') return String(value);
                  return `'${String(value).replaceAll(\"'\", \"''\")}'`;
                }
            """,
            "tests/filter-builder.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { buildFilter } from '../src/filterBuilder.mjs';

                test('builds and/or groups while preserving leaf filters', () => {
                  assert.equal(
                    buildFilter({
                      op: 'and',
                      filters: [
                        { op: 'eq', field: 'status', value: 'open' },
                        { op: 'or', filters: [
                          { op: 'range', field: 'age', min: 18, max: 30 },
                          { op: 'contains', field: 'name', value: \"O'Neil\" },
                        ] },
                      ],
                    }),
                    \"(status = 'open' AND (age BETWEEN 18 AND 30 OR name CONTAINS 'O''Neil'))\"
                  );
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { buildFilter } = await loadModule('src/filterBuilder.mjs');
            assert.equal(
              buildFilter({ op: 'not', filter: { op: 'eq', field: 'archived', value: true } }),
              \"NOT (archived = true)\"
            );
            assert.equal(
              buildFilter({
                op: 'not',
                filter: {
                  op: 'or',
                  filters: [
                    { op: 'eq', field: 'status', value: 'closed' },
                    { op: 'contains', field: 'title', value: 'wip' },
                  ],
                },
              }),
              \"NOT ((status = 'closed' OR title CONTAINS 'wip'))\"
            );
            assert.equal(
              buildFilter({
                op: 'and',
                filters: [
                  { op: 'eq', field: 'priority', value: 'high' },
                  { op: 'not', filter: { op: 'range', field: 'age', min: 0, max: 7 } },
                ],
              }),
              \"(priority = 'high' AND NOT (age BETWEEN 0 AND 7))\"
            );
            assert.equal(buildFilter({ op: 'eq', field: 'active', value: false }), 'active = false');
            assert.throws(() => buildFilter({ op: 'and', filters: [] }), /empty|filter/i);
        """),
    },
    {
        "task_id": "HARD-014",
        "category": "refactor",
        "repo_hint": "python/permission_matrix",
        "instruction": "Refactor permission checks into a reusable resolver: roles inherit permissions, explicit denies override inherited allows, user overrides win last, and inputs must not be mutated.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/permissions.py": """
                def can_access(user, action, matrix):
                    role = user.get("role")
                    permissions = matrix.get(role, {})
                    if action in user.get("allow", []):
                        return True
                    if action in user.get("deny", []):
                        return False
                    return action in permissions.get("allow", [])
            """,
            "tests/test_permissions.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from permissions import can_access


                class PermissionTest(unittest.TestCase):
                    def test_role_inherits_parent_allow(self):
                        matrix = {
                            "viewer": {"allow": ["read"]},
                            "editor": {"inherits": ["viewer"], "allow": ["write"]},
                        }
                        self.assertTrue(can_access({"role": "editor"}, "read", matrix))
                        self.assertTrue(can_access({"role": "editor"}, "write", matrix))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy

            run_visible_tests()
            mod = importlib.import_module("permissions")
            matrix = {
                "guest": {"allow": ["read"], "deny": ["delete"]},
                "member": {"inherits": ["guest"], "allow": ["comment"]},
                "moderator": {"inherits": ["member"], "allow": ["delete"], "deny": ["billing"]},
                "admin": {"inherits": ["moderator"], "allow": ["billing"]},
            }
            original = copy.deepcopy(matrix)
            assert mod.can_access({"role": "admin"}, "read", matrix)
            assert mod.can_access({"role": "admin"}, "comment", matrix)
            assert not mod.can_access({"role": "admin"}, "delete", matrix), "deny inherited from guest overrides later allow"
            assert not mod.can_access({"role": "admin"}, "billing", matrix), "moderator deny overrides admin allow"
            assert mod.can_access({"role": "member", "allow": ["billing"]}, "billing", matrix), "user allow wins last"
            assert not mod.can_access({"role": "admin", "deny": ["read"]}, "read", matrix), "user deny wins last"
            assert matrix == original
            assert hasattr(mod, "resolve_permissions") or hasattr(mod, "_resolve_permissions")
        """),
    },
    {
        "task_id": "HARD-015",
        "category": "ci_failure",
        "repo_hint": "typescript/package_exports",
        "instruction": "Fix the package build and exports so npm run build succeeds and both ESM import and CommonJS require entry points expose formatName.",
        "public_success_check": "npm run build",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": json.dumps(
                {
                    "name": "hard-015-package-exports",
                    "version": "0.0.0",
                    "type": "module",
                    "main": "./dist/index.js",
                    "exports": {
                        ".": "./dist/index.mjs",
                    },
                    "scripts": {
                        "build": "node scripts/build.mjs",
                    },
                },
                indent=2,
            )
            + "\n",
            "scripts/build.mjs": """
                import fs from 'node:fs/promises';
                import path from 'node:path';

                const root = process.cwd();
                const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8'));
                const entry = pkg.exports?.['.'];

                if (!entry || typeof entry !== 'object') {
                  throw new Error('package exports must define conditional import and require entry points');
                }
                if (entry.import !== './dist/index.mjs') {
                  throw new Error('ESM import export must point to ./dist/index.mjs');
                }
                if (entry.require !== './dist/index.cjs') {
                  throw new Error('CommonJS require export must point to ./dist/index.cjs');
                }

                await fs.mkdir(path.join(root, 'dist'), { recursive: true });
                await fs.copyFile(path.join(root, 'src/index.mjs'), path.join(root, 'dist/index.mjs'));
                await fs.copyFile(path.join(root, 'src/index.cjs'), path.join(root, 'dist/index.cjs'));
            """,
            "src/index.mjs": """
                export function formatName(user) {
                  return `${user.first} ${user.last}`;
                }
            """,
            "README.md": """
                # hard-015-package-exports

                This package must support both ESM import and CommonJS require.

                Expected public command:

                ```bash
                npm run build
                ```
            """,
        },
        "grader": node_grader("""
            run('npm', ['run', 'build']);

            const fs = await import('node:fs/promises');
            const { createRequire } = await import('node:module');
            const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8'));
            assert.equal(pkg.exports['.'].import, './dist/index.mjs');
            assert.equal(pkg.exports['.'].require, './dist/index.cjs');

            const esm = await loadModule('dist/index.mjs');
            const require = createRequire(path.join(root, 'grader.cjs'));
            const cjs = require(path.join(root, 'dist/index.cjs'));

            assert.equal(esm.formatName({ first: 'Ada', last: 'Lovelace' }), 'Ada Lovelace');
            assert.equal(cjs.formatName({ first: 'Grace', last: 'Hopper' }), 'Grace Hopper');
            assert.equal(esm.formatName({ first: '  Katherine ', last: ' Johnson  ' }), 'Katherine Johnson');
            assert.equal(cjs.formatName({ first: 'Alan', last: 'Turing', title: 'Dr.' }), 'Alan Turing');
        """),
    },
    {
        "task_id": "HARD-016",
        "category": "bug_fix",
        "repo_hint": "python/time_window",
        "instruction": "Fix time window overlap checks: windows are half-open [start, end), invalid or empty windows raise ValueError, and timezone-aware datetimes must be compared by absolute time across DST boundaries.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/time_window.py": """
                def overlaps(left, right):
                    left_start, left_end = left
                    right_start, right_end = right
                    return left_start <= right_end and right_start <= left_end
            """,
            "tests/test_time_window.py": """
                import sys
                import unittest
                from datetime import datetime
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from time_window import overlaps


                class TimeWindowTest(unittest.TestCase):
                    def test_touching_half_open_windows_do_not_overlap(self):
                        left = (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 0))
                        right = (datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 11, 0))
                        self.assertFalse(overlaps(left, right))

                    def test_actual_overlap(self):
                        left = (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 10, 30))
                        right = (datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 11, 0))
                        self.assertTrue(overlaps(left, right))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            from datetime import datetime, timezone
            from zoneinfo import ZoneInfo

            run_visible_tests()
            mod = importlib.import_module("time_window")

            ny = ZoneInfo("America/New_York")
            utc = timezone.utc

            before_fallback = (
                datetime(2024, 11, 3, 1, 15, tzinfo=ny, fold=0),
                datetime(2024, 11, 3, 1, 45, tzinfo=ny, fold=0),
            )
            after_fallback = (
                datetime(2024, 11, 3, 1, 30, tzinfo=ny, fold=1),
                datetime(2024, 11, 3, 2, 0, tzinfo=ny, fold=1),
            )
            assert not mod.overlaps(before_fallback, after_fallback), "folded DST windows must compare by absolute time"

            same_instant_left = (
                datetime(2026, 5, 1, 12, 0, tzinfo=utc),
                datetime(2026, 5, 1, 13, 0, tzinfo=utc),
            )
            same_instant_right = (
                datetime(2026, 5, 1, 8, 30, tzinfo=ZoneInfo("America/New_York")),
                datetime(2026, 5, 1, 9, 30, tzinfo=ZoneInfo("America/New_York")),
            )
            assert mod.overlaps(same_instant_left, same_instant_right)

            try:
                mod.overlaps(
                    (datetime(2026, 1, 1, 10, 0), datetime(2026, 1, 1, 10, 0)),
                    (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 11, 0)),
                )
            except ValueError:
                pass
            else:
                raise AssertionError("empty windows should raise ValueError")

            try:
                mod.overlaps(
                    (datetime(2026, 1, 1, 11, 0), datetime(2026, 1, 1, 10, 0)),
                    (datetime(2026, 1, 1, 9, 0), datetime(2026, 1, 1, 12, 0)),
                )
            except ValueError:
                pass
            else:
                raise AssertionError("inverted windows should raise ValueError")
        """),
    },
    {
        "task_id": "HARD-017",
        "category": "feature",
        "repo_hint": "typescript/batch_queue",
        "instruction": "Implement a sequential async batch queue: add push, cancel, size, and flush support; flush must preserve item order, wait for async handlers, isolate rejected items, and leave the queue reusable.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/batchQueue.mjs": """
                export class BatchQueue {
                  constructor(handler) {
                    this.handler = handler;
                    this.items = [];
                  }

                  push(item) {
                    this.items.push(item);
                  }

                  size() {
                    return this.items.length;
                  }

                  flush() {
                    const pending = this.items;
                    this.items = [];
                    const results = [];
                    for (const item of pending) {
                      results.push(this.handler(item));
                    }
                    return results;
                  }
                }
            """,
            "tests/batch-queue.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { BatchQueue } from '../src/batchQueue.mjs';

                test('flush waits for async handlers and preserves order', async () => {
                  const queue = new BatchQueue(async item => {
                    await Promise.resolve();
                    return item * 2;
                  });
                  queue.push(1);
                  queue.push(2);
                  assert.equal(queue.size(), 2);
                  assert.deepEqual(await queue.flush(), [
                    { status: 'fulfilled', value: 2 },
                    { status: 'fulfilled', value: 4 },
                  ]);
                  assert.equal(queue.size(), 0);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { BatchQueue } = await loadModule('src/batchQueue.mjs');

            const events = [];
            const queue = new BatchQueue(async item => {
              events.push(`start:${item.id}`);
              if (item.fail) {
                throw new Error(`bad:${item.id}`);
              }
              await Promise.resolve();
              events.push(`done:${item.id}`);
              return item.id.toUpperCase();
            });

            queue.push({ id: 'a' });
            queue.push({ id: 'b', fail: true });
            queue.push({ id: 'c' });
            assert.equal(queue.cancel(item => item.id === 'c'), 1);
            assert.equal(queue.size(), 2);

            const first = await queue.flush();
            assert.deepEqual(first.map(result => result.status), ['fulfilled', 'rejected']);
            assert.equal(first[0].value, 'A');
            assert.match(first[1].reason.message, /bad:b/);
            assert.deepEqual(events, ['start:a', 'done:a', 'start:b']);
            assert.equal(queue.size(), 0);

            queue.push({ id: 'd' });
            queue.push({ id: 'e' });
            assert.equal(queue.cancel(item => item.id === 'missing'), 0);
            assert.deepEqual(await queue.flush(), [
              { status: 'fulfilled', value: 'D' },
              { status: 'fulfilled', value: 'E' },
            ]);
            assert.deepEqual(await queue.flush(), []);
        """),
    },
    {
        "task_id": "HARD-018",
        "category": "error_localization",
        "repo_hint": "python/yaml_frontmatter",
        "instruction": "Fix the frontmatter parser: parse simple YAML-like key/value metadata, preserve colons inside values, return plain documents unchanged, and raise FrontmatterError with useful diagnostics for malformed delimiters or metadata lines.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/frontmatter.py": """
                def parse_frontmatter(text):
                    if not text.startswith("---\\n"):
                        return {}, text
                    end = text.index("\\n---\\n", 4)
                    header = text[4:end].strip()
                    body = text[end + 5:]
                    metadata = {}
                    for line in header.splitlines():
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                    return metadata, body
            """,
            "tests/test_frontmatter.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                import frontmatter


                class FrontmatterTest(unittest.TestCase):
                    def test_simple_frontmatter(self):
                        metadata, body = frontmatter.parse_frontmatter("---\\ntitle: Hello\\n---\\nBody\\n")
                        self.assertEqual(metadata, {"title": "Hello"})
                        self.assertEqual(body, "Body\\n")

                    def test_missing_closing_delimiter_raises_domain_error(self):
                        with self.assertRaises(frontmatter.FrontmatterError) as ctx:
                            frontmatter.parse_frontmatter("---\\ntitle: Hello\\nBody\\n")
                        self.assertIn("closing", str(ctx.exception).lower())


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("frontmatter")

            assert mod.parse_frontmatter("") == ({}, "")
            assert mod.parse_frontmatter("plain body\\n") == ({}, "plain body\\n")

            metadata, body = mod.parse_frontmatter("---\\ntitle: A: B\\ntags: one, two\\n---\\nBody")
            assert metadata == {"title": "A: B", "tags": "one, two"}
            assert body == "Body"

            try:
                mod.parse_frontmatter("---\\ntitle without colon\\n---\\n")
            except mod.FrontmatterError as exc:
                message = str(exc).lower()
                assert "line 2" in message or "metadata" in message
            else:
                raise AssertionError("metadata lines without ':' should raise FrontmatterError")

            try:
                mod.parse_frontmatter("---\\ntitle: Hello\\n--\\nBody")
            except mod.FrontmatterError as exc:
                assert "closing" in str(exc).lower()
            else:
                raise AssertionError("malformed closing delimiter should raise FrontmatterError")
        """),
    },
    {
        "task_id": "HARD-019",
        "category": "multi_turn_change",
        "repo_hint": "python/search_ranker",
        "instruction": "Update the search ranker to boost exact query matches in titles and body text while preserving existing token relevance, stable ordering, and recency tie-break behavior.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/search_ranker.py": """
                from datetime import datetime, timezone


                def rank_results(query, documents):
                    terms = [term.casefold() for term in query.split() if term.strip()]

                    def timestamp(document):
                        value = document.get("updated_at")
                        if isinstance(value, datetime):
                            dt = value
                        else:
                            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return dt

                    def score(document):
                        haystack = f"{document.get('title', '')} {document.get('body', '')}".casefold()
                        return sum(1 for term in terms if term in haystack)

                    indexed = list(enumerate(documents))
                    indexed.sort(
                        key=lambda item: (
                            score(item[1]),
                            timestamp(item[1]),
                            -item[0],
                        ),
                        reverse=True,
                    )
                    return [document for _, document in indexed]
            """,
            "tests/test_search_ranker.py": """
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
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("search_ranker")

            docs = [
                {"id": "new-loose", "title": "Search ranker", "body": "exact match tuning", "updated_at": "2026-06-01T00:00:00Z"},
                {"id": "old-exact-title", "title": "Exact match", "body": "ranking notes", "updated_at": "2024-01-01T00:00:00Z"},
                {"id": "new-one-term", "title": "Exact", "body": "unrelated", "updated_at": "2026-07-01T00:00:00Z"},
            ]
            assert [doc["id"] for doc in mod.rank_results("exact match", docs)][:2] == [
                "old-exact-title",
                "new-loose",
            ]

            phrase_docs = [
                {"id": "recent-split", "title": "Match diagnostics", "body": "exact token appears elsewhere", "updated_at": "2026-05-01T00:00:00Z"},
                {"id": "older-body-phrase", "title": "Diagnostics", "body": "Investigate exact match behavior", "updated_at": "2025-05-01T00:00:00Z"},
            ]
            assert mod.rank_results("exact match", phrase_docs)[0]["id"] == "older-body-phrase"

            tie_docs = [
                {"id": "older-exact", "title": "Exact match", "body": "", "updated_at": "2025-01-01T00:00:00Z"},
                {"id": "newer-exact", "title": "Exact match", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
            ]
            assert [doc["id"] for doc in mod.rank_results("exact match", tie_docs)] == [
                "newer-exact",
                "older-exact",
            ]

            stable_docs = [
                {"id": "first", "title": "Nothing", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
                {"id": "second", "title": "Nothing", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
            ]
            assert [doc["id"] for doc in mod.rank_results("missing", stable_docs)] == ["first", "second"]
        """),
    },
    {
        "task_id": "HARD-020",
        "category": "sandbox_friction",
        "repo_hint": "typescript/asset_loader",
        "instruction": "Fix the asset loader so it never depends on network access: remote asset URLs must resolve through a local fixture manifest fallback, local fixture paths must still load directly, JSON and text assets must be decoded correctly, and missing assets should raise AssetLoadError.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/assetLoader.mjs": """
                import fs from 'node:fs/promises';
                import path from 'node:path';

                export async function loadAsset(source, options = {}) {
                  const type = options.type ?? inferType(source);

                  if (/^https?:\\/\\//.test(source)) {
                    const response = await fetch(source);
                    if (!response.ok) {
                      throw new Error(`failed to fetch asset: ${response.status}`);
                    }
                    return type === 'json' ? response.json() : response.text();
                  }

                  const rootDir = options.rootDir ?? 'fixtures/assets';
                  const filePath = path.join(rootDir, source);
                  const text = await fs.readFile(filePath, 'utf8');
                  return type === 'json' ? JSON.parse(text) : text;
                }

                function inferType(source) {
                  return source.endsWith('.json') ? 'json' : 'text';
                }
            """,
            "fixtures/assets/logo.txt": """
                LOCAL-LOGO
            """,
            "fixtures/assets/config.json": """
                {"name":"local-config","version":1}
            """,
            "fixtures/assets/manifest.json": """
                {
                  "https://cdn.example.invalid/assets/logo.txt": "logo.txt",
                  "https://cdn.example.invalid/assets/config.json": "config.json"
                }
            """,
            "tests/asset-loader.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { loadAsset } from '../src/assetLoader.mjs';

                test('loads local text fixture', async () => {
                  assert.equal(await loadAsset('logo.txt'), 'LOCAL-LOGO\\n');
                });

                test('loads local json fixture', async () => {
                  assert.deepEqual(await loadAsset('config.json'), { name: 'local-config', version: 1 });
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);

            const { loadAsset, AssetLoadError } = await loadModule('src/assetLoader.mjs');

            let fetchCalls = 0;
            globalThis.fetch = async url => {
              fetchCalls += 1;
              throw new Error(`network forbidden in hidden grader: ${url}`);
            };

            assert.equal(
              await loadAsset('https://cdn.example.invalid/assets/logo.txt'),
              'LOCAL-LOGO\\n'
            );

            assert.deepEqual(
              await loadAsset('https://cdn.example.invalid/assets/config.json', { type: 'json' }),
              { name: 'local-config', version: 1 }
            );

            assert.equal(fetchCalls, 0, 'loader must not call fetch for manifest-backed remote assets');
            assert.equal(typeof AssetLoadError, 'function');

            await assert.rejects(
              loadAsset('https://cdn.example.invalid/assets/missing.txt'),
              error => {
                assert.ok(error instanceof AssetLoadError || /asset|missing|fixture/i.test(error.message));
                return true;
              }
            );

            assert.equal(fetchCalls, 0, 'missing manifest entries should fail locally without network');
        """),
    },
    {
        "task_id": "HARD-021",
        "category": "bug_fix",
        "repo_hint": "python/currency_parser",
        "instruction": "Fix currency parsing so amounts are converted to integer cents with optional currency symbols or codes, thousands separators, accounting parentheses for negatives, locale-free dot decimals, and clear CurrencyParseError failures for malformed inputs.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/currency.py": """
                class CurrencyParseError(ValueError):
                    pass


                def parse_cents(value):
                    text = str(value).strip()
                    text = text.replace("$", "").replace(",", "")
                    try:
                        return int(round(float(text) * 100))
                    except ValueError as exc:
                        raise CurrencyParseError(f"invalid amount: {value}") from exc
            """,
            "tests/test_currency.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from currency import CurrencyParseError, parse_cents


                class CurrencyParserTest(unittest.TestCase):
                    def test_simple_dollar_amount(self):
                        self.assertEqual(parse_cents("$12.34"), 1234)

                    def test_thousands_separator(self):
                        self.assertEqual(parse_cents("$1,234.50"), 123450)

                    def test_invalid_text_raises_domain_error(self):
                        with self.assertRaises(CurrencyParseError):
                            parse_cents("not money")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("currency")

            assert mod.parse_cents("(1,234.50)") == -123450
            assert mod.parse_cents("($19.99)") == -1999
            assert mod.parse_cents("USD 2,500.05") == 250005
            assert mod.parse_cents("EUR -0.99") == -99
            assert mod.parse_cents("0.10") == 10
            assert mod.parse_cents("42") == 4200

            malformed = ["1,23", "1.234,56", "$12.345", "(12.00", "USD"]
            for value in malformed:
                try:
                    mod.parse_cents(value)
                except mod.CurrencyParseError:
                    pass
                else:
                    raise AssertionError(f"malformed amount should fail: {value!r}")
        """),
    },
    {
        "task_id": "HARD-022",
        "category": "refactor",
        "repo_hint": "typescript/state_machine",
        "instruction": "Refactor the order state machine into a reusable transition table or helper while preserving behavior: valid transitions should create a new state with a consistent history entry, cancel must be allowed from draft or submitted, invalid transitions must leave the state unchanged, and inputs must not be mutated.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/stateMachine.mjs": """
                export function transition(state, event, details = {}) {
                  const status = state.status;

                  if (status === 'draft' && event === 'submit') {
                    return withHistory(state, 'submitted', event, details);
                  }

                  if (status === 'draft' && event === 'cancel') {
                    return withHistory(state, 'canceled', event, details);
                  }

                  if (status === 'submitted' && event === 'cancel') {
                    return withHistory(state, 'canceled', event, details);
                  }

                  if (status === 'submitted' && event === 'approve') {
                    return withHistory(state, 'approved', event, details);
                  }

                  if (status === 'approved' && event === 'ship') {
                    return withHistory(state, 'shipped', event, details);
                  }

                  if (status === 'shipped' && event === 'deliver') {
                    return withHistory(state, 'delivered', event, details);
                  }

                  return { ...state };
                }

                function withHistory(state, nextStatus, event, details) {
                  const entry = {
                    from: state.status,
                    to: nextStatus,
                    event,
                    by: details.by ?? 'system',
                  };
                  if (details.reason) {
                    entry.reason = details.reason;
                  }
                  return {
                    ...state,
                    status: nextStatus,
                    history: [...(state.history ?? []), entry],
                  };
                }
            """,
            "tests/state-machine.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { transition } from '../src/stateMachine.mjs';

                test('submits and records history', () => {
                  const state = { status: 'draft', history: [] };
                  assert.deepEqual(transition(state, 'submit', { by: 'Ada' }), {
                    status: 'submitted',
                    history: [{ from: 'draft', to: 'submitted', event: 'submit', by: 'Ada' }],
                  });
                });

                test('approves submitted orders', () => {
                  const state = { status: 'submitted', history: [] };
                  assert.equal(transition(state, 'approve').status, 'approved');
                });

                test('cancels submitted orders with a reason', () => {
                  const state = { status: 'submitted', history: [] };
                  assert.deepEqual(transition(state, 'cancel', { by: 'Grace', reason: 'duplicate' }), {
                    status: 'canceled',
                    history: [{ from: 'submitted', to: 'canceled', event: 'cancel', by: 'Grace', reason: 'duplicate' }],
                  });
                });

                test('invalid transitions preserve values', () => {
                  const state = { status: 'draft', history: [] };
                  assert.deepEqual(transition(state, 'ship'), state);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);

            const { transition } = await loadModule('src/stateMachine.mjs');

            const draft = Object.freeze({ status: 'draft', history: Object.freeze([]) });
            const submitted = transition(draft, 'submit', { by: 'Ada' });
            assert.notStrictEqual(submitted, draft, 'valid transitions must create a new state');
            assert.equal(submitted.status, 'submitted');
            assert.deepEqual(draft, { status: 'draft', history: [] }, 'input state must not be mutated');

            const approved = transition(submitted, 'approve', { by: 'Linus' });
            const shipped = transition(approved, 'ship', { by: 'Grace' });
            const delivered = transition(shipped, 'deliver', { by: 'Margaret' });
            assert.equal(delivered.status, 'delivered');
            assert.deepEqual(
              delivered.history.map(entry => [entry.from, entry.to, entry.event]),
              [
                ['draft', 'submitted', 'submit'],
                ['submitted', 'approved', 'approve'],
                ['approved', 'shipped', 'ship'],
                ['shipped', 'delivered', 'deliver'],
              ]
            );

            const submittedForCancel = { status: 'submitted', history: [] };
            const canceled = transition(submittedForCancel, 'cancel', { by: 'Ada', reason: 'duplicate' });
            assert.equal(canceled.status, 'canceled');
            assert.deepEqual(canceled.history[0], {
              from: 'submitted',
              to: 'canceled',
              event: 'cancel',
              by: 'Ada',
              reason: 'duplicate',
            });

            const invalidDraft = { status: 'draft', history: [] };
            assert.strictEqual(transition(invalidDraft, 'ship'), invalidDraft);
            assert.strictEqual(transition(invalidDraft, 'unknown-event'), invalidDraft);

            const deliveredState = { status: 'delivered', history: [] };
            assert.strictEqual(transition(deliveredState, 'cancel'), deliveredState);

            const source = await (await import('node:fs/promises')).readFile('src/stateMachine.mjs', 'utf8');
            assert.match(
              source,
              /TRANSITIONS|transitionMap|allowedTransitions|createTransition|canTransition/,
              'refactor should introduce a reusable transition table or helper'
            );
        """),
    },
    {
        "task_id": "HARD-023",
        "category": "error_recovery",
        "repo_hint": "python/cache_stampede",
        "instruction": "Fix the TTL cache so concurrent requests for the same expired or missing key share one in-flight loader call. Fresh values should be reused until TTL expiry. Loader failures must not be cached. When stale_if_error=True and an expired value exists, return the stale value if refresh fails. Different keys must not block each other. Preserve the public TTLCache API and use the injected now clock for deterministic tests.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/cache_stampede.py": """
                import time


                class TTLCache:
                    def __init__(self, now=None):
                        self._now = now or time.monotonic
                        self._values = {}

                    def get_or_set(self, key, loader, ttl, stale_if_error=False):
                        entry = self._values.get(key)
                        now = self._now()
                        if entry is not None and entry["expires_at"] > now:
                            return entry["value"]

                        value = loader()
                        self._values[key] = {"value": value, "expires_at": self._now() + ttl}
                        return value

                    def clear(self):
                        self._values.clear()
            """,
            "tests/test_cache_stampede.py": """
                import sys
                import threading
                import time
                import unittest
                from concurrent.futures import ThreadPoolExecutor
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from cache_stampede import TTLCache


                class CacheStampedeTest(unittest.TestCase):
                    def test_reuses_fresh_value_and_refreshes_after_ttl(self):
                        now = [100.0]
                        calls = []
                        cache = TTLCache(now=lambda: now[0])

                        self.assertEqual(cache.get_or_set("item", lambda: calls.append("a") or "first", ttl=5), "first")
                        self.assertEqual(cache.get_or_set("item", lambda: calls.append("b") or "second", ttl=5), "first")

                        now[0] = 106.0
                        self.assertEqual(cache.get_or_set("item", lambda: calls.append("c") or "third", ttl=5), "third")
                        self.assertEqual(calls, ["a", "c"])

                    def test_concurrent_miss_uses_one_loader_call(self):
                        cache = TTLCache(now=lambda: 10.0)
                        entered = threading.Event()
                        release = threading.Event()
                        calls = []
                        lock = threading.Lock()

                        def loader():
                            with lock:
                                calls.append("load")
                            entered.set()
                            release.wait(timeout=2)
                            return "shared"

                        with ThreadPoolExecutor(max_workers=5) as pool:
                            futures = [pool.submit(cache.get_or_set, "shared-key", loader, 30) for _ in range(5)]
                            self.assertTrue(entered.wait(timeout=1))
                            time.sleep(0.05)
                            release.set()
                            self.assertEqual([future.result(timeout=1) for future in futures], ["shared"] * 5)

                        self.assertEqual(calls, ["load"])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import threading
            import time
            from concurrent.futures import ThreadPoolExecutor

            run_visible_tests()
            mod = importlib.import_module("cache_stampede")

            now = [0.0]
            cache = mod.TTLCache(now=lambda: now[0])
            assert cache.get_or_set("profile", lambda: {"name": "Ada"}, ttl=5) == {"name": "Ada"}

            now[0] = 10.0

            def failing_refresh():
                raise RuntimeError("origin unavailable")

            assert cache.get_or_set("profile", failing_refresh, ttl=5, stale_if_error=True) == {"name": "Ada"}

            cold_calls = []

            def failing_cold():
                cold_calls.append("fail")
                raise ValueError("temporary")

            try:
                cache.get_or_set("cold", failing_cold, ttl=5, stale_if_error=True)
            except ValueError:
                pass
            else:
                raise AssertionError("cold load failure should propagate")

            assert cache.get_or_set("cold", lambda: "recovered", ttl=5, stale_if_error=True) == "recovered"
            assert cold_calls == ["fail"]

            cache = mod.TTLCache(now=lambda: 50.0)
            entered = threading.Event()
            release = threading.Event()
            calls = []
            calls_lock = threading.Lock()

            def failing_once():
                with calls_lock:
                    calls.append("load")
                entered.set()
                release.wait(timeout=2)
                raise RuntimeError("boom")

            with ThreadPoolExecutor(max_workers=4) as pool:
                futures = [pool.submit(cache.get_or_set, "same", failing_once, 10) for _ in range(4)]
                assert entered.wait(timeout=1)
                time.sleep(0.05)
                release.set()
                for future in futures:
                    try:
                        future.result(timeout=1)
                    except RuntimeError as exc:
                        assert "boom" in str(exc)
                    else:
                        raise AssertionError("all waiters should observe the load failure")

            assert calls == ["load"], "same-key concurrent failure should use one loader call"
            assert cache.get_or_set("same", lambda: "ok", ttl=10) == "ok"

            cache = mod.TTLCache(now=lambda: 100.0)
            slow_started = threading.Event()
            slow_release = threading.Event()

            def slow_loader():
                slow_started.set()
                slow_release.wait(timeout=2)
                return "slow"

            with ThreadPoolExecutor(max_workers=2) as pool:
                slow_future = pool.submit(cache.get_or_set, "slow", slow_loader, 10)
                assert slow_started.wait(timeout=1)
                fast_future = pool.submit(cache.get_or_set, "fast", lambda: "fast", 10)
                assert fast_future.result(timeout=0.2) == "fast"
                slow_release.set()
                assert slow_future.result(timeout=1) == "slow"
        """),
    },
    {
        "task_id": "HARD-024",
        "category": "feature",
        "repo_hint": "typescript/csv_stream",
        "instruction": "Implement a streaming CSV parser with incremental chunk input, RFC 4180-style quoted fields, escaped quotes, quoted newlines, CRLF handling, stable column counts, and clear CsvParseError failures for malformed or ragged input.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/csvStream.mjs": """
                export class CsvParseError extends Error {}

                export class CsvStreamParser {
                  constructor() {
                    this.buffer = '';
                    this.columns = null;
                  }

                  write(chunk) {
                    this.buffer += String(chunk);
                    const rows = [];
                    const lines = this.buffer.split('\\n');
                    this.buffer = lines.pop() ?? '';

                    for (const line of lines) {
                      const cleaned = line.endsWith('\\r') ? line.slice(0, -1) : line;
                      if (cleaned.length === 0) continue;
                      rows.push(this.parseLine(cleaned));
                    }

                    return rows;
                  }

                  end() {
                    if (this.buffer.length === 0) return [];
                    const line = this.buffer;
                    this.buffer = '';
                    return [this.parseLine(line)];
                  }

                  parseLine(line) {
                    const row = line.split(',');
                    if (this.columns === null) {
                      this.columns = row.length;
                    } else if (row.length !== this.columns) {
                      throw new CsvParseError(`ragged row: expected ${this.columns} columns, got ${row.length}`);
                    }
                    return row;
                  }
                }

                export async function parseCsvStream(chunks) {
                  const parser = new CsvStreamParser();
                  const rows = [];
                  for await (const chunk of chunks) {
                    rows.push(...parser.write(chunk));
                  }
                  rows.push(...parser.end());
                  return rows;
                }
            """,
            "tests/csv-stream.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { CsvParseError, CsvStreamParser, parseCsvStream } from '../src/csvStream.mjs';

                test('emits complete unquoted rows incrementally', () => {
                  const parser = new CsvStreamParser();
                  assert.deepEqual(parser.write('name,age\\nAda,'), [['name', 'age']]);
                  assert.deepEqual(parser.write('37\\nGrace,44'), [['Ada', '37']]);
                  assert.deepEqual(parser.end(), [['Grace', '44']]);
                });

                test('parses quoted comma and escaped quote', async () => {
                  assert.deepEqual(
                    await parseCsvStream(['name,note\\nAda,\"ships, fast\"\\nGrace,\"said \"\"hi\"\"\"\\n']),
                    [
                      ['name', 'note'],
                      ['Ada', 'ships, fast'],
                      ['Grace', 'said \"hi\"'],
                    ]
                  );
                });

                test('rejects ragged rows with CsvParseError', async () => {
                  await assert.rejects(
                    parseCsvStream(['a,b\\n1,2,3\\n']),
                    error => error instanceof CsvParseError && /ragged|column/i.test(error.message)
                  );
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);

            const { CsvParseError, CsvStreamParser, parseCsvStream } = await loadModule('src/csvStream.mjs');

            const parser = new CsvStreamParser();
            assert.deepEqual(parser.write('name,note\\nAda,\"hello'), [['name', 'note']]);
            assert.deepEqual(parser.write(', wor'), []);
            assert.deepEqual(parser.write('ld\"\\n'), [['Ada', 'hello, world']]);
            assert.deepEqual(parser.end(), []);

            assert.deepEqual(
              await parseCsvStream(['id,note\\n1,\"a \"\"quo', 'te\"\" here\"\\n']),
              [
                ['id', 'note'],
                ['1', 'a \"quote\" here'],
              ]
            );

            assert.deepEqual(
              await parseCsvStream(['id,body\\n1,\"line one', '\\nline two\"\\n2,done\\n']),
              [
                ['id', 'body'],
                ['1', 'line one\\nline two'],
                ['2', 'done'],
              ]
            );

            assert.deepEqual(
              await parseCsvStream(['a,b\\r', '\\n\"x\\r\\ny\",z']),
              [
                ['a', 'b'],
                ['x\\r\\ny', 'z'],
              ]
            );

            await assert.rejects(
              parseCsvStream(['a,b\\n1,\"unterminated']),
              error => error instanceof CsvParseError && /quote|unterminated/i.test(error.message)
            );

            await assert.rejects(
              parseCsvStream(['a,b\\n1,\"ok\" trailing\\n']),
              error => error instanceof CsvParseError && /quote|trailing|invalid/i.test(error.message)
            );

            const incremental = new CsvStreamParser();
            assert.deepEqual(incremental.write('a,b\\n1,\"still'), [['a', 'b']]);
            assert.deepEqual(incremental.write(' open'), []);
            assert.deepEqual(incremental.write('\"\\n2,done\\n'), [['1', 'still open'], ['2', 'done']]);
            assert.deepEqual(incremental.end(), []);
        """),
    },
    {
        "task_id": "HARD-025",
        "category": "ci_failure",
        "repo_hint": "python/typing_protocol",
        "instruction": "Fix the protocol typing CI failure so MemoryEventWriter structurally conforms to EventWriter and publish_events works with any protocol-compatible writer without changing the public API.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/event_writer.py": """
                from typing import Protocol


                class EventWriter(Protocol):
                    def write(self, message: str) -> int:
                        ...

                    def flush(self) -> None:
                        ...


                class MemoryEventWriter:
                    def __init__(self):
                        self.messages = []
                        self.flushed = False

                    def append(self, message: str) -> None:
                        self.messages.append(message)

                    def drain(self) -> None:
                        self.flushed = True


                def publish_events(events, writer=None):
                    if writer is None:
                        writer = MemoryEventWriter()
                    for event in events:
                        writer.append(f"event: {event}\\n")
                    writer.drain()
                    return writer
            """,
            "tests/test_event_writer.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from event_writer import EventWriter, MemoryEventWriter, publish_events


                class EventWriterTest(unittest.TestCase):
                    def test_memory_writer_conforms_to_protocol(self):
                        writer = MemoryEventWriter()
                        self.assertIsInstance(writer, EventWriter)
                        self.assertEqual(writer.write("hello\\n"), len("hello\\n"))
                        writer.flush()
                        self.assertEqual(writer.messages, ["hello\\n"])
                        self.assertTrue(writer.flushed)

                    def test_publish_events_uses_memory_writer(self):
                        writer = publish_events(["created", "closed"])
                        self.assertEqual(writer.messages, ["event: created\\n", "event: closed\\n"])
                        self.assertTrue(writer.flushed)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("event_writer")

            assert getattr(mod.EventWriter, "_is_runtime_protocol", False), "EventWriter must be runtime-checkable"

            class RecordingWriter:
                def __init__(self):
                    self.messages = []
                    self.flush_calls = 0

                def write(self, message: str) -> int:
                    self.messages.append(message)
                    return len(message)

                def flush(self) -> None:
                    self.flush_calls += 1

            recorder = RecordingWriter()
            assert isinstance(recorder, mod.EventWriter), "foreign structural writer should satisfy EventWriter"

            returned = mod.publish_events(["alpha", "beta"], recorder)
            assert returned is recorder
            assert recorder.messages == ["event: alpha\\n", "event: beta\\n"]
            assert recorder.flush_calls == 1, "publish_events should flush once after writing all events"

            memory = mod.MemoryEventWriter()
            assert isinstance(memory, mod.EventWriter)
            assert memory.write("direct\\n") == len("direct\\n")
            assert memory.messages == ["direct\\n"]
            memory.flush()
            assert memory.flushed is True

            class PartialWriter:
                def write(self, message: str) -> int:
                    return len(message)

            assert not isinstance(PartialWriter(), mod.EventWriter), "flush must remain part of the protocol"

            source = (ROOT / "src" / "event_writer.py").read_text(encoding="utf-8")
            assert "Protocol" in source
            assert "@runtime_checkable" in source
        """),
    },
    {
        "task_id": "HARD-026",
        "category": "multi_turn_change",
        "repo_hint": "python/rules_engine",
        "instruction": "First add priority-based rule resolution; then preserve the legacy first-match fallback for rules that do not declare a priority.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/rules_engine.py": """
                def evaluate(record, rules, default=None):
                    for rule in rules:
                        conditions = rule.get("conditions", {})
                        if all(record.get(key) == value for key, value in conditions.items()):
                            return rule.get("result")
                    return default
            """,
            "tests/test_rules_engine.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from rules_engine import evaluate


                class RulesEngineTest(unittest.TestCase):
                    def test_highest_priority_matching_rule_wins(self):
                        rules = [
                            {"conditions": {"country": "US"}, "result": "review", "priority": 1},
                            {"conditions": {"country": "US", "amount": 5000}, "result": "block", "priority": 10},
                        ]
                        self.assertEqual(evaluate({"country": "US", "amount": 5000}, rules), "block")

                    def test_legacy_rule_is_fallback_when_no_priority_rule_matches(self):
                        rules = [
                            {"conditions": {"country": "US"}, "result": "legacy-review"},
                            {"conditions": {"country": "CA"}, "result": "priority-review", "priority": 5},
                        ]
                        self.assertEqual(evaluate({"country": "US"}, rules), "legacy-review")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("rules_engine")

            rules = [
                {"name": "legacy-catchall", "conditions": {}, "result": "legacy-review"},
                {"name": "low-risk", "conditions": {"type": "transfer"}, "result": "allow", "priority": 1},
                {"name": "high-risk", "conditions": {"type": "transfer", "amount": 9000}, "result": "block", "priority": 50},
            ]
            assert mod.evaluate({"type": "transfer", "amount": 9000}, rules, default="manual") == "block"

            tie_rules = [
                {"conditions": {"segment": "vip"}, "result": "first", "priority": 7},
                {"conditions": {"segment": "vip"}, "result": "second", "priority": 7},
            ]
            assert mod.evaluate({"segment": "vip"}, tie_rules) == "first"

            zero_priority_rules = [
                {"conditions": {"region": "EU"}, "result": "legacy-fallback"},
                {"conditions": {"region": "EU"}, "result": "explicit-zero", "priority": 0},
            ]
            assert mod.evaluate({"region": "EU"}, zero_priority_rules) == "explicit-zero"

            negative_priority_rules = [
                {"conditions": {"kind": "login"}, "result": "legacy-login"},
                {"conditions": {"kind": "login"}, "result": "priority-negative", "priority": -5},
            ]
            assert mod.evaluate({"kind": "login"}, negative_priority_rules) == "priority-negative"

            fallback_rules = [
                {"conditions": {"country": "US"}, "result": "legacy-us"},
                {"conditions": {"country": "CA"}, "result": "priority-ca", "priority": 20},
            ]
            assert mod.evaluate({"country": "US"}, fallback_rules, default="manual") == "legacy-us"
            assert mod.evaluate({"country": "MX"}, fallback_rules, default="manual") == "manual"

            mutation_rules = [
                {"conditions": {"status": "new"}, "result": "legacy-new"},
                {"conditions": {"status": "new"}, "result": "priority-new", "priority": 3},
            ]
            snapshot = [dict(rule) for rule in mutation_rules]
            assert mod.evaluate({"status": "new"}, mutation_rules) == "priority-new"
            assert mutation_rules == snapshot
        """),
    },
    {
        "task_id": "HARD-027",
        "category": "dependency_friction",
        "repo_hint": "typescript/date_formatter",
        "instruction": "Fix the date formatter so it no longer depends on external date libraries. It must format dates deterministically using the built-in runtime only, support UTC-based formatting with optional fixed timezone offsets, handle literals, and raise DateFormatError for invalid dates.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "src/dateFormatter.mjs": """
                import { format } from 'date-fns';

                export class DateFormatError extends Error {}

                export function formatDate(input, pattern = 'YYYY-MM-DD', options = {}) {
                  const date = input instanceof Date ? input : new Date(input);
                  if (Number.isNaN(date.getTime())) {
                    throw new DateFormatError(`invalid date: ${input}`);
                  }
                  return format(date, pattern, options);
                }
            """,
            "tests/date-formatter.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { DateFormatError, formatDate } from '../src/dateFormatter.mjs';

                test('formats a UTC ISO timestamp with numeric tokens', () => {
                  assert.equal(
                    formatDate('2026-02-03T04:05:06Z', 'YYYY-MM-DD HH:mm:ss'),
                    '2026-02-03 04:05:06'
                  );
                });

                test('zero-pads single-digit fields', () => {
                  assert.equal(
                    formatDate(new Date(Date.UTC(2026, 0, 2, 3, 4, 5)), 'YYYY/MM/DD HH:mm:ss'),
                    '2026/01/02 03:04:05'
                  );
                });

                test('applies a fixed timezone offset and prints Z', () => {
                  assert.equal(
                    formatDate('2026-01-01T23:30:00Z', 'YYYY-MM-DD HH:mm Z', {
                      timeZoneOffsetMinutes: 330,
                    }),
                    '2026-01-02 05:00 +05:30'
                  );
                });

                test('rejects invalid dates with DateFormatError', () => {
                  assert.throws(
                    () => formatDate('not-a-date', 'YYYY-MM-DD'),
                    error => error instanceof DateFormatError && /invalid/i.test(error.message)
                  );
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);

            const fs = await import('node:fs/promises');
            const { DateFormatError, formatDate } = await loadModule('src/dateFormatter.mjs');

            assert.equal(
              formatDate('2026-06-07T16:08:09Z', 'ddd, MMM DD, YYYY [at] HH:mm:ss Z'),
              'Sun, Jun 07, 2026 at 16:08:09 +00:00'
            );

            assert.equal(
              formatDate('2026-03-01T01:15:00Z', 'YYYY-MM-DD HH:mm Z', {
                timeZoneOffsetMinutes: -300,
              }),
              '2026-02-28 20:15 -05:00'
            );

            assert.equal(
              formatDate(1777777777000, 'YYYY-MM-DD HH:mm:ss'),
              '2026-05-02 22:49:37'
            );

            const original = new Date(Date.UTC(2026, 11, 31, 23, 59, 58));
            assert.equal(formatDate(original, 'YYYY-MM-DD HH:mm:ss'), '2026-12-31 23:59:58');
            assert.equal(original.getUTCFullYear(), 2026, 'input Date must not be mutated');

            assert.throws(
              () => formatDate(new Date('bad'), 'YYYY-MM-DD'),
              error => error instanceof DateFormatError && /invalid date/i.test(error.message)
            );

            const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8'));
            assert.deepEqual(pkg.dependencies ?? {}, {}, 'fixture solution must not add runtime dependencies');
            assert.deepEqual(pkg.devDependencies ?? {}, {}, 'fixture solution must not add dev dependencies');

            const source = await fs.readFile(path.join(root, 'src/dateFormatter.mjs'), 'utf8');
            assert.ok(
              !/from\\s+['"](date-fns|moment|luxon|dayjs)['"]|require\\(['"](date-fns|moment|luxon|dayjs)['"]\\)/.test(source),
              'solution must not import external date libraries'
            );
        """),
    },
    {
        "task_id": "HARD-028",
        "category": "bug_fix",
        "repo_hint": "python/path_normalizer",
        "instruction": "Fix path normalization so it handles POSIX and Windows-style separators, resolves dot segments lexically, preserves absolute roots and Windows drive or UNC roots, and returns deterministic forward-slash output without using platform-dependent behavior.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "src/path_normalizer.py": """
                def normalize_path(path):
                    text = str(path)
                    parts = []
                    for part in text.split("/"):
                        if part in ("", "."):
                            continue
                        if part == "..":
                            if parts:
                                parts.pop()
                            continue
                        parts.append(part)
                    return "/".join(parts) or "."
            """,
            "tests/test_path_normalizer.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from path_normalizer import normalize_path


                class PathNormalizerTest(unittest.TestCase):
                    def test_collapses_posix_separators_and_current_dir(self):
                        self.assertEqual(normalize_path("docs//./guide.md"), "docs/guide.md")

                    def test_resolves_relative_parent(self):
                        self.assertEqual(normalize_path("docs/api/../index.md"), "docs/index.md")

                    def test_empty_path_is_current_directory(self):
                        self.assertEqual(normalize_path(""), ".")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader(r"""
            run_visible_tests()
            mod = importlib.import_module("path_normalizer")

            assert mod.normalize_path(r"logs\\2026\\..\\latest\\run.txt") == "logs/latest/run.txt"
            assert mod.normalize_path(r"C:\\Users\\Ada\\..\\Grace\\file.txt") == "C:/Users/Grace/file.txt"
            assert mod.normalize_path("C:/Users/./Ada/../Grace") == "C:/Users/Grace"

            assert mod.normalize_path("../src/./../README.md") == "../README.md"
            assert mod.normalize_path("a/../../b") == "../b"
            assert mod.normalize_path("././") == "."

            assert mod.normalize_path("/var//log/../tmp/") == "/var/tmp"
            assert mod.normalize_path("/../etc") == "/etc"
            assert mod.normalize_path("/") == "/"

            assert mod.normalize_path(r"C:\\..\\Windows") == "C:/Windows"
            assert mod.normalize_path(r"\\\\server\\share\\folder\\..\\file.txt") == "//server/share/file.txt"
            assert mod.normalize_path(r"\\\\server\\share\\..\\other") == "//server/share/other"
        """),
    },
    {
        "task_id": "HARD-029",
        "category": "refactor",
        "repo_hint": "typescript/validation_pipeline",
        "instruction": "Refactor the registration validation pipeline so it accumulates every validation error in a stable field order instead of stopping at the first failure, while preserving the public validateRegistration(input) API, valid-user normalization, and input immutability.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "README.md": """
                # validation-pipeline

                `validateRegistration(input)` returns `{ valid, errors, value }`.

                Validation order is `email`, `password`, `roles`.

                Rules:

                - `email` is required and must contain `@`.
                - `password` is required and must be at least 8 characters.
                - `roles` must be a non-empty array.
                - Valid output normalizes email by trimming and lowercasing it.
                - Invalid output keeps `value` as `null` and reports all errors in validation order.
            """,
            "src/validationPipeline.mjs": """
                export function validateRegistration(input) {
                  const data = input ?? {};

                  if (!data.email || !String(data.email).includes('@')) {
                    return invalid('email', 'invalid_email', 'email must contain @');
                  }

                  if (!data.password || String(data.password).length < 8) {
                    return invalid('password', 'weak_password', 'password must be at least 8 characters');
                  }

                  if (!Array.isArray(data.roles) || data.roles.length === 0) {
                    return invalid('roles', 'missing_roles', 'at least one role is required');
                  }

                  return {
                    valid: true,
                    errors: [],
                    value: {
                      email: String(data.email).trim().toLowerCase(),
                      password: data.password,
                      roles: [...data.roles],
                    },
                  };
                }

                function invalid(field, code, message) {
                  return {
                    valid: false,
                    errors: [{ field, code, message }],
                    value: null,
                  };
                }
            """,
            "tests/validation-pipeline.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { validateRegistration } from '../src/validationPipeline.mjs';

                test('normalizes valid registrations', () => {
                  const result = validateRegistration({
                    email: '  ADA@EXAMPLE.COM  ',
                    password: 'correct horse',
                    roles: ['admin'],
                  });

                  assert.equal(result.valid, true);
                  assert.deepEqual(result.errors, []);
                  assert.deepEqual(result.value, {
                    email: 'ada@example.com',
                    password: 'correct horse',
                    roles: ['admin'],
                  });
                });

                test('reports an invalid email', () => {
                  const result = validateRegistration({
                    email: 'ada.example.com',
                    password: 'correct horse',
                    roles: ['admin'],
                  });

                  assert.equal(result.valid, false);
                  assert.equal(result.errors[0].field, 'email');
                  assert.equal(result.errors[0].code, 'invalid_email');
                  assert.equal(result.value, null);
                });

                test('reports a weak password', () => {
                  const result = validateRegistration({
                    email: 'ada@example.com',
                    password: 'short',
                    roles: ['admin'],
                  });

                  assert.equal(result.valid, false);
                  assert.equal(result.errors[0].field, 'password');
                  assert.equal(result.errors[0].code, 'weak_password');
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);

            const { validateRegistration } = await loadModule('src/validationPipeline.mjs');

            const invalidAll = validateRegistration({
              email: 'ada.example.com',
              password: 'short',
              roles: [],
            });
            assert.equal(invalidAll.valid, false);
            assert.equal(invalidAll.value, null);
            assert.deepEqual(
              invalidAll.errors.map(error => [error.field, error.code]),
              [
                ['email', 'invalid_email'],
                ['password', 'weak_password'],
                ['roles', 'missing_roles'],
              ],
              'validation should accumulate every error in stable field order'
            );

            const missingAll = validateRegistration({});
            assert.deepEqual(
              missingAll.errors.map(error => error.field),
              ['email', 'password', 'roles']
            );

            const source = Object.freeze({
              email: '  GRACE@EXAMPLE.COM  ',
              password: 'long-enough',
              roles: Object.freeze(['editor']),
            });
            const valid = validateRegistration(source);
            assert.equal(valid.valid, true);
            assert.deepEqual(valid.value, {
              email: 'grace@example.com',
              password: 'long-enough',
              roles: ['editor'],
            });
            assert.notStrictEqual(valid.value.roles, source.roles, 'roles should be copied');
            assert.deepEqual(source, {
              email: '  GRACE@EXAMPLE.COM  ',
              password: 'long-enough',
              roles: ['editor'],
            });

            const mixed = validateRegistration({
              email: 'linus@example.com',
              password: 'tiny',
              roles: [],
            });
            assert.deepEqual(
              mixed.errors.map(error => error.field),
              ['password', 'roles'],
              'later validators should still run when an earlier one passes'
            );
        """),
    },
    {
        "task_id": "HARD-030",
        "category": "error_localization",
        "repo_hint": "python/template_renderer",
        "instruction": "Use the traceback and README contract to fix the template renderer. Preserve render_template(template, context), support documented placeholder rendering, and report template failures through TemplateRenderError with actionable diagnostics.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # template-renderer

                `render_template(template, context)` renders placeholders using values from `context`.

                Syntax:

                - `{name}` inserts `str(context["name"])`.
                - Placeholder names contain letters, digits, and underscores, and must not start with a digit.
                - `{{` renders a literal `{`.
                - `}}` renders a literal `}`.
                - Missing variables raise `TemplateRenderError` with the missing variable name and its line/column location.
            """,
            "src/template_renderer.py": """
                import re


                class TemplateRenderError(Exception):
                    pass


                def render_template(template, context):
                    def replace(match):
                        name = match.group(1)
                        try:
                            return str(context[name])
                        except KeyError as exc:
                            raise TemplateRenderError(f"missing variable {name}") from exc

                    return re.sub(r"{([A-Za-z_][A-Za-z0-9_]*)}", replace, template)
            """,
            "tests/test_template_renderer.py": """
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
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("template_renderer")

            assert mod.render_template(
                "{{greeting}}, {name}!",
                {"greeting": "HELLO", "name": "Ada"},
            ) == "{greeting}, Ada!"

            assert mod.render_template(
                "Use {{ and }} around {word}.",
                {"word": "tokens"},
            ) == "Use { and } around tokens."

            assert mod.render_template(
                "{{{name}}}",
                {"name": "Ada"},
            ) == "{Ada}"

            assert mod.render_template(
                "{zero} {false} {none}",
                {"zero": 0, "false": False, "none": None},
            ) == "0 False None"

            try:
                mod.render_template("Line 1\\nHello {user}\\nBye", {})
            except mod.TemplateRenderError as exc:
                message = str(exc).lower()
                assert "user" in message
                assert "line 2" in message or "line: 2" in message
                assert "column 7" in message or "col 7" in message or "column: 7" in message
            else:
                raise AssertionError("missing variables should raise TemplateRenderError")
        """),
    },
    {
        "task_id": "HARD-031",
        "category": "multi_turn_tool_debug",
        "repo_hint": "python/env_manifest_resolver",
        "instruction": "Fix the environment manifest resolver so the CLI produces the same resolved JSON whether it is run from the repo root or a nested directory. Preserve documented precedence: defaults < .env < .env.local < explicit --set KEY=VALUE. Empty values in .env.local should not erase existing values unless passed explicitly with --set.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # env-manifest-resolver

                Resolve deployment environment values from a manifest and local
                env files.

                CLI:

                ```bash
                python -m env_manifest_resolver.cli fixtures/app/manifest.json --set KEY=VALUE
                ```

                Precedence is:

                1. manifest `defaults`
                2. `.env` next to the manifest
                3. `.env.local` next to the manifest
                4. explicit `--set KEY=VALUE`

                Blank values in `.env.local` are ignored so local placeholder
                lines do not erase shared `.env` values. Blank values passed
                with `--set KEY=` are explicit overrides and must be preserved.

                The CLI prints stable JSON containing every required key.
            """,
            "fixtures/app/manifest.json": """
                {
                  "required": ["API_URL", "TIMEOUT", "REGION", "FEATURE_FLAG"],
                  "defaults": {
                    "API_URL": "http://localhost:8000",
                    "TIMEOUT": "30",
                    "REGION": "us-east-1",
                    "FEATURE_FLAG": "off"
                  }
                }
            """,
            "fixtures/app/.env": """
                API_URL=https://shared.example.test
                REGION=eu-west-1
            """,
            "fixtures/app/.env.local": """
                TIMEOUT=5
                API_URL=
            """,
            "fixtures/app/services/api/README.md": """
                Nested service directory used by hidden CLI tests.
            """,
            "src/env_manifest_resolver/__init__.py": """
                from .resolver import load_manifest, resolve_manifest

                __all__ = ["load_manifest", "resolve_manifest"]
            """,
            "src/env_manifest_resolver/resolver.py": """
                import json
                from pathlib import Path


                def load_manifest(path):
                    return json.loads(Path(path).read_text(encoding="utf-8"))


                def resolve_manifest(manifest_path, overrides=None):
                    manifest = load_manifest(manifest_path)
                    base_dir = Path.cwd()
                    values = dict(manifest.get("defaults", {}))
                    values.update(_read_env_file(base_dir / ".env"))
                    values.update(_read_env_file(base_dir / ".env.local"))
                    values.update(overrides or {})
                    return {key: values.get(key, "") for key in manifest.get("required", [])}


                def _read_env_file(path):
                    if not path.exists():
                        return {}

                    result = {}
                    for raw_line in path.read_text(encoding="utf-8").splitlines():
                        line = raw_line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        key, value = line.split("=", 1)
                        result[key.strip()] = value.strip()
                    return result
            """,
            "src/env_manifest_resolver/cli.py": """
                import argparse
                import json

                from .resolver import resolve_manifest


                def main(argv=None):
                    parser = argparse.ArgumentParser()
                    parser.add_argument("manifest")
                    parser.add_argument("--set", dest="sets", action="append", default=[])
                    args = parser.parse_args(argv)

                    overrides = {}
                    for item in args.sets:
                        if "=" not in item:
                            parser.error("--set must use KEY=VALUE")
                        key, value = item.split("=", 1)
                        overrides[key] = value

                    resolved = resolve_manifest(args.manifest, overrides)
                    print(json.dumps(resolved, sort_keys=True))


                if __name__ == "__main__":
                    main()
            """,
            "tests/test_public_resolver.py": """
                import json
                import os
                import subprocess
                import sys
                import unittest
                from pathlib import Path


                ROOT = Path(__file__).resolve().parents[1]
                APP = ROOT / "fixtures" / "app"


                class EnvManifestResolverPublicTest(unittest.TestCase):
                    def run_cli(self, *args, cwd=APP):
                        env = os.environ.copy()
                        env["PYTHONPATH"] = str(ROOT / "src")
                        result = subprocess.run(
                            [sys.executable, "-m", "env_manifest_resolver.cli", *args],
                            cwd=cwd,
                            env=env,
                            text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=True,
                        )
                        return json.loads(result.stdout)

                    def test_root_cli_uses_manifest_defaults_and_env_files(self):
                        resolved = self.run_cli("manifest.json")
                        self.assertEqual(resolved["REGION"], "eu-west-1")
                        self.assertEqual(resolved["TIMEOUT"], "5")
                        self.assertEqual(resolved["FEATURE_FLAG"], "off")

                    def test_explicit_set_overrides_env_files(self):
                        resolved = self.run_cli("manifest.json", "--set", "REGION=ap-south-1")
                        self.assertEqual(resolved["REGION"], "ap-south-1")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import json
            import os
            import subprocess

            run_visible_tests()

            env = os.environ.copy()
            env["PYTHONPATH"] = str(ROOT / "src")
            app = ROOT / "fixtures" / "app"
            nested = app / "services" / "api"

            def run_cli(cwd, *args):
                result = subprocess.run(
                    [sys.executable, "-m", "env_manifest_resolver.cli", *args],
                    cwd=cwd,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                return json.loads(result.stdout)

            root_output = run_cli(app, "manifest.json")
            nested_output = run_cli(nested, "../../manifest.json")
            assert nested_output == root_output

            assert root_output["API_URL"] == "https://shared.example.test"
            assert root_output["TIMEOUT"] == "5"
            assert list(root_output.keys()) == ["API_URL", "FEATURE_FLAG", "REGION", "TIMEOUT"]

            explicit_empty = run_cli(app, "manifest.json", "--set", "API_URL=")
            assert explicit_empty["API_URL"] == ""

            explicit_nested = run_cli(nested, "../../manifest.json", "--set", "FEATURE_FLAG=on")
            assert explicit_nested["FEATURE_FLAG"] == "on"
            assert explicit_nested["API_URL"] == "https://shared.example.test"
        """),
    },
    {
        "task_id": "HARD-032",
        "category": "stateful_regression",
        "repo_hint": "typescript/undoable_queue",
        "instruction": "Fix the undoable queue so undo() and redo() preserve item metadata and queue ordering across enqueue, dequeue, and clear operations. Do not change the public API or test runner configuration.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "README.md": """
                # undoable-queue

                `UndoableQueue` is a FIFO queue with history.

                Public API:

                - `enqueue(item)`
                - `dequeue()`
                - `clear()`
                - `undo()`
                - `redo()`
                - `peek()`
                - `toArray()`
                - `size`

                Items are plain objects with at least an `id` field. Queue
                history must preserve full item metadata, keep FIFO ordering,
                and isolate snapshots from later mutations of returned values.
            """,
            "src/undoableQueue.mjs": """
                export class UndoableQueue {
                  constructor(items = []) {
                    this.items = [...items];
                    this.undoStack = [];
                    this.redoStack = [];
                  }

                  get size() {
                    return this.items.length;
                  }

                  enqueue(item) {
                    this._save();
                    this.items.push(item);
                    this.redoStack = [];
                    return this;
                  }

                  dequeue() {
                    if (this.items.length === 0) {
                      return undefined;
                    }
                    this._save();
                    this.redoStack = [];
                    return this.items.shift();
                  }

                  clear() {
                    this._save();
                    this.items = [];
                    return this;
                  }

                  undo() {
                    if (this.undoStack.length === 0) {
                      return false;
                    }
                    this.redoStack.push([...this.items]);
                    this.items = this.undoStack.pop();
                    return true;
                  }

                  redo() {
                    if (this.redoStack.length === 0) {
                      return false;
                    }
                    this.undoStack.push([...this.items]);
                    this.items = this.redoStack.pop();
                    return true;
                  }

                  peek() {
                    return this.items[0];
                  }

                  toArray() {
                    return [...this.items];
                  }

                  _save() {
                    this.undoStack.push([...this.items]);
                  }
                }
            """,
            "src/index.mjs": """
                export { UndoableQueue } from './undoableQueue.mjs';
            """,
            "tests/undoable-queue.test.mjs": """
                import assert from 'node:assert/strict';
                import { test } from 'node:test';
                import { UndoableQueue } from '../src/index.mjs';

                function ids(queue) {
                  return queue.toArray().map(item => item.id);
                }

                test('enqueues and dequeues in FIFO order', () => {
                  const queue = new UndoableQueue();
                  queue.enqueue({ id: 'a' }).enqueue({ id: 'b' });

                  assert.deepEqual(ids(queue), ['a', 'b']);
                  assert.equal(queue.dequeue().id, 'a');
                  assert.deepEqual(ids(queue), ['b']);
                });

                test('undo restores queue ids after dequeue', () => {
                  const queue = new UndoableQueue([{ id: 'a' }, { id: 'b' }]);

                  assert.equal(queue.dequeue().id, 'a');
                  assert.deepEqual(ids(queue), ['b']);
                  assert.equal(queue.undo(), true);
                  assert.deepEqual(ids(queue), ['a', 'b']);
                });

                test('redo reapplies an undone enqueue', () => {
                  const queue = new UndoableQueue([{ id: 'a' }]);

                  queue.enqueue({ id: 'b' });
                  assert.deepEqual(ids(queue), ['a', 'b']);
                  assert.equal(queue.undo(), true);
                  assert.deepEqual(ids(queue), ['a']);
                  assert.equal(queue.redo(), true);
                  assert.deepEqual(ids(queue), ['a', 'b']);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);

            const { UndoableQueue } = await loadModule('src/index.mjs');

            function snapshot(queue) {
              return queue.toArray();
            }

            const itemA = {
              id: 'a',
              priority: 2,
              source: 'api',
              audit: { createdBy: 'Ada', tags: ['hot'] },
            };
            const itemB = {
              id: 'b',
              priority: 1,
              source: 'worker',
              audit: { createdBy: 'Grace', tags: ['cold'] },
            };

            const queue = new UndoableQueue([itemA, itemB]);
            const removed = queue.dequeue();
            removed.priority = 99;
            removed.audit.tags.push('mutated');
            assert.equal(queue.undo(), true);
            assert.deepEqual(snapshot(queue), [
              {
                id: 'a',
                priority: 2,
                source: 'api',
                audit: { createdBy: 'Ada', tags: ['hot'] },
              },
              {
                id: 'b',
                priority: 1,
                source: 'worker',
                audit: { createdBy: 'Grace', tags: ['cold'] },
              },
            ]);

            const peeked = queue.peek();
            peeked.audit.createdBy = 'mutated';
            const listed = queue.toArray();
            listed[1].audit.tags.push('leaked');
            assert.deepEqual(snapshot(queue), [
              {
                id: 'a',
                priority: 2,
                source: 'api',
                audit: { createdBy: 'Ada', tags: ['hot'] },
              },
              {
                id: 'b',
                priority: 1,
                source: 'worker',
                audit: { createdBy: 'Grace', tags: ['cold'] },
              },
            ]);

            queue.clear();
            assert.equal(queue.size, 0);
            assert.equal(queue.undo(), true);
            assert.deepEqual(snapshot(queue).map(item => item.id), ['a', 'b']);
            assert.equal(queue.redo(), true);
            assert.equal(queue.size, 0);

            const ordered = new UndoableQueue();
            ordered.enqueue({ id: 'first', meta: { n: 1 } });
            ordered.enqueue({ id: 'second', meta: { n: 2 } });
            ordered.enqueue({ id: 'third', meta: { n: 3 } });
            assert.equal(ordered.dequeue().id, 'first');
            ordered.undo();
            ordered.redo();
            assert.deepEqual(ordered.toArray().map(item => item.id), ['second', 'third']);
        """),
    },
    {
        "task_id": "HARD-033",
        "category": "error_recovery",
        "repo_hint": "python/log_redactor",
        "instruction": "Fix the log redactor so it consistently redacts credentials from plain text and structured log events without mutating inputs. It must handle token, apiKey, password, and authorization values across key-value text, URL query strings, headers, and JSON-like dictionaries.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # log-redactor

                Redact credentials before logs are persisted.

                Public API:

                - `redact_text(text)`
                - `redact_event(event)`

                Sensitive fields include `token`, `apiKey`, `password`, and
                `authorization`, matched case-insensitively. Redaction should
                replace credential values with `[REDACTED]` while preserving useful
                non-sensitive context. `redact_event` must return a redacted copy
                and must not mutate the input event.
            """,
            "src/log_redactor.py": """
                import re


                SECRET = "[REDACTED]"


                def redact_text(text):
                    return re.sub(r"(token=)[^\\s&]+", r"\\1" + SECRET, str(text))


                def redact_event(event):
                    redacted = dict(event)
                    message = redacted.get("message")
                    if isinstance(message, str):
                        redacted["message"] = redact_text(message)
                    return redacted
            """,
            "tests/test_log_redactor.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from log_redactor import SECRET, redact_event, redact_text


                class LogRedactorTest(unittest.TestCase):
                    def test_redacts_plain_token_value(self):
                        self.assertEqual(
                            redact_text("login token=abc123 user=ada"),
                            f"login token={SECRET} user=ada",
                        )

                    def test_redacts_token_in_event_message(self):
                        event = {"level": "info", "message": "token=abc123 accepted"}

                        redacted = redact_event(event)

                        self.assertEqual(redacted["message"], f"token={SECRET} accepted")
                        self.assertEqual(event["message"], "token=abc123 accepted")


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("log_redactor")
            replacement = mod.SECRET

            assert mod.redact_text("password=hunter2 token=abc") == f"password={replacement} token={replacement}"
            assert mod.redact_text("GET /v1?apiKey=key-123&query=ok") == f"GET /v1?apiKey={replacement}&query=ok"
            assert mod.redact_text("Authorization: Bearer sk-live-123") == f"Authorization: Bearer {replacement}"
            assert mod.redact_text("AUTHORIZATION=Basic abcdef") == f"AUTHORIZATION=Basic {replacement}"

            original = {
                "level": "info",
                "message": "request password=hunter2",
                "headers": {
                    "Authorization": "Bearer sk-live-123",
                    "X-Trace": "keep-me",
                },
                "context": {
                    "apiKey": "key-123",
                    "nested": [{"Password": "credential"}, {"safe": "value"}],
                },
            }
            expected_original = {
                "level": "info",
                "message": "request password=hunter2",
                "headers": {
                    "Authorization": "Bearer sk-live-123",
                    "X-Trace": "keep-me",
                },
                "context": {
                    "apiKey": "key-123",
                    "nested": [{"Password": "credential"}, {"safe": "value"}],
                },
            }

            redacted = mod.redact_event(original)
            assert redacted["message"] == f"request password={replacement}"
            assert redacted["headers"]["Authorization"] == f"Bearer {replacement}"
            assert redacted["headers"]["X-Trace"] == "keep-me"
            assert redacted["context"]["apiKey"] == replacement
            assert redacted["context"]["nested"][0]["Password"] == replacement
            assert redacted["context"]["nested"][1]["safe"] == "value"
            assert original == expected_original

            assert mod.redact_event({"token": "abc", "user": "ada"}) == {
                "token": replacement,
                "user": "ada",
            }
        """),
    },
    {
        "task_id": "HARD-034",
        "category": "multi_turn_change",
        "repo_hint": "python/feature_flags",
        "instruction": "Extend the feature flag evaluator so it preserves the existing enabled/default behavior while adding deterministic percentage rollouts and user allow/deny overrides. The evaluator must be stable across processes, preserve input configuration, and keep evaluate_flag(config, flag_name, user) as the public API.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # feature-flags

                `evaluate_flag(config, flag_name, user)` decides whether a
                feature flag is enabled for a user.

                Current behavior:

                - Missing flags return `config["default"]` when present.
                - Boolean `enabled` controls simple flags.

                Required extension:

                - `allow_users` always enables listed users.
                - `deny_users` always disables listed users.
                - `rollout` is an integer percentage from 0 to 100.
                - Rollout decisions must be deterministic across processes.
                - The input config and user dictionaries must not be mutated.
            """,
            "src/feature_flags.py": """
                def evaluate_flag(config, flag_name, user):
                    flags = config.get("flags", {})
                    if flag_name not in flags:
                        return bool(config.get("default", False))

                    flag = flags[flag_name]
                    if "enabled" in flag:
                        return bool(flag["enabled"])

                    return bool(config.get("default", False))
            """,
            "tests/test_feature_flags.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from feature_flags import evaluate_flag


                class FeatureFlagsTest(unittest.TestCase):
                    def test_enabled_flag_returns_true(self):
                        config = {"flags": {"new_nav": {"enabled": True}}}

                        self.assertTrue(evaluate_flag(config, "new_nav", {"id": "ada"}))

                    def test_disabled_flag_returns_false(self):
                        config = {"flags": {"new_nav": {"enabled": False}}}

                        self.assertFalse(evaluate_flag(config, "new_nav", {"id": "ada"}))

                    def test_missing_flag_uses_default(self):
                        config = {"default": True, "flags": {}}

                        self.assertTrue(evaluate_flag(config, "missing", {"id": "ada"}))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy
            import hashlib

            run_visible_tests()
            mod = importlib.import_module("feature_flags")

            config = {
                "default": False,
                "flags": {
                    "search_v2": {
                        "enabled": True,
                        "rollout": 25,
                        "allow_users": ["ada"],
                        "deny_users": ["mallory"],
                    },
                    "checkout_v2": {
                        "rollout": 0,
                        "allow_users": ["grace"],
                    },
                    "feed_v2": {
                        "rollout": 100,
                        "deny_users": ["linus"],
                    },
                },
            }
            original = copy.deepcopy(config)

            assert mod.evaluate_flag(config, "search_v2", {"id": "ada"}) is True
            assert mod.evaluate_flag(config, "search_v2", {"id": "mallory"}) is False
            assert mod.evaluate_flag(config, "checkout_v2", {"id": "grace"}) is True
            assert mod.evaluate_flag(config, "checkout_v2", {"id": "random"}) is False
            assert mod.evaluate_flag(config, "feed_v2", {"id": "linus"}) is False
            assert mod.evaluate_flag(config, "feed_v2", {"id": "anyone"}) is True

            def bucket(flag_name, user_id):
                digest = hashlib.sha256(f"{flag_name}:{user_id}".encode("utf-8")).hexdigest()
                return int(digest[:8], 16) % 100

            users = [
                {"id": "user-001"},
                {"id": "user-017"},
                {"id": "user-042"},
                {"id": "user-099"},
            ]
            for user in users:
                expected = bucket("search_v2", user["id"]) < 25
                assert mod.evaluate_flag(config, "search_v2", user) is expected

            assert mod.evaluate_flag(config, "missing", {"id": "ada"}) is False
            assert config == original

            user = {"id": "ada", "groups": ["staff"]}
            before_user = copy.deepcopy(user)
            mod.evaluate_flag(config, "search_v2", user)
            assert user == before_user
        """),
    },
    {
        "task_id": "HARD-035",
        "category": "dependency_friction",
        "repo_hint": "python/retry_policy",
        "instruction": "Fix the HTTP retry policy so it preserves the existing exponential backoff behavior while respecting retryable status codes, Retry-After headers, maximum delay caps, and input immutability. Use only the Python standard library.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # retry-policy

                `plan_retries(response, attempts, base_delay=1, max_delay=None)`
                returns retry delays in seconds.

                Existing behavior:

                - Exponential backoff starts at `base_delay`.
                - `attempts=3` with `base_delay=1` returns `[1, 2, 4]`.

                Required behavior:

                - Retry only status `408`, `409`, `425`, `429`, and `5xx`.
                - Non-retryable statuses return `[]`.
                - `Retry-After` may be seconds or an HTTP-date.
                - `max_delay` caps every planned delay.
                - The response dictionary must not be mutated.
            """,
            "src/retry_policy.py": """
                def plan_retries(response, attempts, base_delay=1, max_delay=None):
                    delays = []
                    for attempt in range(attempts):
                        delay = base_delay * (2 ** attempt)
                        if max_delay is not None and delay > max_delay:
                            delay = max_delay
                        delays.append(delay)
                    return delays
            """,
            "tests/test_retry_policy.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from retry_policy import plan_retries


                class RetryPolicyTest(unittest.TestCase):
                    def test_exponential_backoff(self):
                        response = {"status": 503, "headers": {}}

                        self.assertEqual(plan_retries(response, attempts=3), [1, 2, 4])

                    def test_base_delay_is_configurable(self):
                        response = {"status": 503, "headers": {}}

                        self.assertEqual(plan_retries(response, attempts=2, base_delay=3), [3, 6])

                    def test_zero_attempts_returns_empty_plan(self):
                        response = {"status": 503, "headers": {}}

                        self.assertEqual(plan_retries(response, attempts=0), [])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy
            import datetime as dt
            import email.utils

            run_visible_tests()
            mod = importlib.import_module("retry_policy")

            assert mod.plan_retries({"status": 400, "headers": {}}, attempts=3) == []
            assert mod.plan_retries({"status": 404, "headers": {}}, attempts=3) == []
            assert mod.plan_retries({"status": 409, "headers": {}}, attempts=2) == [1, 2]
            assert mod.plan_retries({"status": 500, "headers": {}}, attempts=3, max_delay=2) == [1, 2, 2]

            response = {"status": 429, "headers": {"Retry-After": "7"}}
            original = copy.deepcopy(response)
            assert mod.plan_retries(response, attempts=3) == [7, 14, 28]
            assert response == original

            future = dt.datetime.now(dt.timezone.utc) + dt.timedelta(seconds=11)
            header_date = email.utils.format_datetime(future, usegmt=True)
            planned = mod.plan_retries(
                {"status": 503, "headers": {"retry-after": header_date}},
                attempts=2,
                max_delay=20,
            )
            assert len(planned) == 2
            assert 1 <= planned[0] <= 12
            assert planned[1] == min(planned[0] * 2, 20)

            assert mod.plan_retries(
                {"status": 408, "headers": {"Retry-After": "999"}},
                attempts=2,
                max_delay=30,
            ) == [30, 30]
        """),
    },
    {
        "task_id": "HARD-036",
        "category": "feature",
        "repo_hint": "typescript/metrics_window",
        "instruction": "Fix the metrics window summarizer so it computes stable rolling statistics for a time window. Preserve summarizeWindow(events, now, windowMs), include events at the lower bound, handle unsorted input without mutating it, return zeroed empty-window stats, and compute p95 latency deterministically.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "README.md": """
                # metrics-window

                `summarizeWindow(events, now, windowMs)` returns rolling
                service metrics for events inside a time window.

                Each event has:

                - `timestamp`: epoch milliseconds
                - `latencyMs`: request latency
                - `ok`: whether the request succeeded

                Required output:

                - `count`: number of events in the window
                - `averageLatency`: arithmetic mean latency
                - `p95Latency`: nearest-rank 95th percentile latency
                - `errorRate`: failed events divided by count

                The window includes timestamps from `now - windowMs` through
                `now`, inclusive. Future events are excluded. Empty windows
                return zeroes.
            """,
            "src/metricsWindow.mjs": """
                export function summarizeWindow(events, now, windowMs) {
                  const recent = events.filter(
                    (event) => event.timestamp > now - windowMs && event.timestamp <= now,
                  );
                  const count = recent.length;
                  if (count === 0) {
                    return {
                      count: 0,
                      averageLatency: 0,
                      p95Latency: 0,
                      errorRate: 0,
                    };
                  }

                  const totalLatency = recent.reduce((sum, event) => sum + event.latencyMs, 0);
                  const failures = recent.filter((event) => event.ok === false).length;

                  return {
                    count,
                    averageLatency: totalLatency / count,
                    p95Latency: Math.max(...recent.map((event) => event.latencyMs)),
                    errorRate: failures / count,
                  };
                }
            """,
            "src/index.mjs": """
                export { summarizeWindow } from './metricsWindow.mjs';
            """,
            "tests/metricsWindow.test.mjs": """
                import assert from 'node:assert/strict';
                import test from 'node:test';
                import { summarizeWindow } from '../src/metricsWindow.mjs';

                test('returns zeroes for an empty window', () => {
                  assert.deepEqual(summarizeWindow([], 1_000, 100), {
                    count: 0,
                    averageLatency: 0,
                    p95Latency: 0,
                    errorRate: 0,
                  });
                });

                test('summarizes recent events', () => {
                  const events = [
                    { timestamp: 920, latencyMs: 100, ok: true },
                    { timestamp: 950, latencyMs: 200, ok: false },
                    { timestamp: 990, latencyMs: 300, ok: true },
                    { timestamp: 1_100, latencyMs: 900, ok: false },
                    { timestamp: 500, latencyMs: 50, ok: true },
                  ];

                  assert.deepEqual(summarizeWindow(events, 1_000, 100), {
                    count: 3,
                    averageLatency: 200,
                    p95Latency: 300,
                    errorRate: 1 / 3,
                  });
                });

                test('ignores future events', () => {
                  const events = [
                    { timestamp: 1_000, latencyMs: 125, ok: true },
                    { timestamp: 1_001, latencyMs: 999, ok: false },
                  ];

                  assert.deepEqual(summarizeWindow(events, 1_000, 10), {
                    count: 1,
                    averageLatency: 125,
                    p95Latency: 125,
                    errorRate: 0,
                  });
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { summarizeWindow } = await loadModule('src/metricsWindow.mjs');

            const now = 10_000;
            const windowMs = 1_000;
            const events = [
              { timestamp: 9_500, latencyMs: 18, ok: true },
              { timestamp: 9_000, latencyMs: 12, ok: false },
              { timestamp: 9_100, latencyMs: 1, ok: true },
              { timestamp: 9_200, latencyMs: 2, ok: true },
              { timestamp: 9_300, latencyMs: 3, ok: true },
              { timestamp: 9_400, latencyMs: 4, ok: true },
              { timestamp: 9_600, latencyMs: 5, ok: true },
              { timestamp: 9_700, latencyMs: 6, ok: false },
              { timestamp: 9_800, latencyMs: 7, ok: true },
              { timestamp: 9_900, latencyMs: 8, ok: true },
              { timestamp: 10_000, latencyMs: 9, ok: true },
              { timestamp: 9_050, latencyMs: 10, ok: true },
              { timestamp: 9_150, latencyMs: 11, ok: true },
              { timestamp: 9_250, latencyMs: 13, ok: true },
              { timestamp: 9_350, latencyMs: 14, ok: true },
              { timestamp: 9_450, latencyMs: 15, ok: true },
              { timestamp: 9_550, latencyMs: 16, ok: true },
              { timestamp: 9_650, latencyMs: 17, ok: false },
              { timestamp: 9_750, latencyMs: 19, ok: true },
              { timestamp: 9_850, latencyMs: 20, ok: true },
              { timestamp: 10_001, latencyMs: 5_000, ok: false },
              { timestamp: 8_999, latencyMs: 7_000, ok: false },
            ];
            const before = JSON.stringify(events);
            const result = summarizeWindow(events, now, windowMs);
            assert.equal(JSON.stringify(events), before);
            assert.deepEqual(result, {
              count: 20,
              averageLatency: 10.5,
              p95Latency: 19,
              errorRate: 3 / 20,
            });

            assert.deepEqual(summarizeWindow(events, 20_000, 10), {
              count: 0,
              averageLatency: 0,
              p95Latency: 0,
              errorRate: 0,
            });

            assert.deepEqual(
              summarizeWindow([{ timestamp: 100, latencyMs: 33, ok: false }], 100, 0),
              {
                count: 1,
                averageLatency: 33,
                p95Latency: 33,
                errorRate: 1,
              },
            );
        """),
    },
    {
        "task_id": "HARD-037",
        "category": "stateful_regression",
        "repo_hint": "python/sliding_limiter",
        "instruction": "Fix the sliding-window limiter so allow(user_id, now=None) enforces a rolling time window per user, prunes expired events, preserves independent user state, treats boundary timestamps as expired, and keeps using the injected clock when now is omitted. Rejected requests must not be recorded.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # sliding-limiter

                `SlidingLimiter(limit, window_seconds, clock=None)` decides
                whether a user may perform another action.

                Public API:

                - `allow(user_id, now=None)` returns `True` when the request is
                  accepted and `False` when it is rate-limited.
                - If `now` is omitted, the limiter must call the injected
                  `clock` exactly once for that decision.
                - The rolling window is per user.
                - Events at exactly `now - window_seconds` are expired.
                - Rejected requests must not be recorded.
            """,
            "src/sliding_limiter.py": """
                import time


                class SlidingLimiter:
                    def __init__(self, limit, window_seconds, clock=None):
                        self.limit = limit
                        self.window_seconds = window_seconds
                        self.clock = clock or time.time
                        self._bucket = None
                        self._count = 0

                    def allow(self, user_id, now=None):
                        if now is None:
                            now = self.clock()
                        bucket = int(now // self.window_seconds)
                        if bucket != self._bucket:
                            self._bucket = bucket
                            self._count = 0
                        if self._count >= self.limit:
                            return False
                        self._count += 1
                        return True
            """,
            "tests/test_sliding_limiter.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from sliding_limiter import SlidingLimiter


                class SlidingLimiterTest(unittest.TestCase):
                    def test_allows_until_limit(self):
                        limiter = SlidingLimiter(limit=2, window_seconds=10)

                        self.assertTrue(limiter.allow("ada", now=100))
                        self.assertTrue(limiter.allow("ada", now=101))
                        self.assertFalse(limiter.allow("ada", now=102))

                    def test_new_window_allows_again(self):
                        limiter = SlidingLimiter(limit=1, window_seconds=10)

                        self.assertTrue(limiter.allow("ada", now=100))
                        self.assertFalse(limiter.allow("ada", now=101))
                        self.assertTrue(limiter.allow("ada", now=110))

                    def test_uses_clock_when_now_is_omitted(self):
                        values = iter([200])
                        limiter = SlidingLimiter(limit=1, window_seconds=10, clock=lambda: next(values))

                        self.assertTrue(limiter.allow("ada"))


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("sliding_limiter")

            limiter = mod.SlidingLimiter(limit=2, window_seconds=10)
            assert limiter.allow("ada", now=100.0) is True
            assert limiter.allow("ada", now=109.9) is True
            assert limiter.allow("ada", now=110.0) is True
            assert limiter.allow("ada", now=110.1) is False

            limiter = mod.SlidingLimiter(limit=1, window_seconds=5)
            assert limiter.allow("ada", now=10.0) is True
            assert limiter.allow("grace", now=10.1) is True
            assert limiter.allow("ada", now=10.2) is False
            assert limiter.allow("grace", now=10.3) is False

            limiter = mod.SlidingLimiter(limit=2, window_seconds=10)
            assert limiter.allow("ada", now=50.0) is True
            assert limiter.allow("ada", now=51.0) is True
            assert limiter.allow("ada", now=51.5) is False
            assert limiter.allow("ada", now=60.0) is True
            assert limiter.allow("ada", now=60.1) is False

            calls = []
            times = iter([1.0, 2.0, 12.1])

            def clock():
                calls.append("tick")
                return next(times)

            limiter = mod.SlidingLimiter(limit=2, window_seconds=10, clock=clock)
            assert limiter.allow("linus") is True
            assert limiter.allow("linus") is True
            assert limiter.allow("linus") is True
            assert calls == ["tick", "tick", "tick"]

            limiter = mod.SlidingLimiter(limit=1, window_seconds=1)
            assert limiter.allow("ada", now=0.0) is True
            assert limiter.allow("ada", now=1_000.0) is True
            state = getattr(limiter, "_events", None)
            if state is not None:
                assert len(state.get("ada", [])) <= 1
        """),
    },
    {
        "task_id": "HARD-038",
        "category": "error_localization",
        "repo_hint": "typescript/source_map_ranges",
        "instruction": "Fix source-position mapping so generated line and column ranges map to original positions using the nearest preceding mapping segment, support multi-line generated ranges, preserve zero-based columns, and raise SourceMapError with useful diagnostics for malformed mappings. Preserve mapRange(map, start, end).",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "README.md": """
                # source-map-ranges

                `mapRange(map, start, end)` maps a generated source range back
                to original source positions.

                The map has a `mappings` array. Each mapping contains:

                - `generated`: `{ line, column }`
                - `original`: `{ source, line, column }`

                Lines are one-based and columns are zero-based. For a generated
                position, use the nearest preceding mapping segment on the same
                generated line. Ranges may span more than one generated line.
                Malformed mapping entries should raise `SourceMapError` with a
                message that helps locate the bad entry.
            """,
            "src/sourceMapRanges.mjs": """
                export class SourceMapError extends Error {
                  constructor(message) {
                    super(message);
                    this.name = 'SourceMapError';
                  }
                }

                export function mapRange(map, start, end) {
                  const startOriginal = findExact(map.mappings, start);
                  const endOriginal = findExact(map.mappings, end);
                  if (!startOriginal || !endOriginal) {
                    return null;
                  }
                  return {
                    source: startOriginal.source,
                    start: {
                      line: startOriginal.line,
                      column: startOriginal.column + 1,
                    },
                    end: {
                      line: endOriginal.line,
                      column: endOriginal.column + 1,
                    },
                  };
                }

                function findExact(mappings, position) {
                  for (const entry of mappings || []) {
                    if (
                      entry.generated.line === position.line &&
                      entry.generated.column === position.column
                    ) {
                      return entry.original;
                    }
                  }
                  return null;
                }
            """,
            "src/index.mjs": """
                export { SourceMapError, mapRange } from './sourceMapRanges.mjs';
            """,
            "tests/source-map-ranges.test.mjs": """
                import assert from 'node:assert/strict';
                import test from 'node:test';
                import { mapRange } from '../src/sourceMapRanges.mjs';

                test('maps exact generated range endpoints', () => {
                  const map = {
                    mappings: [
                      {
                        generated: { line: 1, column: 0 },
                        original: { source: 'src/app.ts', line: 10, column: 4 },
                      },
                      {
                        generated: { line: 1, column: 12 },
                        original: { source: 'src/app.ts', line: 10, column: 16 },
                      },
                    ],
                  };

                  assert.deepEqual(
                    mapRange(map, { line: 1, column: 0 }, { line: 1, column: 12 }),
                    {
                      source: 'src/app.ts',
                      start: { line: 10, column: 5 },
                      end: { line: 10, column: 17 },
                    },
                  );
                });

                test('returns null when exact mapping is missing', () => {
                  const map = {
                    mappings: [
                      {
                        generated: { line: 1, column: 0 },
                        original: { source: 'src/app.ts', line: 1, column: 0 },
                      },
                    ],
                  };

                  assert.equal(mapRange(map, { line: 1, column: 1 }, { line: 1, column: 2 }), null);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { SourceMapError, mapRange } = await loadModule('src/sourceMapRanges.mjs');

            const map = {
              mappings: [
                {
                  generated: { line: 1, column: 0 },
                  original: { source: 'src/app.ts', line: 10, column: 4 },
                },
                {
                  generated: { line: 1, column: 8 },
                  original: { source: 'src/app.ts', line: 10, column: 12 },
                },
                {
                  generated: { line: 2, column: 0 },
                  original: { source: 'src/app.ts', line: 11, column: 0 },
                },
                {
                  generated: { line: 2, column: 5 },
                  original: { source: 'src/app.ts', line: 11, column: 5 },
                },
              ],
            };

            assert.deepEqual(
              mapRange(map, { line: 1, column: 10 }, { line: 2, column: 7 }),
              {
                source: 'src/app.ts',
                start: { line: 10, column: 14 },
                end: { line: 11, column: 7 },
              },
            );

            assert.deepEqual(
              mapRange(map, { line: 1, column: 0 }, { line: 1, column: 8 }),
              {
                source: 'src/app.ts',
                start: { line: 10, column: 4 },
                end: { line: 10, column: 12 },
              },
            );

            assert.deepEqual(
              mapRange({ mappings: [...map.mappings].reverse() }, { line: 2, column: 6 }, { line: 2, column: 9 }),
              {
                source: 'src/app.ts',
                start: { line: 11, column: 6 },
                end: { line: 11, column: 9 },
              },
            );

            assert.throws(
              () => mapRange({ mappings: [{ generated: { line: 1 }, original: { source: 'x', line: 1, column: 0 } }] }, { line: 1, column: 0 }, { line: 1, column: 1 }),
              (error) => error instanceof SourceMapError &&
                error.message.includes('mapping[0]') &&
                error.message.includes('generated.column'),
            );
        """),
    },
    {
        "task_id": "HARD-039",
        "category": "multi_turn_tool_debug",
        "repo_hint": "python/cli_report_writer",
        "instruction": "Fix the report CLI so --format json and --format text produce deterministic output from any current working directory, create parent directories for the output path, write atomically through a temporary sibling file, and leave existing output untouched when rendering fails. Preserve python3 -m report_writer.cli.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # cli-report-writer

                The CLI reads a JSON report input and writes either JSON or text.

                Usage:

                ```bash
                python3 -m report_writer.cli --input fixtures/report.json --output out/report.json --format json
                python3 -m report_writer.cli --input fixtures/report.json --output out/report.txt --format text
                ```

                Requirements:

                - Work from the repository root or any nested current directory.
                - Resolve relative input paths against the repository root.
                - Create parent directories for the output path.
                - JSON output must use sorted keys and end with a newline.
                - Text output must use the documented section order.
                - Writes must be atomic: a rendering failure must leave existing
                  output unchanged and remove temporary siblings.
            """,
            "fixtures/report.json": """
                {
                  "title": "Trace Summary",
                  "metrics": {
                    "verification_rate": 0.75,
                    "token_usage": 15200
                  },
                  "sections": [
                    {"name": "Overview", "body": "Agents completed most visible checks."},
                    {"name": "Failures", "body": "Hidden graders still caught edge cases."}
                  ]
                }
            """,
            "src/report_writer/__init__.py": """
                __all__ = ["render_json", "render_text"]

                from .render import render_json, render_text
            """,
            "src/report_writer/render.py": """
                import json


                def render_json(report):
                    return json.dumps(report) + "\\n"


                def render_text(report):
                    lines = [report["title"], ""]
                    for section in report.get("sections", []):
                        lines.append(section["name"])
                        lines.append(section["body"])
                        lines.append("")
                    lines.append("Metrics")
                    for key, value in report.get("metrics", {}).items():
                        lines.append(f"{key}: {value}")
                    return "\\n".join(lines) + "\\n"
            """,
            "src/report_writer/cli.py": """
                import argparse
                import json
                import sys
                from pathlib import Path

                from .render import render_json, render_text


                def main(argv=None):
                    parser = argparse.ArgumentParser()
                    parser.add_argument("--input", required=True)
                    parser.add_argument("--output", required=True)
                    parser.add_argument("--format", choices=["json", "text"], required=True)
                    args = parser.parse_args(argv)

                    input_path = Path(args.input)
                    report = json.loads(input_path.read_text(encoding="utf-8"))
                    if report.get("title") == "RAISE":
                        raise RuntimeError("cannot render report")

                    if args.format == "json":
                        content = render_json(report)
                    else:
                        content = render_text(report)

                    output_path = Path(args.output)
                    output_path.write_text(content, encoding="utf-8")
                    return 0


                if __name__ == "__main__":
                    raise SystemExit(main(sys.argv[1:]))
            """,
            "tests/test_public_cli.py": """
                import json
                import subprocess
                import sys
                import tempfile
                import unittest
                from pathlib import Path


                ROOT = Path(__file__).resolve().parents[1]


                class PublicCliTest(unittest.TestCase):
                    def run_cli(self, *args):
                        env = {"PYTHONPATH": str(ROOT / "src")}
                        return subprocess.run(
                            [sys.executable, "-m", "report_writer.cli", *args],
                            cwd=ROOT,
                            env=env,
                            text=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            check=False,
                        )

                    def test_writes_json_report(self):
                        with tempfile.TemporaryDirectory() as tmp:
                            output = Path(tmp) / "report.json"
                            result = self.run_cli(
                                "--input", "fixtures/report.json",
                                "--output", str(output),
                                "--format", "json",
                            )

                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertEqual(json.loads(output.read_text()), json.loads((ROOT / "fixtures/report.json").read_text()))

                    def test_writes_text_report(self):
                        with tempfile.TemporaryDirectory() as tmp:
                            output = Path(tmp) / "report.txt"
                            result = self.run_cli(
                                "--input", "fixtures/report.json",
                                "--output", str(output),
                                "--format", "text",
                            )

                            self.assertEqual(result.returncode, 0, result.stderr)
                            self.assertIn("Trace Summary", output.read_text())
                            self.assertIn("Metrics", output.read_text())


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import json
            import os
            import subprocess
            import sys
            import tempfile
            from pathlib import Path

            run_visible_tests()

            root = Path.cwd()
            env = os.environ.copy()
            env["PYTHONPATH"] = str(root / "src")

            def run_cli(cwd, *args):
                return subprocess.run(
                    [sys.executable, "-m", "report_writer.cli", *args],
                    cwd=cwd,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                nested_output = tmp_path / "nested" / "reports" / "summary.json"
                result = run_cli(
                    root / "src",
                    "--input", "fixtures/report.json",
                    "--output", str(nested_output),
                    "--format", "json",
                )
                assert result.returncode == 0, result.stderr
                text = nested_output.read_text(encoding="utf-8")
                assert text.endswith("\\n")
                assert json.loads(text)["title"] == "Trace Summary"
                assert text.index('"metrics"') < text.index('"sections"') < text.index('"title"')

                text_output = tmp_path / "out" / "summary.txt"
                result = run_cli(
                    root / "fixtures",
                    "--input", "fixtures/report.json",
                    "--output", str(text_output),
                    "--format", "text",
                )
                assert result.returncode == 0, result.stderr
                rendered = text_output.read_text(encoding="utf-8").splitlines()
                assert rendered[:5] == [
                    "Trace Summary",
                    "",
                    "Overview",
                    "Agents completed most visible checks.",
                    "",
                ]
                assert rendered[-2:] == ["token_usage: 15200", "verification_rate: 0.75"]

                bad_input = tmp_path / "bad.json"
                bad_input.write_text('{"title": "RAISE"}', encoding="utf-8")
                existing = tmp_path / "existing" / "report.txt"
                existing.parent.mkdir()
                existing.write_text("keep me\\n", encoding="utf-8")
                result = run_cli(
                    root,
                    "--input", str(bad_input),
                    "--output", str(existing),
                    "--format", "text",
                )
                assert result.returncode != 0
                assert existing.read_text(encoding="utf-8") == "keep me\\n"
                assert not list(existing.parent.glob("*.tmp"))
        """),
    },
    {
        "task_id": "HARD-040",
        "category": "stateful_regression",
        "repo_hint": "python/ledger_reconciler",
        "instruction": "Fix the ledger reconciler so posting batches are atomic, duplicate event ids are ignored, reversal events negate the original event exactly once, currency mismatches raise LedgerError, and input events/accounts are not mutated. Preserve apply_events(accounts, events).",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # ledger-reconciler

                `apply_events(accounts, events)` applies ledger events and
                returns a new accounts dictionary.

                Account shape:

                ```python
                {"cash": {"currency": "USD", "balance": 100}}
                ```

                Event shape:

                ```python
                {
                    "id": "evt-1",
                    "postings": [
                        {"account": "cash", "amount": -10, "currency": "USD"},
                        {"account": "revenue", "amount": 10, "currency": "USD"},
                    ],
                }
                ```

                Requirements:

                - Apply a batch atomically: failed events leave all balances unchanged.
                - Ignore duplicate event ids that were already applied.
                - A reversal event has `reversal_of` and negates the original event once.
                - Currency mismatches raise `LedgerError`.
                - Inputs must not be mutated.
            """,
            "src/ledger.py": """
                class LedgerError(Exception):
                    pass


                def apply_events(accounts, events):
                    result = accounts.copy()
                    for event in events:
                        for posting in event.get("postings", []):
                            account = posting["account"]
                            amount = posting["amount"]
                            currency = posting["currency"]
                            if account not in result:
                                result[account] = {"currency": currency, "balance": 0}
                            result[account]["balance"] += amount
                    return result
            """,
            "tests/test_ledger.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from ledger import apply_events


                class LedgerTest(unittest.TestCase):
                    def test_applies_balanced_event(self):
                        accounts = {
                            "cash": {"currency": "USD", "balance": 100},
                            "revenue": {"currency": "USD", "balance": 0},
                        }
                        events = [
                            {
                                "id": "evt-1",
                                "postings": [
                                    {"account": "cash", "amount": -25, "currency": "USD"},
                                    {"account": "revenue", "amount": 25, "currency": "USD"},
                                ],
                            }
                        ]

                        result = apply_events(accounts, events)

                        self.assertEqual(result["cash"]["balance"], 75)
                        self.assertEqual(result["revenue"]["balance"], 25)

                    def test_creates_new_account(self):
                        result = apply_events(
                            {},
                            [
                                {
                                    "id": "evt-1",
                                    "postings": [
                                        {"account": "cash", "amount": 5, "currency": "USD"},
                                    ],
                                }
                            ],
                        )

                        self.assertEqual(result["cash"], {"currency": "USD", "balance": 5})


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy

            run_visible_tests()
            mod = importlib.import_module("ledger")

            accounts = {
                "cash": {"currency": "USD", "balance": 100},
                "revenue": {"currency": "USD", "balance": 0},
                "_applied": {},
            }
            events = [
                {
                    "id": "sale-1",
                    "postings": [
                        {"account": "cash", "amount": 30, "currency": "USD"},
                        {"account": "revenue", "amount": -30, "currency": "USD"},
                    ],
                }
            ]
            accounts_before = copy.deepcopy(accounts)
            events_before = copy.deepcopy(events)
            result = mod.apply_events(accounts, events)
            assert accounts == accounts_before
            assert events == events_before
            assert result["cash"]["balance"] == 130
            assert result["revenue"]["balance"] == -30

            result2 = mod.apply_events(result, events)
            assert result2["cash"]["balance"] == 130
            assert result2["revenue"]["balance"] == -30

            reversed_once = mod.apply_events(
                result,
                [{"id": "void-1", "reversal_of": "sale-1"}],
            )
            assert reversed_once["cash"]["balance"] == 100
            assert reversed_once["revenue"]["balance"] == 0
            assert "void-1" in reversed_once.get("_applied", {})

            try:
                mod.apply_events(reversed_once, [{"id": "void-2", "reversal_of": "sale-1"}])
            except mod.LedgerError as error:
                assert "already reversed" in str(error)
            else:
                raise AssertionError("expected LedgerError for duplicate reversal")

            bad_accounts = {
                "cash": {"currency": "USD", "balance": 100},
                "revenue": {"currency": "USD", "balance": 0},
            }
            before_bad = copy.deepcopy(bad_accounts)
            try:
                mod.apply_events(
                    bad_accounts,
                    [
                        {
                            "id": "bad-1",
                            "postings": [
                                {"account": "cash", "amount": -10, "currency": "USD"},
                                {"account": "revenue", "amount": 10, "currency": "EUR"},
                            ],
                        }
                    ],
                )
            except mod.LedgerError as error:
                assert "currency" in str(error).lower()
            else:
                raise AssertionError("expected LedgerError for currency mismatch")
            assert bad_accounts == before_bad

            try:
                mod.apply_events({"cash": {"currency": "USD", "balance": 5}}, [{"id": "missing", "reversal_of": "nope"}])
            except mod.LedgerError as error:
                assert "unknown" in str(error).lower()
            else:
                raise AssertionError("expected LedgerError for unknown reversal")
        """),
    },
    {
        "task_id": "HARD-041",
        "category": "feature",
        "repo_hint": "typescript/range_set",
        "instruction": "Implement an immutable integer range set with add, remove, contains, union, and toArray. Ranges are closed integer intervals, adjacent ranges must coalesce, removals may split ranges, invalid ranges throw RangeSetError, and all outputs must be sorted and normalized.",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "README.md": """
                # range-set

                `RangeSet` stores closed integer intervals.

                Public API:

                - `new RangeSet(ranges = [])`
                - `add(start, end)`
                - `remove(start, end)`
                - `contains(value)`
                - `union(other)`
                - `toArray()`

                Requirements:

                - All operations return a new `RangeSet`; existing instances are
                  immutable.
                - Ranges are closed integer intervals.
                - Overlapping and adjacent ranges coalesce.
                - Removing a range can split an existing range.
                - Invalid ranges throw `RangeSetError`.
                - `toArray()` returns sorted normalized `[start, end]` pairs.
            """,
            "src/range-set.mjs": """
                export class RangeSetError extends Error {
                  constructor(message) {
                    super(message);
                    this.name = 'RangeSetError';
                  }
                }

                export class RangeSet {
                  constructor(ranges = []) {
                    this.ranges = ranges;
                  }

                  add(start, end) {
                    this.ranges.push([start, end]);
                    return this;
                  }

                  remove(start, end) {
                    this.ranges = this.ranges.filter(([rangeStart, rangeEnd]) => {
                      return rangeEnd < start || rangeStart > end;
                    });
                    return this;
                  }

                  contains(value) {
                    return this.ranges.some(([start, end]) => start <= value && value <= end);
                  }

                  union(other) {
                    this.ranges.push(...other.toArray());
                    return this;
                  }

                  toArray() {
                    return this.ranges.slice();
                  }
                }
            """,
            "src/index.mjs": """
                export { RangeSet, RangeSetError } from './range-set.mjs';
            """,
            "tests/range-set.test.mjs": """
                import assert from 'node:assert/strict';
                import test from 'node:test';
                import { RangeSet } from '../src/range-set.mjs';

                test('add stores a range and contains values inside it', () => {
                  const ranges = new RangeSet().add(1, 3);

                  assert.equal(ranges.contains(1), true);
                  assert.equal(ranges.contains(2), true);
                  assert.equal(ranges.contains(4), false);
                  assert.deepEqual(ranges.toArray(), [[1, 3]]);
                });

                test('remove drops a fully covered range', () => {
                  const ranges = new RangeSet([[1, 3], [10, 12]]).remove(1, 3);

                  assert.deepEqual(ranges.toArray(), [[10, 12]]);
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { RangeSet, RangeSetError } = await loadModule('src/range-set.mjs');

            const base = new RangeSet([[1, 3]]);
            const expanded = base.add(4, 6);
            assert.deepEqual(base.toArray(), [[1, 3]]);
            assert.deepEqual(expanded.toArray(), [[1, 6]]);
            assert.equal(expanded.contains(5), true);
            assert.equal(expanded.contains(7), false);

            const split = expanded.remove(3, 4);
            assert.deepEqual(expanded.toArray(), [[1, 6]]);
            assert.deepEqual(split.toArray(), [[1, 2], [5, 6]]);

            const negative = new RangeSet([[-5, -3], [0, 0]]).add(-2, -1);
            assert.deepEqual(negative.toArray(), [[-5, -1], [0, 0]]);

            const left = new RangeSet([[10, 12]]);
            const right = new RangeSet([[1, 2], [3, 5]]);
            const combined = left.union(right);
            assert.deepEqual(left.toArray(), [[10, 12]]);
            assert.deepEqual(right.toArray(), [[1, 5]]);
            assert.deepEqual(combined.toArray(), [[1, 5], [10, 12]]);

            assert.throws(() => new RangeSet([[3, 1]]), RangeSetError);
            assert.throws(() => new RangeSet().add(1.5, 2), RangeSetError);
            assert.throws(() => new RangeSet().remove(5, 4), RangeSetError);
        """),
    },
    {
        "task_id": "HARD-042",
        "category": "multi_turn_tool_debug",
        "repo_hint": "python/snapshot_manifest",
        "instruction": "Fix the snapshot manifest CLI so build-manifest produces deterministic JSON from nested fixture directories. It must ignore configured glob patterns, hash file contents with SHA-256, normalize paths with forward slashes, sort entries by normalized path, include empty directories only when --include-empty-dirs is passed, and produce identical output from repo root or nested working directories.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # snapshot-manifest

                `python3 -m manifest_cli build-manifest ROOT --output manifest.json`
                writes a deterministic JSON manifest for files under `ROOT`.

                Requirements:

                - Hash file contents with SHA-256.
                - Normalize paths with forward slashes.
                - Sort manifest entries by normalized path.
                - Respect ignore patterns from `.manifestignore`.
                - Include empty directories only when `--include-empty-dirs` is passed.
                - Relative paths must work from the repo root or nested working directories.
            """,
            "fixtures/project/README.md": "# Demo Project\n",
            "fixtures/project/src/app.py": "print('hello')\n",
            "fixtures/project/src/data.tmp": "temporary\n",
            "fixtures/project/build/output.txt": "generated\n",
            "fixtures/project/docs/guide.md": "guide\n",
            "fixtures/project/empty/.keepdir": "",
            "fixtures/project/.manifestignore": "*.tmp\nbuild/**\n",
            "src/snapshot_manifest.py": """
                import json
                import os
                from pathlib import Path


                def build_manifest(root, include_empty_dirs=False):
                    root_path = Path(root)
                    entries = []
                    for current, dirs, files in os.walk(root_path):
                        for filename in files:
                            path = Path(current) / filename
                            rel = str(path.relative_to(root_path))
                            entries.append({
                                "path": rel,
                                "kind": "file",
                                "size": path.stat().st_size,
                            })
                    return {"entries": entries}


                def write_manifest(root, output, include_empty_dirs=False):
                    manifest = build_manifest(root, include_empty_dirs=include_empty_dirs)
                    Path(output).write_text(json.dumps(manifest) + "\\n", encoding="utf-8")
                    return manifest
            """,
            "src/manifest_cli.py": """
                import argparse
                import sys

                from snapshot_manifest import write_manifest


                def main(argv=None):
                    parser = argparse.ArgumentParser()
                    sub = parser.add_subparsers(dest="command", required=True)
                    build = sub.add_parser("build-manifest")
                    build.add_argument("root")
                    build.add_argument("--output", required=True)
                    build.add_argument("--include-empty-dirs", action="store_true")
                    args = parser.parse_args(argv)

                    if args.command == "build-manifest":
                        write_manifest(args.root, args.output, include_empty_dirs=args.include_empty_dirs)
                        return 0
                    return 1


                if __name__ == "__main__":
                    raise SystemExit(main(sys.argv[1:]))
            """,
            "tests/test_snapshot_manifest.py": """
                import json
                import subprocess
                import sys
                import tempfile
                import unittest
                from pathlib import Path


                ROOT = Path(__file__).resolve().parents[1]


                class SnapshotManifestTest(unittest.TestCase):
                    def test_builds_basic_manifest(self):
                        with tempfile.TemporaryDirectory() as tmp:
                            output = Path(tmp) / "manifest.json"
                            result = subprocess.run(
                                [
                                    sys.executable,
                                    "-m",
                                    "manifest_cli",
                                    "build-manifest",
                                    "fixtures/project",
                                    "--output",
                                    str(output),
                                ],
                                cwd=ROOT,
                                env={"PYTHONPATH": str(ROOT / "src")},
                                text=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                check=False,
                            )

                            self.assertEqual(result.returncode, 0, result.stderr)
                            manifest = json.loads(output.read_text())
                            paths = {entry["path"] for entry in manifest["entries"]}
                            self.assertIn("README.md", paths)
                            self.assertIn("src/app.py", paths)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import hashlib
            import json
            import os
            import subprocess
            import sys
            import tempfile
            from pathlib import Path

            run_visible_tests()

            root = Path.cwd()
            env = os.environ.copy()
            env["PYTHONPATH"] = str(root / "src")

            def run_cli(cwd, *args):
                return subprocess.run(
                    [sys.executable, "-m", "manifest_cli", "build-manifest", *args],
                    cwd=cwd,
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )

            def load_manifest(path):
                return json.loads(path.read_text(encoding="utf-8"))

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                output_a = tmp_path / "a" / "manifest.json"
                output_a.parent.mkdir()
                result = run_cli(
                    root,
                    "fixtures/project",
                    "--output",
                    str(output_a),
                )
                assert result.returncode == 0, result.stderr
                manifest_a = load_manifest(output_a)

                output_b = tmp_path / "b" / "manifest.json"
                output_b.parent.mkdir()
                result = run_cli(
                    root / "fixtures",
                    "fixtures/project",
                    "--output",
                    str(output_b),
                )
                assert result.returncode == 0, result.stderr
                assert load_manifest(output_b) == manifest_a

                entries = manifest_a["entries"]
                paths = [entry["path"] for entry in entries]
                assert paths == sorted(paths)
                assert all("\\\\" not in path for path in paths)
                assert "src/data.tmp" not in paths
                assert "build/output.txt" not in paths
                assert "empty" not in paths

                by_path = {entry["path"]: entry for entry in entries}
                expected_hash = hashlib.sha256((root / "fixtures/project/src/app.py").read_bytes()).hexdigest()
                assert by_path["src/app.py"]["sha256"] == expected_hash
                assert "size" not in by_path["src/app.py"]

                output_c = tmp_path / "c" / "manifest.json"
                output_c.parent.mkdir()
                result = run_cli(
                    root,
                    "fixtures/project",
                    "--output",
                    str(output_c),
                    "--include-empty-dirs",
                )
                assert result.returncode == 0, result.stderr
                paths_with_dirs = [entry["path"] for entry in load_manifest(output_c)["entries"]]
                assert "empty" in paths_with_dirs
        """),
    },
    {
        "task_id": "HARD-043",
        "category": "data_migration",
        "repo_hint": "python/migration_runner",
        "instruction": "Fix the migration runner so it applies pending migrations in dependency order, skips already-applied migration ids, validates recorded checksums, rolls back all changes on failure, and preserves run_migrations(store, migrations). Raise MigrationError with useful diagnostics for missing dependencies, dependency cycles, and checksum drift.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # migration-runner

                `run_migrations(store, migrations)` applies migration objects
                to an in-memory store and returns the updated store.

                Store shape:

                ```python
                {
                    "data": {},
                    "applied": {"001_init": "checksum"},
                }
                ```

                Migration shape:

                ```python
                {
                    "id": "002_add_users",
                    "checksum": "sha",
                    "depends_on": ["001_init"],
                    "apply": callable,
                }
                ```

                Requirements:

                - Apply pending migrations in dependency order.
                - Skip already-applied migration ids after validating checksums.
                - Roll back all data and applied changes if any migration fails.
                - Raise `MigrationError` for missing dependencies, cycles, and
                  checksum drift.
            """,
            "src/migration_runner.py": """
                class MigrationError(Exception):
                    pass


                def run_migrations(store, migrations):
                    data = store.setdefault("data", {})
                    applied = store.setdefault("applied", {})
                    for migration in migrations:
                        migration_id = migration["id"]
                        if migration_id in applied:
                            continue
                        applied[migration_id] = migration.get("checksum", "")
                        migration["apply"](data)
                    return store
            """,
            "tests/test_migration_runner.py": """
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from migration_runner import run_migrations


                class MigrationRunnerTest(unittest.TestCase):
                    def test_applies_simple_migrations(self):
                        store = {"data": {}, "applied": {}}
                        migrations = [
                            {
                                "id": "001_init",
                                "checksum": "a",
                                "depends_on": [],
                                "apply": lambda data: data.update({"users": []}),
                            },
                            {
                                "id": "002_seed",
                                "checksum": "b",
                                "depends_on": ["001_init"],
                                "apply": lambda data: data["users"].append("ada"),
                            },
                        ]

                        result = run_migrations(store, migrations)

                        self.assertEqual(result["data"]["users"], ["ada"])
                        self.assertEqual(result["applied"], {"001_init": "a", "002_seed": "b"})

                    def test_skips_applied_migration(self):
                        store = {"data": {"users": ["ada"]}, "applied": {"001_init": "a"}}
                        migrations = [
                            {
                                "id": "001_init",
                                "checksum": "a",
                                "depends_on": [],
                                "apply": lambda data: data["users"].append("grace"),
                            }
                        ]

                        result = run_migrations(store, migrations)

                        self.assertEqual(result["data"]["users"], ["ada"])


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy

            run_visible_tests()
            mod = importlib.import_module("migration_runner")

            def set_value(key, value):
                return lambda data: data.__setitem__(key, value)

            def append_value(key, value):
                return lambda data: data.setdefault(key, []).append(value)

            store = {"data": {}, "applied": {}}
            migrations = [
                {"id": "003_seed", "checksum": "c", "depends_on": ["002_users"], "apply": append_value("users", "ada")},
                {"id": "001_init", "checksum": "a", "depends_on": [], "apply": set_value("version", 1)},
                {"id": "002_users", "checksum": "b", "depends_on": ["001_init"], "apply": set_value("users", [])},
            ]
            result = mod.run_migrations(store, migrations)
            assert result["data"] == {"version": 1, "users": ["ada"]}
            assert list(result["applied"].keys()) == ["001_init", "002_users", "003_seed"]

            already = {
                "data": {"version": 1, "users": ["ada"]},
                "applied": {"001_init": "a", "002_users": "b", "003_seed": "c"},
            }
            before = copy.deepcopy(already)
            rerun = mod.run_migrations(
                already,
                [{"id": "003_seed", "checksum": "c", "depends_on": ["002_users"], "apply": append_value("users", "grace")}],
            )
            assert rerun == before

            try:
                mod.run_migrations(
                    already,
                    [{"id": "003_seed", "checksum": "changed", "depends_on": ["002_users"], "apply": append_value("users", "grace")}],
                )
            except mod.MigrationError as error:
                assert "checksum" in str(error).lower()
            else:
                raise AssertionError("expected checksum drift error")

            failing_store = {"data": {"version": 1}, "applied": {"001_init": "a"}}
            before_fail = copy.deepcopy(failing_store)

            def explode(data):
                data["partial"] = True
                raise RuntimeError("boom")

            try:
                mod.run_migrations(
                    failing_store,
                    [{"id": "002_fail", "checksum": "x", "depends_on": ["001_init"], "apply": explode}],
                )
            except RuntimeError:
                pass
            else:
                raise AssertionError("expected migration failure")
            assert failing_store == before_fail

            for bad, expected in [
                ([{"id": "002_missing", "checksum": "b", "depends_on": ["001_missing"], "apply": set_value("x", 1)}], "missing"),
                ([
                    {"id": "001_a", "checksum": "a", "depends_on": ["002_b"], "apply": set_value("a", 1)},
                    {"id": "002_b", "checksum": "b", "depends_on": ["001_a"], "apply": set_value("b", 2)},
                ], "cycle"),
            ]:
                try:
                    mod.run_migrations({"data": {}, "applied": {}}, bad)
                except mod.MigrationError as error:
                    assert expected in str(error).lower()
                else:
                    raise AssertionError(f"expected {expected} error")
        """),
    },
    {
        "task_id": "HARD-044",
        "category": "feature",
        "repo_hint": "typescript/icu_plural_format",
        "instruction": "Implement a small ICU-style plural message formatter. Support {name} interpolation, plural blocks with one, other, exact =n arms, optional offset:n, # substitution after offset, escaped apostrophes, missing-value FormatError diagnostics, and input immutability. Preserve formatMessage(message, values).",
        "public_success_check": "npm test",
        "success_check": "node ../grader/check.mjs",
        "files": {
            "package.json": node_package(),
            "README.md": """
                # icu-plural-format

                `formatMessage(message, values)` formats a small subset of ICU
                messages.

                Supported syntax:

                - `{name}` interpolation
                - `{count, plural, one {...} other {...}}`
                - Exact plural arms such as `=0 {...}`
                - Optional plural offsets such as `offset:1`
                - `#` substitution inside plural arms after applying offset
                - Apostrophe escaping for literal braces and quotes

                Missing interpolation or plural values must raise `FormatError`.
                The `values` object must not be mutated.
            """,
            "src/formatMessage.mjs": """
                export class FormatError extends Error {
                  constructor(message) {
                    super(message);
                    this.name = 'FormatError';
                  }
                }

                export function formatMessage(message, values = {}) {
                  return message.replace(/\\{([a-zA-Z_][a-zA-Z0-9_]*)\\}/g, (match, name) => {
                    if (!(name in values)) {
                      throw new FormatError(`Missing value: ${name}`);
                    }
                    return String(values[name]);
                  });
                }
            """,
            "src/index.mjs": """
                export { FormatError, formatMessage } from './formatMessage.mjs';
            """,
            "tests/formatMessage.test.mjs": """
                import assert from 'node:assert/strict';
                import test from 'node:test';
                import { FormatError, formatMessage } from '../src/formatMessage.mjs';

                test('interpolates named values', () => {
                  assert.equal(
                    formatMessage('Hello {name}, status {status}.', { name: 'Ada', status: 'ready' }),
                    'Hello Ada, status ready.',
                  );
                });

                test('throws FormatError for missing values', () => {
                  assert.throws(
                    () => formatMessage('Hello {name}.', {}),
                    FormatError,
                  );
                });
            """,
        },
        "grader": node_grader("""
            run('npm', ['test']);
            const { FormatError, formatMessage } = await loadModule('src/formatMessage.mjs');

            const values = { name: 'Ada', count: 0 };
            const before = JSON.stringify(values);
            assert.equal(
              formatMessage('{name} has {count, plural, =0 {no messages} one {one message} other {# messages}}.', values),
              'Ada has no messages.',
            );
            assert.equal(JSON.stringify(values), before);

            assert.equal(
              formatMessage('{count, plural, one {One file} other {# files}}', { count: 1 }),
              'One file',
            );
            assert.equal(
              formatMessage('{count, plural, one {One file} other {# files}}', { count: 5 }),
              '5 files',
            );
            assert.equal(
              formatMessage('{count, plural, offset:1 =0 {Nobody came} one {{name} came alone} other {{name} and # others came}}', {
                count: 4,
                name: 'Grace',
              }),
              'Grace and 3 others came',
            );
            assert.equal(
              formatMessage("Use '{'count'}' literally: {count, plural, one {'#'} other {#}}", { count: 2 }),
              'Use {count} literally: 2',
            );

            assert.throws(
              () => formatMessage('{count, plural, one {ok} other {ok}}', {}),
              (error) => error instanceof FormatError && error.message.includes('count'),
            );
            assert.throws(
              () => formatMessage('{name} {missing}', { name: 'Ada' }),
              (error) => error instanceof FormatError && error.message.includes('missing'),
            );
        """),
    },
    {
        "task_id": "HARD-045",
        "category": "stateful_regression",
        "repo_hint": "python/stream_window_join",
        "instruction": "Fix the streaming window joiner so out-of-order left/right events join within a time tolerance, watermarks evict only safely expired buffered events, duplicate event ids are ignored, late events are counted but not emitted, and snapshot() returns an isolated copy. Preserve WindowJoiner(tolerance_ms) with add_left, add_right, advance_watermark, and snapshot.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # stream-window-join

                `WindowJoiner(tolerance_ms)` joins left and right events when
                their timestamps are within the tolerance.

                Event shape:

                ```python
                {"id": "left-1", "time": 1000, "value": "L"}
                ```

                Public API:

                - `add_left(event)` returns newly emitted join pairs.
                - `add_right(event)` returns newly emitted join pairs.
                - `advance_watermark(time_ms)` evicts safely expired buffered events.
                - `snapshot()` returns buffered state and counters.

                Duplicate event ids are ignored. Events older than the current
                watermark are late: count them, but do not emit joins.
            """,
            "src/window_join.py": """
                class WindowJoiner:
                    def __init__(self, tolerance_ms):
                        self.tolerance_ms = tolerance_ms
                        self.left = []
                        self.right = []
                        self.watermark = None
                        self.late_count = 0

                    def add_left(self, event):
                        if self.watermark is not None and event["time"] < self.watermark:
                            self.late_count += 1
                            return []
                        emitted = []
                        for right in self.right:
                            if abs(event["time"] - right["time"]) <= self.tolerance_ms:
                                emitted.append((event, right))
                        self.left.append(event)
                        return emitted

                    def add_right(self, event):
                        if self.watermark is not None and event["time"] < self.watermark:
                            self.late_count += 1
                            return []
                        emitted = []
                        for left in self.left:
                            if abs(left["time"] - event["time"]) <= self.tolerance_ms:
                                emitted.append((left, event))
                        self.right.append(event)
                        return emitted

                    def advance_watermark(self, time_ms):
                        self.watermark = time_ms
                        self.left = [event for event in self.left if event["time"] >= time_ms]
                        self.right = [event for event in self.right if event["time"] >= time_ms]
                        return []

                    def snapshot(self):
                        return {
                            "left": self.left,
                            "right": self.right,
                            "watermark": self.watermark,
                            "late_count": self.late_count,
                        }
            """,
            "tests/test_window_join.py": """
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
            """,
        },
        "grader": py_grader("""
            run_visible_tests()
            mod = importlib.import_module("window_join")

            joiner = mod.WindowJoiner(tolerance_ms=5)
            assert joiner.add_right({"id": "r1", "time": 100, "value": "R"}) == []
            emitted = joiner.add_left({"id": "l1", "time": 104, "value": "L"})
            assert [(left["id"], right["id"]) for left, right in emitted] == [("l1", "r1")]

            assert joiner.add_left({"id": "l1", "time": 104, "value": "L-duplicate"}) == []
            assert joiner.add_right({"id": "r1", "time": 103, "value": "R-duplicate"}) == []

            joiner = mod.WindowJoiner(tolerance_ms=10)
            joiner.add_left({"id": "l-old", "time": 100, "value": "old"})
            joiner.add_left({"id": "l-keep", "time": 111, "value": "keep"})
            joiner.advance_watermark(105)
            snap = joiner.snapshot()
            assert [event["id"] for event in snap["left"]] == ["l-keep"]
            assert joiner.add_right({"id": "r-keep", "time": 116, "value": "R"})
            assert joiner.add_left({"id": "late", "time": 104, "value": "late"}) == []
            assert joiner.snapshot()["late_count"] == 1

            snapshot = joiner.snapshot()
            snapshot["left"].append({"id": "mutated", "time": 999, "value": "x"})
            assert all(event["id"] != "mutated" for event in joiner.snapshot()["left"])

            joiner = mod.WindowJoiner(tolerance_ms=3)
            assert joiner.add_left({"id": "l2", "time": 200, "value": "L"}) == []
            assert joiner.add_right({"id": "r2", "time": 204, "value": "R"}) == []
            assert joiner.add_right({"id": "r3", "time": 203, "value": "R3"})
        """),
    },
    {
        "task_id": "HARD-046",
        "category": "data_migration",
        "repo_hint": "python/sqlite_migration_runner",
        "instruction": "Fix the SQLite migration runner so numbered migrations apply once in numeric order, each migration runs atomically, applied migration name and checksum are recorded, changed applied migrations raise MigrationError, and dry_run=True reports pending migrations without changing the database. Preserve run_migrations(db_path, migrations_dir, dry_run=False). Use only the Python standard library.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # sqlite-migration-runner

                `run_migrations(db_path, migrations_dir, dry_run=False)` applies
                SQL migration files to a SQLite database.

                Migration files are named with a numeric prefix, for example:

                - `001_init.sql`
                - `002_seed.sql`
                - `010_add_status.sql`

                Requirements:

                - apply numbered migrations in numeric order
                - apply each migration at most once
                - store applied migration names and content checksums
                - raise `MigrationError` if an applied migration file changes
                - roll back a failed migration atomically
                - make `dry_run=True` return pending migration names without
                  creating or changing database state
            """,
            "migrations/001_init.sql": """
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL
                );
            """,
            "migrations/002_seed.sql": """
                INSERT INTO users (id, name) VALUES (1, 'Ada');
            """,
            "migrations/010_add_status.sql": """
                ALTER TABLE users ADD COLUMN status TEXT DEFAULT 'new';
                UPDATE users SET status = 'active' WHERE name = 'Ada';
            """,
            "src/migrator.py": """
                import sqlite3
                from pathlib import Path


                class MigrationError(Exception):
                    pass


                def run_migrations(db_path, migrations_dir, dry_run=False):
                    files = sorted(Path(migrations_dir).glob("*.sql"))
                    names = [path.name for path in files]
                    if dry_run:
                        return names

                    conn = sqlite3.connect(db_path)
                    try:
                        conn.execute(
                            "CREATE TABLE IF NOT EXISTS schema_migrations "
                            "(name TEXT PRIMARY KEY)"
                        )
                        applied = {
                            row[0]
                            for row in conn.execute("SELECT name FROM schema_migrations")
                        }
                        for path in files:
                            if path.name in applied:
                                continue
                            conn.executescript(path.read_text(encoding="utf-8"))
                            conn.execute(
                                "INSERT INTO schema_migrations(name) VALUES (?)",
                                (path.name,),
                            )
                        conn.commit()
                    finally:
                        conn.close()
                    return names
            """,
            "tests/test_migrator.py": """
                import sqlite3
                import sys
                import tempfile
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from migrator import run_migrations


                class MigratorTest(unittest.TestCase):
                    def test_applies_fixture_migrations(self):
                        root = Path(__file__).resolve().parents[1]
                        with tempfile.TemporaryDirectory() as tmp:
                            db_path = Path(tmp) / "app.db"

                            applied = run_migrations(db_path, root / "migrations")

                            self.assertIn("001_init.sql", applied)
                            with sqlite3.connect(db_path) as conn:
                                rows = conn.execute(
                                    "SELECT id, name FROM users ORDER BY id"
                                ).fetchall()
                            self.assertEqual(rows, [(1, "Ada")])

                    def test_dry_run_lists_migrations(self):
                        root = Path(__file__).resolve().parents[1]
                        with tempfile.TemporaryDirectory() as tmp:
                            db_path = Path(tmp) / "app.db"

                            pending = run_migrations(db_path, root / "migrations", dry_run=True)

                            self.assertIn("001_init.sql", pending)
                            self.assertIn("002_seed.sql", pending)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import shutil
            import sqlite3
            import tempfile
            from pathlib import Path

            run_visible_tests()
            mod = importlib.import_module("migrator")

            root = Path.cwd()
            source_migrations = root / "migrations"

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                migrations = tmp_path / "migrations"
                shutil.copytree(source_migrations, migrations)
                db_path = tmp_path / "app.db"

                applied = mod.run_migrations(db_path, migrations)
                assert applied == ["001_init.sql", "002_seed.sql", "010_add_status.sql"]

                with sqlite3.connect(db_path) as conn:
                    rows = conn.execute(
                        "SELECT id, name, status FROM users ORDER BY id"
                    ).fetchall()
                    migration_rows = conn.execute(
                        "SELECT name, checksum FROM schema_migrations ORDER BY name"
                    ).fetchall()
                assert rows == [(1, "Ada", "active")]
                assert [row[0] for row in migration_rows] == applied
                assert all(row[1] for row in migration_rows)

                again = mod.run_migrations(db_path, migrations)
                assert again == []
                with sqlite3.connect(db_path) as conn:
                    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                    migration_count = conn.execute(
                        "SELECT COUNT(*) FROM schema_migrations"
                    ).fetchone()[0]
                assert count == 1
                assert migration_count == 3

                (migrations / "002_seed.sql").write_text(
                    "INSERT INTO users (id, name) VALUES (2, 'Grace');\\n",
                    encoding="utf-8",
                )
                try:
                    mod.run_migrations(db_path, migrations)
                except mod.MigrationError as error:
                    assert "checksum" in str(error).lower()
                else:
                    raise AssertionError("changed applied migration did not fail")

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                migrations = tmp_path / "migrations"
                migrations.mkdir()
                (migrations / "001_init.sql").write_text(
                    "CREATE TABLE ok_table (id INTEGER PRIMARY KEY);\\n",
                    encoding="utf-8",
                )
                (migrations / "002_bad.sql").write_text(
                    "CREATE TABLE partial_table (id INTEGER);\\n"
                    "INSERT INTO partial_table VALUES (1);\\n"
                    "INSERT INTO missing_table VALUES (1);\\n",
                    encoding="utf-8",
                )
                db_path = tmp_path / "bad.db"

                try:
                    mod.run_migrations(db_path, migrations)
                except Exception:
                    pass
                else:
                    raise AssertionError("bad migration unexpectedly succeeded")

                with sqlite3.connect(db_path) as conn:
                    names = {
                        row[0]
                        for row in conn.execute(
                            "SELECT name FROM sqlite_master WHERE type='table'"
                        )
                    }
                    recorded = []
                    if "schema_migrations" in names:
                        recorded = conn.execute(
                            "SELECT name FROM schema_migrations"
                        ).fetchall()
                assert "partial_table" not in names
                assert ("002_bad.sql",) not in recorded

            with tempfile.TemporaryDirectory() as tmp:
                tmp_path = Path(tmp)
                migrations = tmp_path / "migrations"
                shutil.copytree(source_migrations, migrations)
                db_path = tmp_path / "dry.db"

                pending = mod.run_migrations(db_path, migrations, dry_run=True)
                assert pending == ["001_init.sql", "002_seed.sql", "010_add_status.sql"]
                with sqlite3.connect(db_path) as conn:
                    tables = conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    ).fetchall()
                assert tables == []
        """),
    },
    {
        "task_id": "HARD-047",
        "category": "stateful_regression",
        "repo_hint": "python/webhook_replay_guard",
        "instruction": "Fix the webhook replay guard so signed webhook envelopes are accepted only once per tenant within the replay window. Preserve verify_event(envelope, keys, store, now), verify HMAC-SHA256 signatures over the exact raw body text, enforce timestamp skew, support signing-key rotation, prune expired seen ids, and do not mutate the envelope or keys inputs. Use only the Python standard library.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # webhook-replay-guard

                `verify_event(envelope, keys, store, now)` accepts a signed
                webhook event or raises `WebhookError`.

                Envelope fields:

                - `tenant`: tenant id
                - `event_id`: unique id from the webhook sender
                - `timestamp`: integer Unix timestamp
                - `body`: raw request body text
                - `signature`: header text like `t=1700000000,v1=<hex>`

                The `keys` mapping stores one active signing key per tenant, or
                a list of active keys during rotation. The HMAC message is the
                exact raw body text prefixed by the timestamp and a dot:

                ```text
                <timestamp>.<raw body text>
                ```

                Requirements:

                - use HMAC-SHA256 and constant-time comparison
                - reject timestamps outside `REPLAY_WINDOW_SECONDS`
                - accept rotated keys
                - reject replayed `(tenant, event_id)` pairs
                - allow different tenants to reuse the same event id
                - prune expired seen ids from the mutable `store`
                - do not mutate `envelope` or `keys`
            """,
            "src/webhook_guard.py": """
                import hashlib
                import hmac
                import json


                REPLAY_WINDOW_SECONDS = 300


                class WebhookError(Exception):
                    pass


                def _parse_signature(header):
                    parts = {}
                    for item in header.split(","):
                        if "=" in item:
                            key, value = item.split("=", 1)
                            parts[key.strip()] = value.strip()
                    return int(parts["t"]), parts["v1"]


                def _canonical_body(body):
                    parsed = json.loads(body)
                    return json.dumps(parsed, sort_keys=True, separators=(",", ":"))


                def verify_event(envelope, keys, store, now):
                    tenant = envelope["tenant"]
                    event_id = envelope["event_id"]
                    timestamp = int(envelope["timestamp"])

                    seen = store.setdefault("seen", set())
                    if event_id in seen:
                        raise WebhookError("replayed event")
                    seen.add(event_id)

                    if abs(now - timestamp) > REPLAY_WINDOW_SECONDS:
                        raise WebhookError("timestamp outside replay window")

                    header_timestamp, actual = _parse_signature(envelope["signature"])
                    if header_timestamp != timestamp:
                        raise WebhookError("timestamp mismatch")

                    key = keys[tenant]
                    body = _canonical_body(envelope["body"])
                    message = f"{timestamp}.{body}".encode("utf-8")
                    expected = hmac.new(
                        key.encode("utf-8"),
                        message,
                        hashlib.sha256,
                    ).hexdigest()

                    if actual != expected:
                        raise WebhookError("invalid signature")
                    return True
            """,
            "tests/test_webhook_guard.py": """
                import hashlib
                import hmac
                import sys
                import unittest
                from pathlib import Path

                sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
                from webhook_guard import WebhookError, verify_event


                def sign(timestamp, body, key):
                    message = f"{timestamp}.{body}".encode("utf-8")
                    digest = hmac.new(
                        key.encode("utf-8"),
                        message,
                        hashlib.sha256,
                    ).hexdigest()
                    return f"t={timestamp},v1={digest}"


                def envelope(event_id="evt_1", timestamp=1000, body='{"amount":10}'):
                    return {
                        "tenant": "tenant-a",
                        "event_id": event_id,
                        "timestamp": timestamp,
                        "body": body,
                        "signature": sign(timestamp, body, "k1"),
                    }


                class WebhookGuardTest(unittest.TestCase):
                    def test_accepts_valid_event(self):
                        self.assertTrue(
                            verify_event(envelope(), {"tenant-a": "k1"}, {}, 1000)
                        )

                    def test_rejects_replay(self):
                        store = {}
                        verify_event(envelope(), {"tenant-a": "k1"}, store, 1000)
                        with self.assertRaises(WebhookError):
                            verify_event(envelope(), {"tenant-a": "k1"}, store, 1000)

                    def test_rejects_old_timestamp(self):
                        with self.assertRaises(WebhookError):
                            verify_event(envelope(timestamp=600), {"tenant-a": "k1"}, {}, 1000)

                    def test_rejects_bad_signature(self):
                        item = envelope()
                        item["signature"] = "t=1000,v1=bad"
                        with self.assertRaises(WebhookError):
                            verify_event(item, {"tenant-a": "k1"}, {}, 1000)


                if __name__ == "__main__":
                    unittest.main()
            """,
        },
        "grader": py_grader("""
            import copy
            import hashlib
            import hmac

            run_visible_tests()
            mod = importlib.import_module("webhook_guard")


            def sign(timestamp, body, key):
                message = f"{timestamp}.{body}".encode("utf-8")
                digest = hmac.new(
                    key.encode("utf-8"),
                    message,
                    hashlib.sha256,
                ).hexdigest()
                return f"ignored=x, t={timestamp}, v1={digest}"


            def make_event(tenant, event_id, timestamp, body, key):
                return {
                    "tenant": tenant,
                    "event_id": event_id,
                    "timestamp": timestamp,
                    "body": body,
                    "signature": sign(timestamp, body, key),
                }


            keys = {"tenant-a": "k1", "tenant-b": "k2"}
            store = {}

            raw_body = '{\\n  "amount": 10,\\n  "id": "evt_raw"\\n}'
            event = make_event("tenant-a", "evt_raw", 1000, raw_body, "k1")
            original_event = copy.deepcopy(event)
            original_keys = copy.deepcopy(keys)
            assert mod.verify_event(event, keys, store, 1000) is True
            assert event == original_event
            assert keys == original_keys

            replay = make_event("tenant-a", "evt_raw", 1000, raw_body, "k1")
            try:
                mod.verify_event(replay, keys, store, 1000)
            except mod.WebhookError as error:
                assert "replay" in str(error).lower()
            else:
                raise AssertionError("same tenant replay was accepted")

            other_tenant = make_event("tenant-b", "evt_raw", 1000, raw_body, "k2")
            assert mod.verify_event(other_tenant, keys, store, 1000) is True

            rotated_keys = {"tenant-a": ["old-key", "new-key"]}
            rotated = make_event("tenant-a", "evt_rotated", 1000, '{"ok":true}', "new-key")
            assert mod.verify_event(rotated, rotated_keys, store, 1000) is True

            boundary = make_event("tenant-a", "evt_boundary", 700, '{"ok":true}', "k1")
            assert mod.verify_event(boundary, keys, store, 1000) is True

            bad = make_event("tenant-a", "evt_bad", 1000, '{"bad":true}', "k1")
            bad["signature"] = "t=1000,v1=bad"
            try:
                mod.verify_event(bad, keys, store, 1000)
            except mod.WebhookError:
                pass
            else:
                raise AssertionError("bad signature was accepted")
            fixed = make_event("tenant-a", "evt_bad", 1000, '{"bad":true}', "k1")
            assert mod.verify_event(fixed, keys, store, 1000) is True

            expired = make_event("tenant-a", "evt_expired", 1000, '{"old":true}', "k1")
            assert mod.verify_event(expired, keys, store, 1000) is True
            fresh = make_event("tenant-a", "evt_fresh", 1299, '{"fresh":true}', "k1")
            assert mod.verify_event(fresh, keys, store, 1300) is True
            later = make_event("tenant-a", "evt_later", 1600, '{"later":true}', "k1")
            assert mod.verify_event(later, keys, store, 1600) is True
            expired_again = make_event("tenant-a", "evt_expired", 1600, '{"old":true}', "k1")
            assert mod.verify_event(expired_again, keys, store, 1600) is True

            mismatch = make_event("tenant-a", "evt_mismatch", 1000, '{"x":1}', "k1")
            mismatch["signature"] = sign(999, '{"x":1}', "k1")
            try:
                mod.verify_event(mismatch, keys, store, 1000)
            except mod.WebhookError as error:
                assert "timestamp" in str(error).lower()
            else:
                raise AssertionError("mismatched signature timestamp was accepted")
        """),
    },
    {
        "task_id": "HARD-048",
        "category": "multi_turn_change",
        "repo_hint": "python/cursor_pagination",
        "instruction": "Fix cursor pagination so list_page(items, limit, cursor=None, *, order=\"desc\") uses stable keyset pagination. Results must sort by created_at then id, duplicate timestamps must page deterministically, the cursor item must be excluded from the next page, malformed cursors must raise CursorError, limits must be clamped to the documented range, and inputs must not be mutated. Preserve Page(items, next_cursor) and CursorError. Use only the Python standard library.",
        "public_success_check": "python3 -m unittest discover -s tests",
        "success_check": "python3 ../grader/check.py",
        "files": {
            "README.md": """
                # cursor-pagination

                `list_page(items, limit, cursor=None, *, order="desc")` returns
                a `Page(items, next_cursor)` for API-style cursor pagination.

                Item shape:

                ```python
                {"id": "item-id", "created_at": 1700000000, ...}
                ```

                Requirements:

                - sort by `(created_at, id)` for deterministic keyset pages
                - support `order="desc"` and `order="asc"`
                - exclude the cursor item from the next page
                - keep pagination stable when new records are inserted before
                  the cursor between requests
                - clamp limits into `1 <= limit <= MAX_LIMIT`
                - raise `CursorError` for malformed or tampered cursors
                - do not mutate the input list or item dictionaries
            """,
            "src/cursor_pagination.py": """
                from __future__ import annotations

                import base64
                import json
                from dataclasses import dataclass


                MAX_LIMIT = 100


                class CursorError(Exception):
                    pass


                @dataclass
                class Page:
                    items: list
                    next_cursor: str | None


                def _encode_cursor(offset):
                    payload = json.dumps({"offset": offset}).encode("utf-8")
                    return base64.urlsafe_b64encode(payload).decode("ascii")


                def _decode_cursor(cursor):
                    try:
                        data = base64.urlsafe_b64decode(cursor.encode("ascii"))
                        return json.loads(data.decode("utf-8"))["offset"]
                    except Exception as exc:
                        raise CursorError("malformed cursor") from exc


                def list_page(items, limit, cursor=None, *, order="desc"):
                    if order not in {"asc", "desc"}:
                        raise ValueError("order must be asc or desc")

                    start = _decode_cursor(cursor) if cursor else 0
                    limit = max(1, min(int(limit), MAX_LIMIT))

                    items.sort(
                        key=lambda item: item["created_at"],
                        reverse=(order == "desc"),
                    )
                    page_items = items[start:start + limit]
                    next_offset = start + len(page_items)
                    next_cursor = None
                    if next_offset < len(items):
                        next_cursor = _encode_cursor(next_offset)
                    return Page(page_items, next_cursor)
            """,
            "tests/test_cursor_pagination.py": """
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
            """,
        },
        "grader": py_grader("""
            import base64
            import copy
            import json

            run_visible_tests()
            mod = importlib.import_module("cursor_pagination")

            items = [
                {"id": "b", "created_at": 100, "title": "B"},
                {"id": "a", "created_at": 100, "title": "A"},
                {"id": "c", "created_at": 90, "title": "C"},
                {"id": "d", "created_at": 80, "title": "D"},
            ]
            before = copy.deepcopy(items)

            page1 = mod.list_page(items, 2)
            assert [item["id"] for item in page1.items] == ["b", "a"]
            assert page1.next_cursor is not None
            assert items == before

            changed = [{"id": "z", "created_at": 200, "title": "Z"}, *items]
            page2 = mod.list_page(changed, 2, page1.next_cursor)
            assert [item["id"] for item in page2.items] == ["c", "d"]
            assert page2.next_cursor is None

            asc = mod.list_page(items, 3, order="asc")
            assert [item["id"] for item in asc.items] == ["d", "c", "a"]
            asc2 = mod.list_page(items, 3, asc.next_cursor, order="asc")
            assert [item["id"] for item in asc2.items] == ["b"]

            many = [{"id": str(i), "created_at": i} for i in range(150)]
            capped = mod.list_page(many, 1000)
            assert len(capped.items) == mod.MAX_LIMIT
            minimum = mod.list_page(many, 0)
            assert len(minimum.items) == 1

            first = mod.list_page(items, 1)
            second = mod.list_page(items, 1, first.next_cursor)
            assert first.items[0]["id"] != second.items[0]["id"]

            tampered_payloads = [
                "abc",
                base64.urlsafe_b64encode(json.dumps({"offset": 1}).encode("utf-8")).decode("ascii"),
                base64.urlsafe_b64encode(json.dumps({"created_at": 100}).encode("utf-8")).decode("ascii"),
                base64.urlsafe_b64encode(json.dumps({"created_at": 100, "id": "missing"}).encode("utf-8")).decode("ascii"),
            ]
            for bad in tampered_payloads:
                try:
                    mod.list_page(items, 2, bad)
                except mod.CursorError:
                    pass
                else:
                    raise AssertionError(f"bad cursor was accepted: {bad}")
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
