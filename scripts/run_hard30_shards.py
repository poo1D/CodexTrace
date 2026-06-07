from __future__ import annotations

import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SELECTION_DIR = ROOT / "benchmark" / "hard" / "pilot" / "hard30-selection"
DEFAULT_RUN_DIR = ROOT / "benchmark" / "hard" / "pilot" / "hard30-real"


@dataclass(frozen=True)
class ShardCommand:
    task_id: str
    command: list[str]
    shard_dir: Path
    stdout_path: Path
    stderr_path: Path


@dataclass(frozen=True)
class ShardStatus:
    task_id: str
    complete: bool
    record_count: int
    manifest_path: Path


def load_task_ids(selection_dir: Path = DEFAULT_SELECTION_DIR) -> list[str]:
    task_id_path = selection_dir / "task_ids.txt"
    return [line.strip() for line in task_id_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def build_shard_commands(
    task_ids: list[str],
    selection_dir: Path = DEFAULT_SELECTION_DIR,
    run_dir: Path = DEFAULT_RUN_DIR,
    timeout_seconds: int = 600,
    codex_bin: str = "codex",
    sandbox: str = "workspace-write",
    dry_run: bool = False,
) -> list[ShardCommand]:
    tasks_path = selection_dir / "tasks.jsonl"
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
        ))
    return commands


def inspect_shard(command: ShardCommand, expected_records: int = 2) -> ShardStatus:
    manifest = command.shard_dir / "runs.jsonl"
    if not manifest.exists():
        return ShardStatus(command.task_id, False, 0, manifest)
    record_count = sum(1 for line in manifest.read_text(encoding="utf-8").splitlines() if line.strip())
    return ShardStatus(command.task_id, record_count == expected_records, record_count, manifest)


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
        return subprocess.run(
            command.command,
            cwd=ROOT,
            env=env,
            text=True,
            stdout=stdout_handle,
            stderr=stderr_handle,
            check=False,
        )


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
    parser = argparse.ArgumentParser(description="Run the hard30 pilot as isolated per-task shards.")
    parser.add_argument("--selection-dir", type=Path, default=DEFAULT_SELECTION_DIR)
    parser.add_argument("--run-dir", type=Path, default=DEFAULT_RUN_DIR)
    parser.add_argument("--task-id", action="append", dest="task_ids")
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", default="workspace-write")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-complete", action="store_true", help="Do not rerun shards that already have two run records.")
    args = parser.parse_args()

    selected_ids = args.task_ids or load_task_ids(args.selection_dir)
    commands = build_shard_commands(
        selected_ids,
        selection_dir=args.selection_dir,
        run_dir=args.run_dir,
        timeout_seconds=args.timeout_seconds,
        codex_bin=args.codex_bin,
        sandbox=args.sandbox,
        dry_run=args.dry_run,
    )
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
