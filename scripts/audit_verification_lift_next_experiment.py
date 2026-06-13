from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_VERIFICATION_LIFT_AGGREGATE = Path("benchmark/verification-lift/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_LIFT_V2_AGGREGATE = Path("benchmark/verification-lift-v2/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_ABLATION_AGGREGATE = Path("benchmark/verification-ablation/pilot/full-real/aggregate.json")
DEFAULT_VERIFICATION_LIFT_BASELINE = Path("benchmark/verification-lift/prompts/baseline.txt")
DEFAULT_VERIFICATION_ABLATION_BASELINE = Path("benchmark/verification-ablation/prompts/baseline.txt")
DEFAULT_THESIS_READINESS = Path("docs/thesis_readiness.json")
DEFAULT_VERIFICATION_LIFT_V2_AUDIT = Path("docs/verification_lift_v2_plan_audit.json")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _rate_delta(aggregate: dict[str, Any], metric: str) -> float:
    return float(aggregate["deltas"][metric])


def _summary_rate(aggregate: dict[str, Any], prompt_type: str, metric: str) -> float:
    return float(aggregate["summary"][prompt_type][metric])


def _contains_any(text: str, phrases: list[str]) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in phrases)


def build_verification_lift_next_experiment_audit(
    verification_lift_aggregate_path: Path = DEFAULT_VERIFICATION_LIFT_AGGREGATE,
    verification_lift_v2_aggregate_path: Path = DEFAULT_VERIFICATION_LIFT_V2_AGGREGATE,
    verification_ablation_aggregate_path: Path = DEFAULT_VERIFICATION_ABLATION_AGGREGATE,
    verification_lift_baseline_path: Path = DEFAULT_VERIFICATION_LIFT_BASELINE,
    verification_ablation_baseline_path: Path = DEFAULT_VERIFICATION_ABLATION_BASELINE,
    thesis_readiness_path: Path = DEFAULT_THESIS_READINESS,
    verification_lift_v2_audit_path: Path = DEFAULT_VERIFICATION_LIFT_V2_AUDIT,
) -> dict[str, Any]:
    lift = _read_json(verification_lift_aggregate_path)
    lift_v2 = _read_json(verification_lift_v2_aggregate_path) if verification_lift_v2_aggregate_path.exists() else None
    ablation = _read_json(verification_ablation_aggregate_path)
    thesis = _read_json(thesis_readiness_path)
    v2_audit = _read_json(verification_lift_v2_audit_path) if verification_lift_v2_audit_path.exists() else {}
    lift_baseline = verification_lift_baseline_path.read_text(encoding="utf-8")
    ablation_baseline = verification_ablation_baseline_path.read_text(encoding="utf-8")
    requirements = {row["id"]: row for row in thesis["requirements"]}

    lift_broad_delta = _rate_delta(lift, "verification_rate")
    lift_exact_delta = _rate_delta(lift, "success_check_verification_rate")
    lift_v2_broad_delta = _rate_delta(lift_v2, "verification_rate") if lift_v2 else 0.0
    lift_v2_exact_delta = _rate_delta(lift_v2, "success_check_verification_rate") if lift_v2 else 0.0
    ablation_broad_delta = _rate_delta(ablation, "verification_rate")
    ablation_exact_delta = _rate_delta(ablation, "success_check_verification_rate")
    lift_baseline_saturated = (
        _summary_rate(lift, "baseline", "verification_rate") >= 1
        and _summary_rate(lift, "baseline", "success_check_verification_rate") >= 1
    )
    ablation_is_no_verify = _contains_any(
        ablation_baseline,
        [
            "do not run test",
            "do not run tests",
            "do not run test, build, lint, grader",
            "did not run tests",
        ],
    )
    lift_baseline_allows_skip = _contains_any(
        lift_baseline,
        [
            "may skip command execution",
            "skip command execution",
            "inspection gives you enough confidence",
        ],
    )

    original_verification_lift_closed = (
        requirements["verification_lift"]["status"] == "satisfied"
        and max(lift_broad_delta, lift_v2_broad_delta) > 0
        and max(lift_exact_delta, lift_v2_exact_delta) > 0
    )
    next_experiment_required = not original_verification_lift_closed
    acceptance_gates = [
        {
            "id": "ordinary_baseline",
            "gate": "Baseline prompt must be ordinary or weak-baseline, not an explicit no-verify ablation.",
            "rationale": "A no-verify baseline can prove harness control but cannot close the original ordinary-baseline claim.",
        },
        {
            "id": "non_saturated_baseline_or_depth_metric",
            "gate": "Measure broad verification, exact visible success-check verification, and verification depth so saturation is visible.",
            "rationale": "The current weak-baseline pilot has baseline verification 1.00 and exact verification 1.00, leaving no rate headroom.",
        },
        {
            "id": "paired_task_count",
            "gate": "Collect at least 8 paired tasks and 16 real runs before treating the result as a verification-lift experiment.",
            "rationale": "This matches the current verification-lift tier size while avoiding single-task anecdotes.",
        },
        {
            "id": "claim_closure",
            "gate": "Close the original claim only if intervention verification rate or exact success-check verification increases over a non-ablation baseline.",
            "rationale": "If the non-ablation baseline remains saturated, keep the paper framed as a boundary result.",
        },
    ]
    return {
        "ok": True,
        "status": "next_experiment_required" if next_experiment_required else "original_claim_closed",
        "original_verification_lift_closed": original_verification_lift_closed,
        "next_experiment_required": next_experiment_required,
        "current_evidence": {
            "verification_lift": {
                "tasks": int(lift["summary"]["baseline"]["n"]),
                "baseline_verification_rate": _summary_rate(lift, "baseline", "verification_rate"),
                "intervention_verification_rate": _summary_rate(lift, "intervention", "verification_rate"),
                "verification_delta": lift_broad_delta,
                "baseline_success_check_verification_rate": _summary_rate(lift, "baseline", "success_check_verification_rate"),
                "intervention_success_check_verification_rate": _summary_rate(lift, "intervention", "success_check_verification_rate"),
                "success_check_verification_delta": lift_exact_delta,
                "baseline_saturated": lift_baseline_saturated,
            },
            "verification_ablation": {
                "tasks": int(ablation["summary"]["baseline"]["n"]),
                "baseline_verification_rate": _summary_rate(ablation, "baseline", "verification_rate"),
                "intervention_verification_rate": _summary_rate(ablation, "intervention", "verification_rate"),
                "verification_delta": ablation_broad_delta,
                "success_check_verification_delta": ablation_exact_delta,
                "baseline_is_no_verify_ablation": ablation_is_no_verify,
            },
            "verification_lift_v2": (
                {
                    "exists": True,
                    "tasks": int(lift_v2["summary"]["baseline"]["n"]),
                    "baseline_verification_rate": _summary_rate(lift_v2, "baseline", "verification_rate"),
                    "intervention_verification_rate": _summary_rate(lift_v2, "intervention", "verification_rate"),
                    "verification_delta": lift_v2_broad_delta,
                    "baseline_success_check_verification_rate": _summary_rate(lift_v2, "baseline", "success_check_verification_rate"),
                    "intervention_success_check_verification_rate": _summary_rate(lift_v2, "intervention", "success_check_verification_rate"),
                    "success_check_verification_delta": lift_v2_exact_delta,
                    "baseline_saturated": (
                        _summary_rate(lift_v2, "baseline", "verification_rate") >= 1
                        and _summary_rate(lift_v2, "baseline", "success_check_verification_rate") >= 1
                    ),
                }
                if lift_v2
                else {"exists": False}
            ),
            "thesis_requirement_status": requirements["verification_lift"]["status"],
        },
        "prompt_constraints": {
            "current_lift_baseline_allows_skip": lift_baseline_allows_skip,
            "ablation_baseline_forbids_verification": ablation_is_no_verify,
            "ordinary_baseline_required": True,
            "no_verify_ablation_disallowed_for_original_claim": True,
        },
        "planned_v2_scaffold": {
            "exists": bool(v2_audit),
            "ready": bool(v2_audit.get("ok")),
            "task_count": int(v2_audit.get("task_count", 0) or 0),
            "materialized_count": int(v2_audit.get("materialized_count", 0) or 0),
            "baseline_prompt_is_ordinary": bool(v2_audit.get("baseline_prompt_is_ordinary")),
            "intervention_is_evidence_gated": bool(v2_audit.get("intervention_is_evidence_gated")),
            "audit_path": str(verification_lift_v2_audit_path),
        },
        "acceptance_gates": acceptance_gates,
    }


def render_verification_lift_next_experiment_markdown(result: dict[str, Any]) -> str:
    lift = result["current_evidence"]["verification_lift"]
    lift_v2 = result["current_evidence"]["verification_lift_v2"]
    ablation = result["current_evidence"]["verification_ablation"]
    planned = result["planned_v2_scaffold"]
    lines = [
        "# Verification-Lift Next Experiment Audit",
        "",
        "This generated audit records whether current evidence closes the original ordinary-baseline verification-lift claim.",
        "",
        "## Verdict",
        "",
        f"- OK: {'yes' if result['ok'] else 'no'}",
        f"- Original verification-lift claim closed: {'yes' if result['original_verification_lift_closed'] else 'no'}",
        f"- Next experiment required: {'yes' if result['next_experiment_required'] else 'no'}",
        "- No-verify ablation cannot close the ordinary-baseline claim.",
        "",
        "## Current Evidence",
        "",
        "| Tier | Tasks | Baseline verification | Intervention verification | Broad delta | Exact success-check delta | Interpretation |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        (
            f"| verification-lift | {lift['tasks']} | {lift['baseline_verification_rate']:.2f} | "
            f"{lift['intervention_verification_rate']:.2f} | {lift['verification_delta']:.2f} | "
            f"{lift['success_check_verification_delta']:.2f} | weak-baseline pilot is saturated |"
        ),
    ]
    if lift_v2.get("exists"):
        lines.append(
            f"| verification-lift-v2 | {lift_v2['tasks']} | {lift_v2['baseline_verification_rate']:.2f} | "
            f"{lift_v2['intervention_verification_rate']:.2f} | {lift_v2['verification_delta']:.2f} | "
            f"{lift_v2['success_check_verification_delta']:.2f} | ordinary-baseline pilot is saturated |"
        )
    lines.extend([
        (
            f"| verification-ablation | {ablation['tasks']} | {ablation['baseline_verification_rate']:.2f} | "
            f"{ablation['intervention_verification_rate']:.2f} | {ablation['verification_delta']:.2f} | "
            f"{ablation['success_check_verification_delta']:.2f} | mechanism ablation only |"
        ),
        "",
        "## Prompt Constraints",
        "",
        f"- Current lift baseline allows skip: {'yes' if result['prompt_constraints']['current_lift_baseline_allows_skip'] else 'no'}",
        f"- Ablation baseline forbids verification: {'yes' if result['prompt_constraints']['ablation_baseline_forbids_verification'] else 'no'}",
        "- Ordinary baseline required: yes",
        "- No-verify ablation disallowed for original claim: yes",
        "",
        "## Planned Ordinary-Baseline V2 Scaffold",
        "",
        f"- Exists: {'yes' if planned['exists'] else 'no'}",
        f"- Ready: {'yes' if planned['ready'] else 'no'}",
        f"- Tasks: {planned['task_count']}",
        f"- Materialized fixtures: {planned['materialized_count']}",
        f"- Baseline prompt is ordinary: {'yes' if planned['baseline_prompt_is_ordinary'] else 'no'}",
        f"- Intervention is evidence-gated: {'yes' if planned['intervention_is_evidence_gated'] else 'no'}",
        f"- Audit: `{planned['audit_path']}`",
        "",
        "## Acceptance Gates",
        "",
    ])
    for gate in result["acceptance_gates"]:
        lines.append(f"- `{gate['id']}`: {gate['gate']} Rationale: {gate['rationale']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the next experiment needed to close the verification-lift claim.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_verification_lift_next_experiment_audit()
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = render_verification_lift_next_experiment_markdown(result)
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(markdown, encoding="utf-8")
    if not args.json_output and not args.markdown_output:
        print(markdown, end="")
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
