from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


DEFAULT_TASKS = Path("benchmark/verification-lift-v2/tasks.jsonl")
DEFAULT_RUN_DIR = Path("benchmark/verification-lift-v2/pilot/full-real")
PATH_FIELDS = ("trace_path", "workdir", "grader_path", "prompt_path")


def load_task_ids(tasks_path: Path = DEFAULT_TASKS) -> list[str]:
    rows = [json.loads(line) for line in tasks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [str(row["task_id"]) for row in rows]


def rewrite_shard_row(row: dict[str, Any], shard_prefix: Path) -> dict[str, Any]:
    rewritten = dict(row)
    for field in PATH_FIELDS:
        value = str(rewritten.get(field, ""))
        if value:
            rewritten[field] = str(shard_prefix / value)
    return rewritten


def merge_shards(
    run_dir: Path = DEFAULT_RUN_DIR,
    tasks_path: Path = DEFAULT_TASKS,
    task_ids: list[str] | None = None,
    allow_partial: bool = False,
) -> list[dict[str, Any]]:
    selected_ids = task_ids or load_task_ids(tasks_path)
    rows = []
    missing = []
    incomplete = []
    for task_id in selected_ids:
        shard_prefix = Path("shards") / task_id
        manifest = run_dir / shard_prefix / "runs.jsonl"
        if not manifest.exists():
            missing.append(task_id)
            continue
        shard_rows = [
            rewrite_shard_row(json.loads(line), shard_prefix)
            for line in manifest.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if len(shard_rows) != 2:
            incomplete.append((task_id, len(shard_rows)))
        rows.extend(shard_rows)

    if (missing or incomplete) and not allow_partial:
        problems = []
        if missing:
            problems.append(f"missing shards: {', '.join(missing)}")
        if incomplete:
            rendered = ", ".join(f"{task_id}={count}" for task_id, count in incomplete)
            problems.append(f"incomplete shard records: {rendered}")
        raise FileNotFoundError("; ".join(problems))

    output = run_dir / "runs.jsonl"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge per-task benchmark shard manifests into one runs.jsonl.")
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--allow-partial", action="store_true")
    args = parser.parse_args()

    try:
        rows = merge_shards(args.run_dir, args.tasks, args.task_ids, args.allow_partial)
    except FileNotFoundError as error:
        print(error, file=sys.stderr)
        return 1
    print(f"Wrote {len(rows)} run record(s) to {args.run_dir / 'runs.jsonl'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
