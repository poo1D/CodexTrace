from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from codex_trace.research import build_paper_report


DEFAULT_HARD30_REPORT = Path("benchmark/hard/pilot/hard30-real/paper-report-labeled.json")
DEFAULT_FULL30_MANIFEST = Path("benchmark/pilot/full30-real/runs.jsonl")
DEFAULT_FULL30_PROCESS_LABELS = Path("benchmark/pilot/full30-real/process-labels.jsonl")
DEFAULT_DETECTOR_FIXTURE_MANIFEST = Path("benchmark/detector-fixtures/runs.jsonl")
DEFAULT_DETECTOR_FIXTURE_LABELS = Path("benchmark/detector-fixtures/labels.jsonl")


def build_rq4_signal_audit(
    hard30_report_path: Path = DEFAULT_HARD30_REPORT,
    full30_manifest_path: Path = DEFAULT_FULL30_MANIFEST,
    full30_process_labels_path: Path = DEFAULT_FULL30_PROCESS_LABELS,
    detector_fixture_manifest_path: Path = DEFAULT_DETECTOR_FIXTURE_MANIFEST,
    detector_fixture_labels_path: Path = DEFAULT_DETECTOR_FIXTURE_LABELS,
) -> dict[str, Any]:
    hard30 = _read_json(hard30_report_path)
    full30 = build_paper_report(full30_manifest_path, labels_path=full30_process_labels_path)
    fixtures = build_paper_report(detector_fixture_manifest_path, labels_path=detector_fixture_labels_path)

    hard30_outcome = {row["signal"]: row for row in hard30["signal_by_outcome"]}
    hidden_boundary = {
        "verification_delta_success_minus_failure": hard30_outcome["verification_rate"]["delta_success_minus_failure"],
        "unresolved_error_delta_success_minus_failure": hard30_outcome["unresolved_error"]["delta_success_minus_failure"],
        "token_usage_delta_success_minus_failure": hard30_outcome["token_usage"]["delta_success_minus_failure"],
        "failure_score_delta_success_minus_failure": hard30_outcome["failure_score"]["delta_success_minus_failure"],
    }

    hard30_repetitive = _top_label_signals(hard30["signal_by_label"], "repetitive_exploration")
    full30_sandbox = _top_label_signals(full30["signal_by_label"], "sandbox_permission_deadlock")
    fixture_labels = sorted({row["failure_tag"] for row in fixtures["signal_by_label"]})
    fixture_top = {
        label: _top_label_signals(fixtures["signal_by_label"], label, limit=3)
        for label in fixture_labels
    }

    ready = (
        hidden_boundary["verification_delta_success_minus_failure"] == 0
        and hidden_boundary["unresolved_error_delta_success_minus_failure"] == 0
        and len(hard30_repetitive) >= 3
        and len(full30_sandbox) >= 3
        and len(fixture_top) >= 6
    )
    return {
        "summary": {
            "ready": ready,
            "hard30_hidden_boundary": hidden_boundary,
            "hard30_repetitive_top_signal_count": len(hard30_repetitive),
            "full30_sandbox_top_signal_count": len(full30_sandbox),
            "detector_fixture_label_count": len(fixture_top),
        },
        "hard30_hidden_boundary": hidden_boundary,
        "hard30_repetitive_exploration_top_signals": hard30_repetitive,
        "full30_sandbox_permission_top_signals": full30_sandbox,
        "detector_fixture_top_signals_by_label": fixture_top,
    }


def render_rq4_signal_audit_markdown(result: dict[str, Any]) -> str:
    boundary = result["hard30_hidden_boundary"]
    lines = [
        "# RQ4 Signal Audit",
        "",
        "This generated audit summarizes which trace signals explain observable process labels and where trace signals fail to explain hidden semantic outcome failures.",
        "",
        "## Summary",
        "",
        f"- Ready for boundary-style RQ4 claim: {'yes' if result['summary']['ready'] else 'no'}",
        f"- Detector-fixture labels with top signals: {result['summary']['detector_fixture_label_count']}",
        f"- Hard30 hidden semantic verification delta: {boundary['verification_delta_success_minus_failure']:+.2f}",
        f"- Hard30 hidden semantic unresolved-error delta: {boundary['unresolved_error_delta_success_minus_failure']:+.2f}",
        "",
        "## Hidden Semantic Boundary",
        "",
        "| Signal | Delta success-failure | Interpretation |",
        "| --- | ---: | --- |",
        f"| verification_rate | {boundary['verification_delta_success_minus_failure']:+.2f} | Hidden failures are still verified. |",
        f"| unresolved_error | {boundary['unresolved_error_delta_success_minus_failure']:+.2f} | Hidden failures do not leave unresolved tool errors. |",
        f"| token_usage | {boundary['token_usage_delta_success_minus_failure']:+.1f} | Token usage does not reliably expose hidden correctness. |",
        f"| failure_score | {boundary['failure_score_delta_success_minus_failure']:+.2f} | Process failure score does not rank hidden correctness. |",
        "",
        "## Real Process Positives",
        "",
        "### Hard30 Repetitive Exploration",
        "",
        "| Signal | Label mean | Baseline mean | Delta label-baseline |",
        "| --- | ---: | ---: | ---: |",
    ]
    for row in result["hard30_repetitive_exploration_top_signals"]:
        lines.append(_signal_row(row))
    lines.extend([
        "",
        "### Full30 Sandbox/Permission",
        "",
        "| Signal | Label mean | Baseline mean | Delta label-baseline |",
        "| --- | ---: | ---: | ---: |",
    ])
    for row in result["full30_sandbox_permission_top_signals"]:
        lines.append(_signal_row(row))

    lines.extend([
        "",
        "## Controlled Detector Fixtures",
        "",
        "| Label | Top signal | Delta label-baseline |",
        "| --- | --- | ---: |",
    ])
    for label, rows in result["detector_fixture_top_signals_by_label"].items():
        top = rows[0] if rows else {"signal": "-", "delta_label_minus_overall": 0}
        lines.append(f"| {label} | {top['signal']} | {_fmt(top['delta_label_minus_overall'])} |")
    lines.extend([
        "",
        "Interpretation: RQ4 is best framed as a boundary result. Process signals explain observable process failures such as repeated exploration and sandbox friction, but hidden semantic failures can look procedurally clean.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_rq4_signal_audit_markdown(result), encoding="utf-8")


def _top_label_signals(rows: list[dict[str, Any]], label: str, limit: int = 5) -> list[dict[str, Any]]:
    selected = [row for row in rows if row["failure_tag"] == label]
    selected.sort(key=lambda row: abs(float(row.get("delta_label_minus_overall", 0) or 0)), reverse=True)
    return selected[:limit]


def _signal_row(row: dict[str, Any]) -> str:
    return (
        f"| {row['signal']} | {_fmt(row['label_mean'])} | {_fmt(row['overall_mean'])} | "
        f"{_fmt(row['delta_label_minus_overall'])} |"
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        if abs(value) >= 1000:
            return f"{value / 1000:.1f}k"
        return f"{value:.4g}"
    return str(value)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an RQ4 trace-signal audit.")
    parser.add_argument("--hard30-report", type=Path, default=DEFAULT_HARD30_REPORT)
    parser.add_argument("--full30-manifest", type=Path, default=DEFAULT_FULL30_MANIFEST)
    parser.add_argument("--full30-process-labels", type=Path, default=DEFAULT_FULL30_PROCESS_LABELS)
    parser.add_argument("--detector-fixture-manifest", type=Path, default=DEFAULT_DETECTOR_FIXTURE_MANIFEST)
    parser.add_argument("--detector-fixture-labels", type=Path, default=DEFAULT_DETECTOR_FIXTURE_LABELS)
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_rq4_signal_audit(
        args.hard30_report,
        args.full30_manifest,
        args.full30_process_labels,
        args.detector_fixture_manifest,
        args.detector_fixture_labels,
    )
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_rq4_signal_audit_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
