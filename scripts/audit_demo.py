from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_SCRIPT = Path("scripts/demo.sh")
EXPECTED_FINDINGS = (
    "verification_gap",
    "command_failure_unhandled",
    "repeated_search_or_read",
    "sandbox_or_permission_block",
    "premature_completion",
)


def build_demo_audit(script_path: Path = DEFAULT_SCRIPT) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="codextrace-demo-audit-") as tmp_name:
        output_dir = Path(tmp_name)
        result = subprocess.run(
            ["bash", str(script_path), "--output-dir", str(output_dir)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        report_json = output_dir / "demo-report.json"
        report_md = output_dir / "demo-report.md"
        json_text = report_json.read_text(encoding="utf-8") if report_json.exists() else ""
        markdown_text = report_md.read_text(encoding="utf-8") if report_md.exists() else ""
        report = json.loads(json_text) if json_text else {}

    findings = report.get("diagnosis", {}).get("findings", [])
    finding_codes = sorted({str(row.get("code", "")) for row in findings})
    findings_with_event_ids = sum(1 for row in findings if row.get("event_ids"))
    expected_present = {
        code: code in finding_codes and code in markdown_text
        for code in EXPECTED_FINDINGS
    }
    stdout_checks = {
        "demo_header": "== CodexTrace demo ==" in result.stdout,
        "json_step": "1. Generate JSON diagnosis" in result.stdout,
        "markdown_step": "2. Generate Markdown diagnosis" in result.stdout,
        "preview": "Preview CLI report:" in result.stdout,
        "visual_replay_hint": "Run the visual replay:" in result.stdout,
    }
    output_checks = {
        "json_report": bool(json_text and report_json.name in result.stdout),
        "markdown_report": bool(markdown_text and report_md.name in result.stdout),
        "diagnosis_object": "diagnosis" in report,
        "event_ids": findings_with_event_ids == len(EXPECTED_FINDINGS),
        "markdown_title": "# CodexTrace Diagnosis" in markdown_text,
    }
    ready = (
        result.returncode == 0
        and all(stdout_checks.values())
        and all(output_checks.values())
        and all(expected_present.values())
    )
    return {
        "summary": {
            "ready": ready,
            "script": str(script_path),
            "exit_code": result.returncode,
            "expected_finding_count": len(EXPECTED_FINDINGS),
            "covered_finding_count": sum(1 for value in expected_present.values() if value),
            "findings_with_event_ids": findings_with_event_ids,
            "stdout_checks": sum(1 for value in stdout_checks.values() if value),
            "output_checks": sum(1 for value in output_checks.values() if value),
        },
        "stdout_checks": stdout_checks,
        "output_checks": output_checks,
        "expected_findings": expected_present,
        "finding_codes": finding_codes,
        "stdout_tail": result.stdout.splitlines()[-8:],
        "stderr": result.stderr,
    }


def render_demo_audit_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Demo Audit",
        "",
        "This generated audit runs the reviewer-facing offline demo script and checks that it emits JSON and Markdown diagnosis artifacts with traceable failure findings.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Script: `{summary['script']}`",
        f"- Exit code: {summary['exit_code']}",
        f"- Expected findings covered: {summary['covered_finding_count']} / {summary['expected_finding_count']}",
        f"- Findings with event IDs: {summary['findings_with_event_ids']} / {summary['expected_finding_count']}",
        f"- Stdout checks covered: {summary['stdout_checks']} / {len(result['stdout_checks'])}",
        f"- Output checks covered: {summary['output_checks']} / {len(result['output_checks'])}",
        "",
        "## Finding Coverage",
        "",
        "| Finding | Covered |",
        "| --- | --- |",
    ]
    for code, covered in result["expected_findings"].items():
        lines.append(f"| `{code}` | {_yes(covered)} |")

    lines.extend([
        "",
        "## Demo Output Checks",
        "",
        "| Check | Covered |",
        "| --- | --- |",
    ])
    for name, covered in result["output_checks"].items():
        lines.append(f"| `{name}` | {_yes(covered)} |")

    lines.extend([
        "",
        "Interpretation: this audit proves the committed offline demo path works without re-running Codex. It does not start the optional Web UI.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_demo_audit_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the reviewer-facing offline demo script.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_demo_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_demo_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
