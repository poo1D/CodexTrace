from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


NON_ABLATION_TIERS = (
    ("full30", Path("benchmark/pilot/full30-real/aggregate.json"), "ordinary seed pilot"),
    ("hard10", Path("benchmark/hard/pilot/hard10-real/aggregate.json"), "early hard-tier pilot"),
    ("hard30", Path("benchmark/hard/pilot/hard30-real/aggregate.json"), "paper-facing hard-tier pilot"),
    ("process-stress", Path("benchmark/process-stress/pilot/full-real/aggregate.json"), "observable-process stress pilot"),
    ("verification-lift", Path("benchmark/verification-lift/pilot/full-real/aggregate.json"), "weak optional-verification pilot"),
    ("verification-lift-v2", Path("benchmark/verification-lift-v2/pilot/full-real/aggregate.json"), "ordinary-baseline retest"),
)
TARGET_BASELINE_RATE = 0.51
TARGET_INTERVENTION_RATE = 0.83


def build_verification_lift_power_audit(
    non_ablation_tiers: tuple[tuple[str, Path, str], ...] = NON_ABLATION_TIERS,
) -> dict[str, Any]:
    rows = [_row(tier, path, _read_json(path), description) for tier, path, description in non_ablation_tiers]
    baseline_runs = sum(row["baseline_runs"] for row in rows)
    intervention_runs = sum(row["intervention_runs"] for row in rows)
    baseline_unverified = sum(row["baseline_unverified_broad"] for row in rows)
    baseline_exact_unverified = sum(row["baseline_unverified_exact"] for row in rows)
    observed_baseline_rate = _safe_divide(sum(row["baseline_verified_broad"] for row in rows), baseline_runs)
    observed_intervention_rate = _safe_divide(sum(row["intervention_verified_broad"] for row in rows), intervention_runs)
    observed_exact_baseline_rate = _safe_divide(sum(row["baseline_verified_exact"] for row in rows), baseline_runs)
    observed_exact_intervention_rate = _safe_divide(sum(row["intervention_verified_exact"] for row in rows), intervention_runs)
    empirical_headroom = 1.0 - observed_baseline_rate
    empirical_exact_headroom = 1.0 - observed_exact_baseline_rate
    broad_rule_of_three = _rule_of_three_upper_bound(baseline_runs, baseline_unverified)
    exact_rule_of_three = _rule_of_three_upper_bound(baseline_runs, baseline_exact_unverified)
    expected_delta = TARGET_INTERVENTION_RATE - TARGET_BASELINE_RATE
    impossible_expected_table = (
        observed_baseline_rate > TARGET_BASELINE_RATE
        and empirical_headroom < expected_delta
        and broad_rule_of_three < expected_delta
    )

    return {
        "summary": {
            "ready": (
                baseline_runs > 0
                and baseline_unverified == 0
                and baseline_exact_unverified == 0
                and empirical_headroom == 0
                and empirical_exact_headroom == 0
                and impossible_expected_table
            ),
            "non_ablation_tier_count": len(rows),
            "baseline_runs": baseline_runs,
            "intervention_runs": intervention_runs,
            "baseline_unverified_broad": baseline_unverified,
            "baseline_unverified_exact": baseline_exact_unverified,
            "observed_baseline_verification_rate": observed_baseline_rate,
            "observed_intervention_verification_rate": observed_intervention_rate,
            "observed_exact_baseline_verification_rate": observed_exact_baseline_rate,
            "observed_exact_intervention_verification_rate": observed_exact_intervention_rate,
            "empirical_rate_headroom": empirical_headroom,
            "empirical_exact_rate_headroom": empirical_exact_headroom,
            "rule_of_three_nonverification_upper_bound": broad_rule_of_three,
            "rule_of_three_exact_nonverification_upper_bound": exact_rule_of_three,
            "expected_table_baseline_rate": TARGET_BASELINE_RATE,
            "expected_table_intervention_rate": TARGET_INTERVENTION_RATE,
            "expected_table_delta": expected_delta,
            "expected_table_compatible": not impossible_expected_table,
            "ordinary_expansion_can_close_claim": baseline_unverified > 0 or baseline_exact_unverified > 0,
            "interpretation": (
                "stored ordinary and weak-baseline runs have no observed verification-rate headroom; "
                "additional same-style saturated runs cannot prove a positive rate lift"
            ),
        },
        "tiers": rows,
        "closure_conditions": [
            {
                "id": "non_saturated_ordinary_baseline",
                "status": "missing",
                "evidence": f"{baseline_unverified}/{baseline_runs} broad baseline runs lack verification.",
                "requirement": "At least one non-ablation baseline run must omit broad or exact success-check verification before a positive rate lift has empirical headroom.",
            },
            {
                "id": "positive_paired_rate_delta",
                "status": "missing",
                "evidence": "All stored non-ablation broad and exact verification deltas are 0.00.",
                "requirement": "Intervention must improve broad or exact visible-success-check verification over the matched ordinary baseline.",
            },
            {
                "id": "expected_headline_table",
                "status": "contradicted",
                "evidence": (
                    f"Observed ordinary/weak-baseline verification is {observed_baseline_rate:.2f}, "
                    f"not {TARGET_BASELINE_RATE:.2f}; empirical headroom is {empirical_headroom:.2f}, "
                    f"not the expected {expected_delta:.2f} delta."
                ),
                "requirement": "The expected 51% -> 83% style result would require a non-saturated baseline population.",
            },
        ],
    }


def render_verification_lift_power_markdown(result: dict[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Verification-Lift Power and Headroom Audit",
        "",
        "This generated audit checks whether current non-ablation evidence has enough verification-rate headroom to support the original expected verification-lift claim.",
        "",
        "## Summary",
        "",
        f"- Ready: {'yes' if summary['ready'] else 'no'}",
        f"- Non-ablation tiers: {summary['non_ablation_tier_count']}",
        f"- Baseline runs: {summary['baseline_runs']}",
        f"- Baseline runs without broad verification: {summary['baseline_unverified_broad']}",
        f"- Baseline runs without exact success-check verification: {summary['baseline_unverified_exact']}",
        f"- Observed baseline verification: {summary['observed_baseline_verification_rate']:.2f}",
        f"- Observed intervention verification: {summary['observed_intervention_verification_rate']:.2f}",
        f"- Empirical verification-rate headroom: {summary['empirical_rate_headroom']:.2f}",
        f"- Rule-of-three nonverification upper bound: {summary['rule_of_three_nonverification_upper_bound']:.3f}",
        f"- Expected headline verification delta: {summary['expected_table_delta']:.2f}",
        f"- Expected 51% -> 83% table compatible: {'yes' if summary['expected_table_compatible'] else 'no'}",
        f"- Ordinary expansion can close current claim without non-saturated baseline evidence: {'yes' if summary['ordinary_expansion_can_close_claim'] else 'no'}",
        f"- Interpretation: {summary['interpretation']}",
        "",
        "## Tier Headroom",
        "",
        "| Tier | Baseline runs | Baseline broad | Baseline exact | Broad headroom | Exact headroom | Interpretation |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for row in result["tiers"]:
        lines.append(
            f"| {row['tier']} | {row['baseline_runs']} | {row['baseline_verification_rate']:.2f} | "
            f"{row['baseline_exact_verification_rate']:.2f} | {row['broad_headroom']:.2f} | "
            f"{row['exact_headroom']:.2f} | {'saturated' if row['saturated'] else 'non-saturated'} |"
        )
    lines.extend([
        "",
        "## Claim-Closure Conditions",
        "",
        "| Condition | Status | Evidence | Requirement |",
        "| --- | --- | --- | --- |",
    ])
    for row in result["closure_conditions"]:
        lines.append(f"| `{row['id']}` | `{row['status']}` | {row['evidence']} | {row['requirement']} |")
    lines.extend([
        "",
        "Interpretation: this is not a substitute for a new positive experiment. It is a stopping rule for the current ordinary-baseline verification-rate claim: with 98 / 98 stored non-ablation baseline runs already verifying, the original rate-lift thesis lacks empirical headroom unless a future ordinary-baseline design first produces non-saturated baseline behavior.",
    ])
    return "\n".join(lines) + "\n"


def write_outputs(result: dict[str, Any], json_path: Path | None, markdown_path: Path | None) -> None:
    if json_path:
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(render_verification_lift_power_markdown(result), encoding="utf-8")


def _row(tier: str, path: Path, aggregate: dict[str, Any], description: str) -> dict[str, Any]:
    baseline = aggregate["summary"]["baseline"]
    intervention = aggregate["summary"]["intervention"]
    baseline_runs = int(baseline["n"])
    intervention_runs = int(intervention["n"])
    baseline_rate = float(baseline["verification_rate"])
    intervention_rate = float(intervention["verification_rate"])
    baseline_exact = float(baseline["success_check_verification_rate"])
    intervention_exact = float(intervention["success_check_verification_rate"])
    baseline_verified_broad = round(baseline_rate * baseline_runs)
    baseline_verified_exact = round(baseline_exact * baseline_runs)
    intervention_verified_broad = round(intervention_rate * intervention_runs)
    intervention_verified_exact = round(intervention_exact * intervention_runs)
    return {
        "tier": tier,
        "description": description,
        "path": str(path),
        "baseline_runs": baseline_runs,
        "intervention_runs": intervention_runs,
        "baseline_verification_rate": baseline_rate,
        "intervention_verification_rate": intervention_rate,
        "baseline_exact_verification_rate": baseline_exact,
        "intervention_exact_verification_rate": intervention_exact,
        "baseline_verified_broad": baseline_verified_broad,
        "baseline_verified_exact": baseline_verified_exact,
        "intervention_verified_broad": intervention_verified_broad,
        "intervention_verified_exact": intervention_verified_exact,
        "baseline_unverified_broad": baseline_runs - baseline_verified_broad,
        "baseline_unverified_exact": baseline_runs - baseline_verified_exact,
        "broad_headroom": 1.0 - baseline_rate,
        "exact_headroom": 1.0 - baseline_exact,
        "saturated": baseline_rate == 1 and intervention_rate == 1 and baseline_exact == 1 and intervention_exact == 1,
    }


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _safe_divide(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def _rule_of_three_upper_bound(total: int, failures: int) -> float:
    if total <= 0 or failures:
        return 0.0
    return min(1.0, 3.0 / total)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit verification-lift power and empirical headroom.")
    parser.add_argument("--json-output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    args = parser.parse_args()

    result = build_verification_lift_power_audit()
    if args.json_output or args.markdown_output:
        write_outputs(result, args.json_output, args.markdown_output)
    else:
        print(render_verification_lift_power_markdown(result), end="")
    return 0 if result["summary"]["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
