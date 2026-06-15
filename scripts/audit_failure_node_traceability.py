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
from codex_trace.report import render_json, render_markdown


DEFAULT_TRACE = Path("demo/failing-codex-trace.jsonl")
DEFAULT_BENCHMARK_MANIFEST = Path("benchmark/hard/pilot/hard30-real/runs.jsonl")
DEFAULT_BENCHMARK_RUN_DIR = Path("benchmark/hard/pilot/hard30-real")
DEFAULT_SCHEMA = Path("codex_trace/schema.py")
DEFAULT_DIAGNOSE = Path("codex_trace/diagnose.py")
DEFAULT_REPORT = Path("codex_trace/report.py")
DEFAULT_WEB_MAIN = Path("web/src/main.tsx")
DEFAULT_WEB_STYLES = Path("web/src/styles.css")
EXPECTED_DEMO_FINDINGS = (
    "command_failure_unhandled",
    "verification_gap",
    "premature_completion",
    "repeated_search_or_read",
    "sandbox_or_permission_block",
)


def build_failure_node_traceability_audit(
    trace_path: Path = DEFAULT_TRACE,
    benchmark_manifest_path: Path = DEFAULT_BENCHMARK_MANIFEST,
    benchmark_run_dir: Path = DEFAULT_BENCHMARK_RUN_DIR,
    schema_path: Path = DEFAULT_SCHEMA,
    diagnose_path: Path = DEFAULT_DIAGNOSE,
    report_path: Path = DEFAULT_REPORT,
    web_main_path: Path = DEFAULT_WEB_MAIN,
    web_styles_path: Path = DEFAULT_WEB_STYLES,
) -> dict[str, Any]:
    trace = parse_jsonl(trace_path)
    diagnosis = diagnose(trace)
    event_ids = {event.id for event in trace.events}
    report_json = json.loads(render_json(trace, diagnosis))
    report_markdown = render_markdown(trace, diagnosis)
    source_texts = {
        "schema": schema_path.read_text(encoding="utf-8"),
        "diagnose": diagnose_path.read_text(encoding="utf-8"),
        "report": report_path.read_text(encoding="utf-8"),
        "web_main": web_main_path.read_text(encoding="utf-8"),
        "web_styles": web_styles_path.read_text(encoding="utf-8"),
    }

    finding_rows = []
    for finding in diagnosis.findings:
        missing_event_ids = [event_id for event_id in finding.event_ids if event_id not in event_ids]
        finding_rows.append({
            "code": finding.code,
            "severity": finding.severity,
            "evidence_count": len(finding.evidence),
            "has_recommendation": bool(finding.recommendation.strip()),
            "event_ids": finding.event_ids,
            "event_id_count": len(finding.event_ids),
            "missing_event_ids": missing_event_ids,
            "covered": bool(finding.evidence)
            and bool(finding.recommendation.strip())
            and bool(finding.event_ids)
            and not missing_event_ids,
        })

    report_findings = report_json["diagnosis"]["findings"]
    json_event_id_findings = sum(1 for finding in report_findings if finding.get("event_ids"))
    markdown_event_id_lines = report_markdown.count("- Event IDs:")
    highlighted_event_ids = sorted({
        event_id
        for finding in diagnosis.findings
        for event_id in finding.event_ids
    })
    expected_present = sorted(set(EXPECTED_DEMO_FINDINGS) & {row["code"] for row in finding_rows})
    benchmark = _benchmark_finding_event_id_coverage(benchmark_manifest_path, benchmark_run_dir)
    source_checks = {
        "schema_event_ids": "event_ids: list[str]" in source_texts["schema"],
        "diagnose_event_ids": "event_ids=" in source_texts["diagnose"],
        "markdown_event_ids": "- Event IDs:" in source_texts["report"],
        "web_flatmap_event_ids": ".flatMap((finding) => finding.event_ids)" in source_texts["web_main"],
        "web_highlight_class": "highlighted.has(event.id)" in source_texts["web_main"],
        "web_highlight_style": ".event.highlighted" in source_texts["web_styles"],
    }

    return {
        "summary": {
            "ready": all(row["covered"] for row in finding_rows)
            and len(expected_present) == len(EXPECTED_DEMO_FINDINGS)
            and json_event_id_findings == len(finding_rows)
            and markdown_event_id_lines == len(finding_rows)
            and benchmark["trace_count"] == 60
            and benchmark["finding_count"] > 0
            and benchmark["missing_event_id_findings"] == 0
            and all(source_checks.values()),
            "trace": str(trace_path),
            "finding_count": len(finding_rows),
            "expected_demo_findings": len(EXPECTED_DEMO_FINDINGS),
            "expected_demo_findings_present": len(expected_present),
            "findings_with_event_ids": sum(1 for row in finding_rows if row["event_id_count"] > 0),
            "json_event_id_findings": json_event_id_findings,
            "markdown_event_id_lines": markdown_event_id_lines,
            "highlighted_event_count": len(highlighted_event_ids),
            "benchmark_manifest": str(benchmark_manifest_path),
            "benchmark_traces_checked": benchmark["trace_count"],
            "benchmark_finding_count": benchmark["finding_count"],
            "benchmark_findings_with_event_ids": benchmark["findings_with_event_ids"],
            "benchmark_missing_event_id_findings": benchmark["missing_event_id_findings"],
        },
        "source_checks": source_checks,
        "findings": finding_rows,
        "benchmark_finding_counts": benchmark["finding_counts"],
        "highlighted_event_ids": highlighted_event_ids,
    }


def render_failure_node_traceability_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Failure Node Traceability Audit",
        "",
        "This generated audit checks that diagnosis findings carry trace event IDs from parser output through JSON reports, Markdown reports, and the Web UI highlight path.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Demo trace: `{summary['trace']}`",
        f"- Demo findings: {summary['finding_count']}",
        f"- Expected demo findings present: {summary['expected_demo_findings_present']} / {summary['expected_demo_findings']}",
        f"- Findings with event IDs: {summary['findings_with_event_ids']} / {summary['finding_count']}",
        f"- JSON findings with event IDs: {summary['json_event_id_findings']} / {summary['finding_count']}",
        f"- Markdown Event IDs lines: {summary['markdown_event_id_lines']} / {summary['finding_count']}",
        f"- Highlighted event nodes: {summary['highlighted_event_count']}",
        f"- Benchmark manifest: `{summary['benchmark_manifest']}`",
        f"- Benchmark traces checked: {summary['benchmark_traces_checked']}",
        f"- Benchmark findings with event IDs: {summary['benchmark_findings_with_event_ids']} / {summary['benchmark_finding_count']}",
        f"- Benchmark findings missing event IDs: {summary['benchmark_missing_event_id_findings']}",
        "",
        "## Source Path Checks",
        "",
        "| Check | Covered |",
        "| --- | --- |",
    ]
    for name, covered in result["source_checks"].items():
        lines.append(f"| `{name}` | {_yes(covered)} |")

    lines.extend([
        "",
        "## Finding Node Coverage",
        "",
        "| Finding | Severity | Evidence | Recommendation | Event IDs | Covered |",
        "| --- | --- | ---: | --- | ---: | --- |",
    ])
    for row in result["findings"]:
        lines.append(
            f"| `{row['code']}` | `{row['severity']}` | {row['evidence_count']} | "
            f"{_yes(row['has_recommendation'])} | {row['event_id_count']} | {_yes(row['covered'])} |"
        )
    lines.extend([
        "",
        "## Benchmark Finding Counts",
        "",
        "| Finding | Count |",
        "| --- | ---: |",
    ])
    for code, count in result["benchmark_finding_counts"].items():
        lines.append(f"| `{code}` | {count} |")
    lines.extend([
        "",
        "Interpretation: this audit covers process-finding node traceability. It does not claim that hidden semantic failures have visible failure nodes; those remain a separate detector-boundary result.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_failure_node_traceability_markdown(result), encoding="utf-8")


def _yes(value: bool) -> str:
    return "yes" if value else "no"


def _benchmark_finding_event_id_coverage(manifest_path: Path, run_dir: Path) -> dict[str, Any]:
    rows = [
        json.loads(line)
        for line in manifest_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    finding_counts: dict[str, int] = {}
    trace_count = 0
    finding_count = 0
    findings_with_event_ids = 0
    missing_event_id_findings = 0
    for row in rows:
        trace_path = run_dir / str(row.get("trace_path", ""))
        trace = parse_jsonl(trace_path)
        diagnosis = diagnose(trace)
        event_ids = {event.id for event in trace.events}
        trace_count += 1
        for finding in diagnosis.findings:
            finding_counts[finding.code] = finding_counts.get(finding.code, 0) + 1
            finding_count += 1
            has_valid_event_ids = bool(finding.event_ids) and all(event_id in event_ids for event_id in finding.event_ids)
            if has_valid_event_ids:
                findings_with_event_ids += 1
            else:
                missing_event_id_findings += 1
    return {
        "trace_count": trace_count,
        "finding_count": finding_count,
        "findings_with_event_ids": findings_with_event_ids,
        "missing_event_id_findings": missing_event_id_findings,
        "finding_counts": dict(sorted(finding_counts.items())),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit diagnosis finding event-ID traceability into report and UI outputs.")
    parser.add_argument("--trace", type=Path, default=DEFAULT_TRACE)
    parser.add_argument("--benchmark-manifest", type=Path, default=DEFAULT_BENCHMARK_MANIFEST)
    parser.add_argument("--benchmark-run-dir", type=Path, default=DEFAULT_BENCHMARK_RUN_DIR)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_failure_node_traceability_audit(args.trace, args.benchmark_manifest, args.benchmark_run_dir)
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_failure_node_traceability_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
