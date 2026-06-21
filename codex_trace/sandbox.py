from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .research import BenchmarkTask, initialize_git_repo, load_tasks, run_success_check


@dataclass
class DockerRunConfig:
    image: str = "python:3.12-slim"
    cpus: str = "1"
    memory: str = "512m"
    timeout_seconds: int = 60
    network: str = "none"
    command: str | None = None
    dry_run: bool = False


def run_docker_benchmark(
    tasks_path: str | Path,
    output_dir: str | Path,
    task_ids: list[str] | None = None,
    config: DockerRunConfig | None = None,
) -> list[dict[str, Any]]:
    cfg = config or DockerRunConfig()
    selected = set(task_ids or [])
    rows = []
    for task in load_tasks(tasks_path):
        if selected and task.task_id not in selected:
            continue
        rows.append(run_docker_task(task, output_dir, cfg))
    return rows


def run_docker_task(task: BenchmarkTask, output_dir: str | Path, config: DockerRunConfig) -> dict[str, Any]:
    if not task.fixture_path:
        raise ValueError(f"{task.task_id} does not define fixture_path")

    output_root = Path(output_dir)
    run_dir = output_root / task.task_id / "docker"
    repo_dir = run_dir / "repo"
    artifacts_dir = run_dir / "artifacts"
    stdout_path = artifacts_dir / "stdout.log"
    stderr_path = artifacts_dir / "stderr.log"
    diff_path = artifacts_dir / "diff.patch"
    report_path = artifacts_dir / "report.json"
    metadata_path = artifacts_dir / "metadata.json"

    if run_dir.exists():
        shutil.rmtree(run_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(task.fixture_path, repo_dir)
    initialize_git_repo(repo_dir)

    command = config.command or task.success_check
    docker_command = build_docker_command(repo_dir, command, config)
    started = time.time()
    timed_out = False
    if config.dry_run:
        completed = subprocess.CompletedProcess(docker_command, 0, "", "")
    else:
        try:
            completed = subprocess.run(
                docker_command,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=config.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            timed_out = True
            completed = subprocess.CompletedProcess(
                docker_command,
                124,
                _decode_timeout_output(error.stdout),
                _decode_timeout_output(error.stderr) or f"Timed out after {config.timeout_seconds}s",
            )
    duration_ms = round((time.time() - started) * 1000)

    stdout_path.write_text(completed.stdout or "", encoding="utf-8")
    stderr_path.write_text(completed.stderr or "", encoding="utf-8")
    diff_text = git_diff(repo_dir)
    diff_path.write_text(diff_text, encoding="utf-8")

    metadata = {
        "task_id": task.task_id,
        "image": config.image,
        "command": command,
        "docker_command": docker_command,
        "exit_code": completed.returncode,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "resource_limits": {
            "cpus": config.cpus,
            "memory": config.memory,
            "network": config.network,
            "timeout_seconds": config.timeout_seconds,
        },
        "workdir": str(repo_dir),
        "stdout_path": _relative_to(stdout_path, output_root),
        "stderr_path": _relative_to(stderr_path, output_root),
        "diff_path": _relative_to(diff_path, output_root),
    }
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = {
        "schema_version": 1,
        "task": {
            "task_id": task.task_id,
            "category": task.category,
            "instruction": task.instruction,
            "repo_hint": task.repo_hint,
        },
        "run": metadata,
        "logs": {
            "stdout": completed.stdout or "",
            "stderr": completed.stderr or "",
        },
        "diff": diff_text,
        "outcome": "success" if completed.returncode == 0 else "failure",
    }
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    return {
        "task_id": task.task_id,
        "runner": "docker",
        "outcome": report["outcome"],
        "exit_code": completed.returncode,
        "timed_out": timed_out,
        "duration_ms": duration_ms,
        "command": command,
        "workdir": _relative_to(repo_dir, output_root),
        "stdout_path": _relative_to(stdout_path, output_root),
        "stderr_path": _relative_to(stderr_path, output_root),
        "diff_path": _relative_to(diff_path, output_root),
        "metadata_path": _relative_to(metadata_path, output_root),
        "report_path": _relative_to(report_path, output_root),
    }


def build_docker_command(repo_dir: str | Path, command: str, config: DockerRunConfig) -> list[str]:
    return [
        "docker",
        "run",
        "--rm",
        "--network",
        config.network,
        "--cpus",
        str(config.cpus),
        "--memory",
        str(config.memory),
        "--workdir",
        "/workspace",
        "-v",
        f"{Path(repo_dir).resolve()}:/workspace",
        config.image,
        "sh",
        "-lc",
        command,
    ]


def write_docker_run_manifest(rows: list[dict[str, Any]], path: str | Path) -> None:
    manifest_path = Path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    with manifest_path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def smoke_check_fixture(task_id: str = "SM-001") -> subprocess.CompletedProcess[str]:
    tasks = {task.task_id: task for task in load_tasks("benchmark/smoke/tasks.jsonl")}
    return run_success_check(tasks[task_id].fixture_path, tasks[task_id].success_check, timeout_seconds=30)


def git_diff(repo_dir: str | Path) -> str:
    result = subprocess.run(
        ["git", "diff", "--binary"],
        cwd=repo_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return result.stderr
    return result.stdout


def _decode_timeout_output(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _relative_to(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
