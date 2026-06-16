from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


DEFAULT_PATHS = (
    Path("README.md"),
    Path("docs/artifact_guide.md"),
    Path("docs/paper_draft.md"),
    Path("docs/paper_outline.md"),
    Path("docs/headline_results.md"),
    Path("docs/submission_package.md"),
    Path("docs/reproducibility_checklist.md"),
)

EXPECTED_SKETCH_STRINGS = (
    "Baseline success rate:       42%",
    "Intervention success rate:   58%",
    "Baseline verification rate:  51%",
    "Intervention verification:   83%",
    "Avg repeated tool calls:     6.4 -> 3.1",
    "Avg unresolved errors:       2.2 -> 0.9",
    "Avg token usage:             18.7k -> 15.2k",
    "42%",
    "58%",
    "51%",
    "83%",
    "18.7k -> 15.2k",
)

REQUIRED_HEADLINE_PHRASES = (
    "This generated table replaces the original expected-results sketch with the current stored evidence.",
    "Ordinary verification-rate lift supported: no",
    "Waste reduction supported: yes",
    "ordinary verification-rate lift is unsupported; no-verify ablation is a mechanism check only, not an ordinary baseline",
    "| `hard30_success` | 0.50 | 0.50 | +0.00 | flat hard30 success |",
    "| `hard30_verification` | 1.00 | 1.00 | +0.00 | saturated; no ordinary verification lift |",
    "| `hard30_token_usage` | 355.0k | 256.3k | -98.7k | supported waste reduction |",
)

EXPECTED_SKETCH_REPLACEMENTS = (
    {
        "sketch_metric": "success_rate",
        "original_expected": "42% -> 58%",
        "stored_evidence": "hard30 0.50 -> 0.50; hard10 0.70 -> 0.80",
        "paper_status": "flat hard30; pilot-qualified hard10 lift",
    },
    {
        "sketch_metric": "verification_rate",
        "original_expected": "51% -> 83%",
        "stored_evidence": "hard30 1.00 -> 1.00; verification-lift-v2 1.00 -> 1.00",
        "paper_status": "ordinary-baseline verification-rate lift unsupported",
    },
    {
        "sketch_metric": "repeated_tool_calls",
        "original_expected": "6.4 -> 3.1",
        "stored_evidence": "hard30 12.93 -> 9.20",
        "paper_status": "supported waste reduction",
    },
    {
        "sketch_metric": "unresolved_errors",
        "original_expected": "2.2 -> 0.9",
        "stored_evidence": "hard30 0.00 -> 0.00",
        "paper_status": "no unresolved-error movement",
    },
    {
        "sketch_metric": "token_usage",
        "original_expected": "18.7k -> 15.2k",
        "stored_evidence": "hard30 355.0k -> 256.3k",
        "paper_status": "supported waste reduction",
    },
)


def build_expected_results_reconciliation(
    paper_paths: tuple[Path, ...] = DEFAULT_PATHS,
    headline_path: Path = Path("docs/headline_results.md"),
) -> dict[str, Any]:
    paper_checks = []
    for path in paper_paths:
        text = path.read_text(encoding="utf-8")
        forbidden = [phrase for phrase in EXPECTED_SKETCH_STRINGS if phrase in text]
        paper_checks.append({
            "path": str(path),
            "forbidden_expected_strings": forbidden,
            "clean": not forbidden,
        })

    headline = headline_path.read_text(encoding="utf-8")
    headline_checks = [
        {"phrase": phrase, "present": phrase in headline}
        for phrase in REQUIRED_HEADLINE_PHRASES
    ]

    return {
        "summary": {
            "ready": all(row["clean"] for row in paper_checks) and all(row["present"] for row in headline_checks),
            "paper_file_count": len(paper_checks),
            "clean_paper_file_count": sum(1 for row in paper_checks if row["clean"]),
            "headline_phrase_count": len(headline_checks),
            "headline_phrase_present_count": sum(1 for row in headline_checks if row["present"]),
            "replacement_count": len(EXPECTED_SKETCH_REPLACEMENTS),
            "headline_path": str(headline_path),
        },
        "paper_files": paper_checks,
        "headline_checks": headline_checks,
        "expected_sketch_replacements": list(EXPECTED_SKETCH_REPLACEMENTS),
    }


def render_expected_results_reconciliation_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Expected Results Reconciliation Audit",
        "",
        "This generated audit checks that paper-facing files use the stored headline evidence instead of the original expected-results sketch.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Paper files clean: {summary['clean_paper_file_count']} / {summary['paper_file_count']}",
        f"- Headline phrases present: {summary['headline_phrase_present_count']} / {summary['headline_phrase_count']}",
        f"- Expected sketch replacements: {summary['replacement_count']}",
        f"- Headline table: `{summary['headline_path']}`",
        "",
        "## Paper-Facing Files",
        "",
        "| File | Clean | Forbidden expected strings |",
        "| --- | --- | --- |",
    ]
    for row in result["paper_files"]:
        forbidden = ", ".join(f"`{phrase}`" for phrase in row["forbidden_expected_strings"]) or "-"
        lines.append(f"| `{row['path']}` | {'yes' if row['clean'] else 'no'} | {forbidden} |")

    lines.extend([
        "",
        "## Headline Evidence",
        "",
        "| Required phrase | Present |",
        "| --- | --- |",
    ])
    for row in result["headline_checks"]:
        phrase = _escape_table_cell(f"`{row['phrase']}`")
        lines.append(f"| {phrase} | {'yes' if row['present'] else 'no'} |")
    lines.extend([
        "",
        "## Expected Sketch Replacement Map",
        "",
        "| Sketch metric | Original expected | Stored evidence | Paper status |",
        "| --- | --- | --- | --- |",
    ])
    for row in result["expected_sketch_replacements"]:
        lines.append(
            f"| `{row['sketch_metric']}` | `{row['original_expected']}` | "
            f"{row['stored_evidence']} | {row['paper_status']} |"
        )
    lines.extend([
        "",
        "Interpretation: this audit prevents the aspirational expected-results table from drifting back into the paper as evidence. It does not judge whether the current headline results are strong enough for a particular venue.",
    ])
    return "\n".join(lines) + "\n"


def _escape_table_cell(text: str) -> str:
    return text.replace("|", r"\|")


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_expected_results_reconciliation_markdown(result), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit replacement of the expected-results sketch with stored evidence.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_expected_results_reconciliation()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_expected_results_reconciliation_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
