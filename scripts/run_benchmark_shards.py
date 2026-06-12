from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TASKS = ROOT / "benchmark" / "verification-lift-v2" / "tasks.jsonl"
DEFAULT_PROMPT_DIR = ROOT / "benchmark" / "verification-lift-v2" / "prompts"
DEFAULT_RUN_DIR = ROOT / "benchmark" / "verification-lift-v2" / "pilot" / "full-real"


@dataclass(frozen=True)
class ShardCommand:
    task_id: str
    command: list[str]
    shard_dir: Path
    stdout_path: Path
    stderr_path: Path
    metadata_path: Path


@dataclass(frozen=True)
class ShardStatus:
    task_id: str
    complete: bool
    record_count: int
    manifest_path: Path
    prompt_types: tuple[str, ...] = ()
    returncode: int | None = None
    invalid_reasons: tuple[str, ...] = ()


def load_task_ids(tasks_path: Path = DEFAULT_TASKS) -> list[str]:
    rows = [json.loads(line) for line in tasks_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [str(row["task_id"]) for row in rows]


def select_task_ids(
    tasks_path: Path = DEFAULT_TASKS,
    explicit_task_ids: list[str] | None = None,
    offset: int = 0,
    limit: int | None = None,
) -> list[str]:
    if offset < 0:
        raise ValueError("offset must be non-negative")
    if limit is not None and limit < 1:
        raise ValueError("limit must be at least 1")
    task_ids = explicit_task_ids or load_task_ids(tasks_path)
    if explicit_task_ids:
        return task_ids
    selected = task_ids[offset:]
    if limit is not None:
        selected = selected[:limit]
    return selected


def build_shard_commands(
    task_ids: list[str],
    tasks_path: Path = DEFAULT_TASKS,
    prompt_dir: Path = DEFAULT_PROMPT_DIR,
    run_dir: Path = DEFAULT_RUN_DIR,
    timeout_seconds: int = 600,
    codex_bin: str = "codex",
    sandbox: str = "workspace-write",
    dry_run: bool = False,
) -> list[ShardCommand]:
    shards_root = run_dir / "shards"
    commands = []
    for task_id in task_ids:
        shard_dir = shards_root / task_id
        command = [
            sys.executable,
            "-m",
            "codex_trace.cli",
            "research",
            "run",
            "--tasks",
            str(tasks_path),
            "--prompt-dir",
            str(prompt_dir),
            "--output-dir",
            str(shard_dir),
            "--task-id",
            task_id,
            "--codex-bin",
            codex_bin,
            "--sandbox",
            sandbox,
            "--timeout-seconds",
            str(timeout_seconds),
        ]
        if dry_run:
            command.append("--dry-run")
        commands.append(ShardCommand(
            task_id=task_id,
            command=command,
            shard_dir=shard_dir,
            stdout_path=shard_dir / "shard-run.stdout",
            stderr_path=shard_dir / "shard-run.stderr",
            metadata_path=shard_dir / "shard-run.json",
        ))
    return commands


def inspect_shard(command: ShardCommand, expected_records: int = 2) -> ShardStatus:
    returncode = None
    invalid_reasons = []
    if command.metadata_path.exists():
        metadata = json.loads(command.metadata_path.read_text(encoding="utf-8"))
        if metadata.get("returncode") is not None:
            returncode = int(metadata["returncode"])
    manifest = command.shard_dir / "runs.jsonl"
    if not manifest.exists():
        return ShardStatus(command.task_id, False, 0, manifest, returncode=returncode)
    rows = [json.loads(line) for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip()]
    prompt_types = tuple(sorted(str(row.get("prompt_type", "")) for row in rows if row.get("prompt_type")))
    for row in rows:
        prompt_type = str(row.get("prompt_type", "unknown"))
        codex_exit_code = row.get("codex_exit_code")
        if codex_exit_code not in (None, 0):
            invalid_reasons.append(f"{prompt_type} codex_exit_code={codex_exit_code}")
        trace_path = str(row.get("trace_path", ""))
        if trace_path:
            trace_file = command.shard_dir / trace_path
            if not trace_file.exists():
                invalid_reasons.append(f"{prompt_type} missing trace: {trace_path}")
            elif trace_file.stat().st_size == 0:
                invalid_reasons.append(f"{prompt_type} empty trace: {trace_path}")
    complete = len(rows) == expected_records and returncode in (None, 0) and not invalid_reasons
    return ShardStatus(command.task_id, complete, len(rows), manifest, prompt_types, returncode, tuple(invalid_reasons))


def summarize_shards(commands: list[ShardCommand]) -> dict[str, Any]:
    statuses = [inspect_shard(command) for command in commands]
    completed = [status.task_id for status in statuses if status.complete]
    failed = [status.task_id for status in statuses if status.returncode not in (None, 0) or status.invalid_reasons]
    incomplete = [status.task_id for status in statuses if status.record_count and not status.complete]
    missing = [status.task_id for status in statuses if not status.record_count]
    total_records = sum(status.record_count for status in statuses)
    return {
        "task_count": len(statuses),
        "completed_count": len(completed),
        "failed_count": len(failed),
        "incomplete_count": len(incomplete),
        "missing_count": len(missing),
        "record_count": total_records,
        "expected_record_count": len(statuses) * 2,
        "ready_to_merge": len(statuses) > 0 and len(completed) == len(statuses),
        "completed": completed,
        "failed": failed,
        "incomplete": incomplete,
        "missing": missing,
        "shards": [
            {
                "task_id": status.task_id,
                "complete": status.complete,
                "record_count": status.record_count,
                "prompt_types": list(status.prompt_types),
                "returncode": status.returncode,
                "invalid_reasons": list(status.invalid_reasons),
                "manifest_path": str(status.manifest_path),
                "stdout_path": str(commands[index].stdout_path),
                "stderr_path": str(commands[index].stderr_path),
                "metadata_path": str(commands[index].metadata_path),
            }
            for index, status in enumerate(statuses)
        ],
    }


def render_status(summary: dict[str, Any]) -> str:
    lines = [
        "# Benchmark Shard Status",
        "",
        f"Tasks: {summary['task_count']}",
        f"Completed shards: {summary['completed_count']}",
        f"Failed shards: {summary['failed_count']}",
        f"Incomplete shards: {summary['incomplete_count']}",
        f"Missing shards: {summary['missing_count']}",
        f"Run records: {summary['record_count']} / {summary['expected_record_count']}",
        f"Ready to merge: {'yes' if summary['ready_to_merge'] else 'no'}",
    ]
    if summary["failed"]:
        lines.extend(["", f"Failed: {', '.join(summary['failed'])}"])
    if summary["incomplete"]:
        lines.extend(["", f"Incomplete: {', '.join(summary['incomplete'])}"])
    if summary["missing"]:
        lines.extend(["", f"Missing: {', '.join(summary['missing'])}"])
    return "\n".join(lines) + "\n"


def filter_commands(commands: list[ShardCommand], skip_complete: bool) -> list[ShardCommand]:
    if not skip_complete:
        return commands
    pending = []
    for command in commands:
        status = inspect_shard(command)
        if status.complete:
            print(f"{command.task_id}: skip complete ({status.record_count} records)")
        else:
            pending.append(command)
    return pending


def run_shard(command: ShardCommand) -> subprocess.CompletedProcess[str]:
    command.shard_dir.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["PYTHONPATH"] = str(ROOT)
    with command.stdout_path.open("w", encoding="utf-8") as stdout_handle, command.stderr_path.open("w", encoding="utf-8") as stderr_handle:
        result = subprocess.run(
            command.command,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=False,
        )
    command.metadata_path.write_text(
        json.dumps(
            {
                "task_id": command.task_id,
                "returncode": result.returncode,
                "command": command.command,
                "stdout_path": str(command.stdout_path),
                "stderr_path": str(command.stderr_path),
            },
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )
    return result


def run_shards(commands: list[ShardCommand], max_parallel: int) -> list[tuple[ShardCommand, int]]:
    if max_parallel < 1:
        raise ValueError("max_parallel must be at least 1")

    results = []
    with ThreadPoolExecutor(max_workers=max_parallel) as executor:
        futures = {executor.submit(run_shard, command): command for command in commands}
        for future in as_completed(futures):
            command = futures[future]
            result = future.result()
            results.append((command, result.returncode))
            status = "ok" if result.returncode == 0 else f"exit {result.returncode}"
            print(f"{command.task_id}: {status}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a CodexTrace benchmark pilot as isolated per-task shards.")
    parser.add_argument("--tasks", type=Path, default=DEFAULT_TASKS)
    parser.add_argument("--prompt-dir", type=Path, default=DEFAULT_PROMPT_DIR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--offset", type=int, default=0, help="Skip this many selected task ids before building shards.")
    parser.add_argument("--limit", type=int, help="Run or inspect at most this many selected task ids.")
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", default="workspace-write")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-complete", action="store_true", help="Do not rerun shards that already have two run records.")
    parser.add_argument("--status", action="store_true", help="Print shard completion status without running Codex.")
    parser.add_argument("--status-json", type=Path, help="Optionally write shard status as JSON.")
    args = parser.parse_args()

    try:
        selected_ids = select_task_ids(args.tasks, args.task_ids, args.offset, args.limit)
    except ValueError as error:
        print(error, file=sys.stderr)
        return 2
    commands = build_shard_commands(
        selected_ids,
        tasks_path=args.tasks,
        prompt_dir=args.prompt_dir,
        run_dir=args.run_dir,
        timeout_seconds=args.timeout_seconds,
        codex_bin=args.codex_bin,
        sandbox=args.sandbox,
        dry_run=args.dry_run,
    )
    if args.status:
        summary = summarize_shards(commands)
        print(render_status(summary), end="")
        if args.status_json:
            args.status_json.parent.mkdir(parents=True, exist_ok=True)
            args.status_json.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return 0 if summary["ready_to_merge"] else 1

    commands = filter_commands(commands, args.skip_complete)
    if not commands:
        print("No pending shard(s).")
        return 0
    results = run_shards(commands, args.max_parallel)
    failures = [(command.task_id, returncode) for command, returncode in results if returncode != 0]
    if failures:
        for task_id, returncode in failures:
            print(f"{task_id} failed with exit {returncode}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
