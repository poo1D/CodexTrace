from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_PAPER_DRAFT = Path("docs/paper_draft.md")
DEFAULT_FULL30 = Path("benchmark/pilot/full30-real/aggregate.json")
DEFAULT_HARD10 = Path("benchmark/hard/pilot/hard10-real/aggregate.json")
DEFAULT_HARD30 = Path("benchmark/hard/pilot/hard30-real/aggregate.json")
DEFAULT_PROCESS_STRESS = Path("benchmark/process-stress/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_LIFT = Path("benchmark/verification-lift/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_ABLATION = Path("benchmark/verification-ablation/pilot/full-real/aggregate.json")
DEFAULT_TASK_DIAGNOSIS = Path("docs/hard30_task_diagnosis.json")


def build_paper_number_guard(
    paper_draft_path: Path = DEFAULT_PAPER_DRAFT,
    full30_path: Path = DEFAULT_FULL30,
    hard10_path: Path = DEFAULT_HARD10,
    hard30_path: Path = DEFAULT_HARD30,
    process_stress_path: Path = DEFAULT_PROCESS_STRESS,
    verification_lift_path: Path = DEFAULT_VERIFICATION_LIFT,
    verification_ablation_path: Path = DEFAULT_VERIFICATION_ABLATION,
    task_diagnosis_path: Path = DEFAULT_TASK_DIAGNOSIS,
) -> dict[str, Any]:
    text = _normalize(paper_draft_path.read_text(encoding="utf-8"))
    full30 = _read_json(full30_path)
    hard10 = _read_json(hard10_path)
    hard30 = _read_json(hard30_path)
    process_stress = _read_json(process_stress_path)
    verification_lift = _read_json(verification_lift_path)
    verification_ablation = _read_json(verification_ablation_path)
    task_diagnosis = _read_json(task_diagnosis_path)

    snippets = [
        _snippet(
            "abstract full30 waste",
            (
                f"the intervention reduces repeated tool calls from {_fmt2(full30['summary']['baseline']['avg_repeated_tool_calls'])} "
                f"to {_fmt2(full30['summary']['intervention']['avg_repeated_tool_calls'])} and average token usage "
                f"from {_fmt_k(full30['summary']['baseline']['avg_token_usage'])} to {_fmt_k(full30['summary']['intervention']['avg_token_usage'])}"
            ),
        ),
        _snippet(
            "abstract hard30 waste",
            (
                f"success rate stays flat at {_fmt_pct0(hard30['summary']['baseline']['success_rate'])}, but the intervention reduces "
                f"repeated tool calls from {_fmt2(hard30['summary']['baseline']['avg_repeated_tool_calls'])} "
                f"to {_fmt2(hard30['summary']['intervention']['avg_repeated_tool_calls'])}, average token usage "
                f"from {_fmt_k(hard30['summary']['baseline']['avg_token_usage'])} to {_fmt_k(hard30['summary']['intervention']['avg_token_usage'])}"
            ),
        ),
        _snippet(
            "full30 failure-score row",
            (
                f"| avg_failure_score | {_fmt2(full30['summary']['baseline']['avg_failure_score'])} | "
                f"{_fmt2(full30['summary']['intervention']['avg_failure_score'])} | "
                f"{_fmt_signed2(full30['deltas']['avg_failure_score'])} |"
            ),
        ),
        _snippet(
            "hard10 token row",
            (
                f"| avg_token_usage | {_fmt_k(hard10['summary']['baseline']['avg_token_usage'])} | "
                f"{_fmt_k(hard10['summary']['intervention']['avg_token_usage'])} | "
                f"{_fmt_signed_k(hard10['deltas']['avg_token_usage'])} |"
            ),
        ),
        _snippet(
            "hard30 waste row",
            (
                f"| avg_token_usage | {_fmt_k(hard30['summary']['baseline']['avg_token_usage'])} | "
                f"{_fmt_k(hard30['summary']['intervention']['avg_token_usage'])} | "
                f"{_fmt_signed_k(hard30['deltas']['avg_token_usage'])} |"
            ),
        ),
        _snippet(
            "hard30 paired task counts",
            (
                f"token usage improves in {task_diagnosis['summary']['token_improved_count']} of {task_diagnosis['summary']['task_count']} tasks, "
                f"repeated tool calls improve in {task_diagnosis['summary']['repeated_call_improved_count']} of {task_diagnosis['summary']['task_count']} tasks"
            ),
        ),
        _snippet(
            "process-stress paragraph",
            (
                f"flat at {_fmt2(process_stress['summary']['baseline']['success_rate'])} -> "
                f"{_fmt2(process_stress['summary']['intervention']['success_rate'])}, while repeated tool calls improve from "
                f"{_fmt2(process_stress['summary']['baseline']['avg_repeated_tool_calls'])} to "
                f"{_fmt2(process_stress['summary']['intervention']['avg_repeated_tool_calls'])} and token usage improves from "
                f"{_fmt_k(process_stress['summary']['baseline']['avg_token_usage'])} to "
                f"{_fmt_k(process_stress['summary']['intervention']['avg_token_usage'])}"
            ),
        ),
        _snippet(
            "verification-lift paragraph",
            (
                f"verification both remain {_fmt2(verification_lift['summary']['baseline']['verification_rate'])} -> "
                f"{_fmt2(verification_lift['summary']['intervention']['verification_rate'])}, success remains "
                f"{_fmt2(verification_lift['summary']['baseline']['success_rate'])} -> "
                f"{_fmt2(verification_lift['summary']['intervention']['success_rate'])}, repeated"
            ),
        ),
        _snippet(
            "verification-ablation paragraph",
            (
                f"verification both rise from {_fmt2(verification_ablation['summary']['baseline']['verification_rate'])} to "
                f"{_fmt2(verification_ablation['summary']['intervention']['verification_rate'])} and failure score drops from "
                f"{_fmt2(verification_ablation['summary']['baseline']['avg_failure_score'])} to "
                f"{_fmt2(verification_ablation['summary']['intervention']['avg_failure_score'])}"
            ),
        ),
    ]
    checked = [
        {
            **snippet,
            "present": _normalize(snippet["text"]) in text,
        }
        for snippet in snippets
    ]
    missing = [row for row in checked if not row["present"]]
    return {
        "ok": not missing,
        "paper_draft": str(paper_draft_path),
        "summary": {
            "checked": len(checked),
            "missing": len(missing),
        },
        "snippets": checked,
        "missing": missing,
    }


def render_paper_number_guard_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# Paper Number Guard",
        "",
        "This generated guard checks that paper-draft numeric claims match stored aggregate artifacts.",
        "",
        f"OK: {'yes' if result['ok'] else 'no'}",
        f"Checked snippets: {result['summary']['checked']}",
        f"Missing snippets: {result['summary']['missing']}",
        "",
        "| Claim | Status | Expected snippet |",
        "| --- | --- | --- |",
    ]
    for row in result["snippets"]:
        status = "present" if row["present"] else "missing"
        lines.append(f"| {row['name']} | {status} | `{row['text']}` |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Guard paper-draft numeric claims against stored result artifacts.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_paper_number_guard()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_paper_number_guard_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["ok"] else 1


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _snippet(name: str, text: str) -> dict[str, str]:
    return {"name": name, "text": text}


def _normalize(text: str) -> str:
    return " ".join(text.split())


def _fmt2(value: float) -> str:
    return f"{float(value):.2f}"


def _fmt_signed2(value: float) -> str:
    return f"{float(value):+.2f}"


def _fmt_pct0(value: float) -> str:
    return f"{float(value) * 100:.0f}%"


def _fmt_k(value: float) -> str:
    return f"{float(value) / 1000:.1f}k"


def _fmt_signed_k(value: float) -> str:
    return f"{float(value) / 1000:+.1f}k"


if __name__ == "__main__":
    raise SystemExit(main())
