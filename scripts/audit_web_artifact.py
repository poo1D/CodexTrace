from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.diagnose import diagnose
from codex_trace.parser import parse_jsonl
from codex_trace.report import render_json


DEFAULT_TRACE = Path("demo/failing-codex-trace.jsonl")
DEFAULT_REPORT = Path("web/public/report.json")
DEFAULT_MAIN = Path("web/src/main.tsx")
DEFAULT_STYLES = Path("web/src/styles.css")
DEFAULT_PACKAGE = Path("web/package.json")
DEFAULT_INDEX = Path("web/index.html")
EXPECTED_FINDINGS = (
    "command_failure_unhandled",
    "verification_gap",
    "premature_completion",
    "repeated_search_or_read",
    "sandbox_or_permission_block",
)


def build_web_artifact_audit(
    trace_path: Path = DEFAULT_TRACE,
    report_path: Path = DEFAULT_REPORT,
    main_path: Path = DEFAULT_MAIN,
    styles_path: Path = DEFAULT_STYLES,
    package_path: Path = DEFAULT_PACKAGE,
    index_path: Path = DEFAULT_INDEX,
) -> dict[str, Any]:
    expected_report = json.loads(render_json(parse_jsonl(trace_path), diagnose(parse_jsonl(trace_path))))
    web_report = json.loads(report_path.read_text(encoding="utf-8"))
    main_text = main_path.read_text(encoding="utf-8")
    styles_text = styles_path.read_text(encoding="utf-8")
    package = json.loads(package_path.read_text(encoding="utf-8"))
    index_text = index_path.read_text(encoding="utf-8")

    expected_findings = {
        finding["code"]: finding
        for finding in expected_report["diagnosis"]["findings"]
    }
    web_findings = {
        finding["code"]: finding
        for finding in web_report["diagnosis"]["findings"]
    }
    finding_rows = []
    for code in EXPECTED_FINDINGS:
        expected = expected_findings.get(code, {})
        actual = web_findings.get(code, {})
        finding_rows.append({
            "code": code,
            "present": bool(actual),
            "event_ids_match": actual.get("event_ids") == expected.get("event_ids"),
            "expected_event_ids": expected.get("event_ids", []),
            "actual_event_ids": actual.get("event_ids", []),
        })

    report_checks = {
        "event_count": len(web_report["trace"]["events"]) == len(expected_report["trace"]["events"]),
        "finding_count": len(web_report["diagnosis"]["findings"]) == len(EXPECTED_FINDINGS),
        "failure_score": web_report["diagnosis"]["failure_score"] == expected_report["diagnosis"]["failure_score"],
        "usage": web_report["trace"]["usage"] == expected_report["trace"]["usage"],
        "finding_event_ids": all(row["event_ids_match"] for row in finding_rows),
    }
    source_checks = {
        "fetch_report": 'fetch("/report.json")' in main_text,
        "fallback_report": "catch(() => setReport(demoReport))" in main_text,
        "finding_event_flatmap": ".flatMap((finding) => finding.event_ids)" in main_text,
        "highlighted_class": "highlighted.has(event.id)" in main_text,
        "highlighted_style": ".event.highlighted" in styles_text,
        "responsive_css": "@media (max-width: 860px)" in styles_text,
        "vite_build_script": package.get("scripts", {}).get("build") == "tsc && vite build",
        "react_dependency": "react" in package.get("dependencies", {}),
        "root_mount": '<div id="root"></div>' in index_text,
    }
    ready = all(report_checks.values()) and all(source_checks.values()) and all(row["present"] for row in finding_rows)
    return {
        "summary": {
            "ready": ready,
            "trace": str(trace_path),
            "web_report": str(report_path),
            "expected_findings": len(EXPECTED_FINDINGS),
            "covered_findings": sum(1 for row in finding_rows if row["present"] and row["event_ids_match"]),
            "report_checks": sum(1 for value in report_checks.values() if value),
            "source_checks": sum(1 for value in source_checks.values() if value),
        },
        "report_checks": report_checks,
        "source_checks": source_checks,
        "findings": finding_rows,
    }


def render_web_artifact_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Web Artifact Audit",
        "",
        "This generated audit checks that the committed Web replay fixture matches the current demo diagnosis and that the TypeScript UI preserves the event-ID highlight path.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Trace: `{summary['trace']}`",
        f"- Web report: `{summary['web_report']}`",
        f"- Findings with matching event IDs: {summary['covered_findings']} / {summary['expected_findings']}",
        f"- Report checks covered: {summary['report_checks']} / {len(result['report_checks'])}",
        f"- Source checks covered: {summary['source_checks']} / {len(result['source_checks'])}",
        "",
        "## Finding Event-ID Coverage",
        "",
        "| Finding | Present | Event IDs match |",
        "| --- | --- | --- |",
    ]
    for row in result["findings"]:
        lines.append(f"| `{row['code']}` | {_yes(row['present'])} | {_yes(row['event_ids_match'])} |")

    lines.extend([
        "",
        "## UI Source Checks",
        "",
        "| Check | Covered |",
        "| --- | --- |",
    ])
    for name, covered in result["source_checks"].items():
        lines.append(f"| `{name}` | {_yes(covered)} |")

    lines.extend([
        "",
        "Interpretation: this audit covers the committed static Web artifact and source path. It does not install npm dependencies or start the Vite dev server.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_web_artifact_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the committed Web replay artifact.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_web_artifact_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_web_artifact_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
