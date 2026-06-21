from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_CI = Path(".github/workflows/ci.yml")
DEFAULT_PYPROJECT = Path("pyproject.toml")
DEFAULT_MAKEFILE = Path("Makefile")


CI_CHECKS = (
    {
        "id": "checkout",
        "phrase": "actions/checkout@v5",
        "description": "checks out repository sources",
    },
    {
        "id": "setup_python",
        "phrase": "actions/setup-python@v5",
        "description": "installs the Python runtime",
    },
    {
        "id": "python_312",
        "phrase": 'python-version: "3.12"',
        "description": "pins CI to Python 3.12",
    },
    {
        "id": "editable_dev_install",
        "phrase": 'pip install -e ".[dev]"',
        "description": "installs package and dev dependencies",
    },
    {
        "id": "pytest",
        "phrase": "run: pytest",
        "description": "runs Python tests",
    },
    {
        "id": "submission_readiness",
        "phrase": "PYTHONPATH=. python3 scripts/check_submission_readiness.py",
        "description": "runs the paper artifact readiness gate",
    },
    {
        "id": "docker_sandbox_smoke",
        "phrase": "codex-trace sandbox run --tasks benchmark/smoke/tasks.jsonl --task-id SM-001 --output-dir /tmp/codextrace-docker-real --image python:3.12-slim --timeout-seconds 60",
        "description": "runs one smoke fixture through the Docker sandbox runner",
    },
    {
        "id": "setup_node",
        "phrase": "actions/setup-node@v4",
        "description": "installs the Node runtime",
    },
    {
        "id": "node_22",
        "phrase": 'node-version: "22"',
        "description": "pins CI to Node 22",
    },
    {
        "id": "web_install",
        "phrase": "run: npm ci\n        working-directory: web",
        "description": "installs Web UI dependencies",
    },
    {
        "id": "web_build",
        "phrase": "run: npm run build\n        working-directory: web",
        "description": "builds the Web replay artifact",
    },
)

PYPROJECT_CHECKS = (
    {
        "id": "project_name",
        "phrase": 'name = "codex-trace"',
        "description": "declares the package name",
    },
    {
        "id": "python_requirement",
        "phrase": 'requires-python = ">=3.10"',
        "description": "declares supported Python versions",
    },
    {
        "id": "dev_extra_pytest",
        "phrase": 'dev = ["pytest>=8.0"]',
        "description": "exposes pytest through the dev extra",
    },
    {
        "id": "console_script",
        "phrase": 'codex-trace = "codex_trace.cli:main"',
        "description": "installs the codex-trace CLI entry point",
    },
    {
        "id": "build_backend",
        "phrase": 'build-backend = "setuptools.build_meta"',
        "description": "declares a setuptools build backend",
    },
    {
        "id": "pytest_pythonpath",
        "phrase": 'pythonpath = ["."]',
        "description": "keeps tests importable from repository root",
    },
)

MAKE_CHECKS = (
    {"id": "test", "phrase": "test:", "description": "local pytest target"},
    {"id": "demo", "phrase": "demo:", "description": "offline demo target"},
    {"id": "web_build", "phrase": "web-build:", "description": "local Web build target"},
)


def build_ci_surface_audit(
    ci_path: Path = DEFAULT_CI,
    pyproject_path: Path = DEFAULT_PYPROJECT,
    makefile_path: Path = DEFAULT_MAKEFILE,
) -> dict[str, Any]:
    ci_text = ci_path.read_text(encoding="utf-8")
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    makefile_text = makefile_path.read_text(encoding="utf-8")

    ci_rows = _check_phrases(CI_CHECKS, ci_text)
    pyproject_rows = _check_phrases(PYPROJECT_CHECKS, pyproject_text)
    make_rows = _check_phrases(MAKE_CHECKS, makefile_text)

    return {
        "summary": {
            "ready": all(row["present"] for row in ci_rows + pyproject_rows + make_rows),
            "ci_check_count": len(ci_rows),
            "covered_ci_check_count": sum(1 for row in ci_rows if row["present"]),
            "packaging_check_count": len(pyproject_rows),
            "covered_packaging_check_count": sum(1 for row in pyproject_rows if row["present"]),
            "make_check_count": len(make_rows),
            "covered_make_check_count": sum(1 for row in make_rows if row["present"]),
            "ci_path": str(ci_path),
            "pyproject_path": str(pyproject_path),
            "makefile_path": str(makefile_path),
        },
        "ci_checks": ci_rows,
        "packaging_checks": pyproject_rows,
        "make_checks": make_rows,
    }


def render_ci_surface_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# CI Surface Audit",
        "",
        "This generated audit checks that the repository CI and packaging surface exercise the paper artifact's core offline gates.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- CI checks covered: {summary['covered_ci_check_count']} / {summary['ci_check_count']}",
        f"- Packaging checks covered: {summary['covered_packaging_check_count']} / {summary['packaging_check_count']}",
        f"- Makefile checks covered: {summary['covered_make_check_count']} / {summary['make_check_count']}",
        f"- CI workflow: `{summary['ci_path']}`",
        f"- Python package metadata: `{summary['pyproject_path']}`",
        f"- Local task runner: `{summary['makefile_path']}`",
        "",
        "## CI Checks",
        "",
        "| Check | Description | Covered |",
        "| --- | --- | --- |",
    ]
    for row in result["ci_checks"]:
        lines.append(f"| `{row['id']}` | {row['description']} | {'yes' if row['present'] else 'no'} |")

    lines.extend([
        "",
        "## Packaging Checks",
        "",
        "| Check | Description | Covered |",
        "| --- | --- | --- |",
    ])
    for row in result["packaging_checks"]:
        lines.append(f"| `{row['id']}` | {row['description']} | {'yes' if row['present'] else 'no'} |")

    lines.extend([
        "",
        "## Makefile Checks",
        "",
        "| Check | Description | Covered |",
        "| --- | --- | --- |",
    ])
    for row in result["make_checks"]:
        lines.append(f"| `{row['id']}` | {row['description']} | {'yes' if row['present'] else 'no'} |")

    lines.extend([
        "",
        "Interpretation: this audit checks committed CI and packaging declarations. It does not execute GitHub Actions itself.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_ci_surface_markdown(result), encoding="utf-8")


def _check_phrases(checks: tuple[dict[str, str], ...], text: str) -> list[dict[str, Any]]:
    return [
        {
            "id": check["id"],
            "phrase": check["phrase"],
            "description": check["description"],
            "present": check["phrase"] in text,
        }
        for check in checks
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit CI and packaging coverage for the CodexTrace artifact.")
    parser.add_argument("--ci", type=Path, default=DEFAULT_CI)
    parser.add_argument("--pyproject", type=Path, default=DEFAULT_PYPROJECT)
    parser.add_argument("--makefile", type=Path, default=DEFAULT_MAKEFILE)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_ci_surface_audit(args.ci, args.pyproject, args.makefile)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_ci_surface_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
