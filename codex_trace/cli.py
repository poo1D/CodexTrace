from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .diagnose import diagnose
from .parser import parse_jsonl
from .report import render_json, render_markdown
from .research import (
    aggregate_runs,
    build_dashboard_artifact,
    build_paper_report,
    build_results_summary,
    evaluate_detector_labels,
    generate_label_template,
    load_tasks,
    render_aggregate_markdown,
    render_label_evaluation_markdown,
    render_label_template_jsonl,
    render_paper_report_markdown,
    render_results_summary_markdown,
    render_prompt,
    run_benchmark,
    write_aggregate_outputs,
    write_dashboard_artifact,
    write_label_evaluation_outputs,
    write_label_template,
    write_paper_report_outputs,
    write_results_summary_outputs,
    write_run_manifest,
    write_runs_csv,
)
from .sandbox import DockerRunConfig, run_docker_benchmark, smoke_check_fixture, write_docker_run_manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="codex-trace", description="Diagnose and replay agent harness traces.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    collect = subparsers.add_parser("collect", help="Normalize a Codex JSONL trace into schema JSON.")
    collect.add_argument("trace", type=Path)
    collect.add_argument("-o", "--output", type=Path)

    diagnose_cmd = subparsers.add_parser("diagnose", help="Diagnose a Codex JSONL trace.")
    diagnose_cmd.add_argument("trace", type=Path)
    diagnose_cmd.add_argument("--format", choices=["markdown", "json"], default="markdown")
    diagnose_cmd.add_argument("-o", "--output", type=Path)

    sandbox_cmd = subparsers.add_parser("sandbox", help="Docker sandbox benchmark runner.")
    sandbox_subparsers = sandbox_cmd.add_subparsers(dest="sandbox_command", required=True)

    docker_run_cmd = sandbox_subparsers.add_parser("run", help="Run benchmark fixture checks in a constrained Docker container.")
    docker_run_cmd.add_argument("--tasks", type=Path, default=Path("benchmark/smoke/tasks.jsonl"))
    docker_run_cmd.add_argument("--output-dir", type=Path, required=True)
    docker_run_cmd.add_argument("--task-id", action="append", dest="task_ids")
    docker_run_cmd.add_argument("--image", default="python:3.12-slim")
    docker_run_cmd.add_argument("--cpus", default="1")
    docker_run_cmd.add_argument("--memory", default="512m")
    docker_run_cmd.add_argument("--network", default="none")
    docker_run_cmd.add_argument("--timeout-seconds", type=int, default=60)
    docker_run_cmd.add_argument("--command", dest="docker_command")
    docker_run_cmd.add_argument("--dry-run", action="store_true")

    sandbox_smoke_cmd = sandbox_subparsers.add_parser("smoke-check", help="Run a local fixture smoke check without Docker.")
    sandbox_smoke_cmd.add_argument("--task-id", default="SM-001")

    research = subparsers.add_parser("research", help="Research benchmark helpers.")
    research_subparsers = research.add_subparsers(dest="research_command", required=True)

    prompt_cmd = research_subparsers.add_parser("prompt", help="Render a baseline or intervention prompt for one task.")
    prompt_cmd.add_argument("task_id")
    prompt_cmd.add_argument("prompt_type", choices=["baseline", "intervention"])
    prompt_cmd.add_argument("--tasks", type=Path, default=Path("benchmark/tasks.jsonl"))
    prompt_cmd.add_argument("--prompt-dir", type=Path, default=Path("benchmark/prompts"))

    aggregate_cmd = research_subparsers.add_parser("aggregate", help="Aggregate baseline vs intervention trace runs.")
    aggregate_cmd.add_argument("manifest", type=Path)
    aggregate_cmd.add_argument("--json-output", type=Path)
    aggregate_cmd.add_argument("--markdown-output", type=Path)
    aggregate_cmd.add_argument("--csv-output", type=Path)

    label_template_cmd = research_subparsers.add_parser("label-template", help="Generate a manual-label JSONL template from a run manifest.")
    label_template_cmd.add_argument("manifest", type=Path)
    label_template_cmd.add_argument("--output", type=Path)
    label_template_cmd.add_argument("--include-predictions", action="store_true")

    eval_cmd = research_subparsers.add_parser("evaluate-labels", help="Evaluate detector tags against manual failure labels.")
    eval_cmd.add_argument("manifest", type=Path)
    eval_cmd.add_argument("labels", type=Path)
    eval_cmd.add_argument("--json-output", type=Path)
    eval_cmd.add_argument("--markdown-output", type=Path)

    paper_cmd = research_subparsers.add_parser("paper-report", help="Generate paper-ready RQ1-RQ4 result tables.")
    paper_cmd.add_argument("manifest", type=Path)
    paper_cmd.add_argument("--labels", type=Path)
    paper_cmd.add_argument("--json-output", type=Path)
    paper_cmd.add_argument("--markdown-output", type=Path)

    dashboard_cmd = research_subparsers.add_parser("dashboard", help="Generate Web dashboard reports.json from a run manifest.")
    dashboard_cmd.add_argument("manifest", type=Path)
    dashboard_cmd.add_argument("-o", "--output", type=Path, default=Path("web/public/reports.json"))

    summary_cmd = research_subparsers.add_parser("summary", help="Generate a combined full30/hard10/hard30/process-stress paper result summary.")
    summary_cmd.add_argument("--full-manifest", type=Path, default=Path("benchmark/pilot/full30-real/runs.jsonl"))
    summary_cmd.add_argument("--full-process-labels", type=Path, default=Path("benchmark/pilot/full30-real/process-labels.jsonl"))
    summary_cmd.add_argument("--detector-fixture-manifest", type=Path, default=Path("benchmark/detector-fixtures/runs.jsonl"))
    summary_cmd.add_argument("--detector-fixture-labels", type=Path, default=Path("benchmark/detector-fixtures/labels.jsonl"))
    summary_cmd.add_argument("--hard-manifest", type=Path, default=Path("benchmark/hard/pilot/hard10-real/runs.jsonl"))
    summary_cmd.add_argument("--hard-labels", type=Path, default=Path("benchmark/hard/pilot/hard10-real/manual-labels.jsonl"))
    summary_cmd.add_argument("--hard30-manifest", type=Path, default=Path("benchmark/hard/pilot/hard30-real/runs.jsonl"))
    summary_cmd.add_argument("--hard30-labels", type=Path, default=Path("benchmark/hard/pilot/hard30-real/manual-labels.jsonl"))
    summary_cmd.add_argument("--process-stress-manifest", type=Path, default=Path("benchmark/process-stress/pilot/full-real/runs.jsonl"))
    summary_cmd.add_argument("--process-stress-labels", type=Path, default=Path("benchmark/process-stress/pilot/full-real/manual-labels.jsonl"))
    summary_cmd.add_argument("--verification-lift-manifest", type=Path, default=Path("benchmark/verification-lift/pilot/full-real/runs.jsonl"))
    summary_cmd.add_argument("--verification-lift-labels", type=Path, default=Path("benchmark/verification-lift/pilot/full-real/manual-labels.jsonl"))
    summary_cmd.add_argument("--verification-lift-v2-manifest", type=Path, default=Path("benchmark/verification-lift-v2/pilot/full-real/runs.jsonl"))
    summary_cmd.add_argument("--verification-ablation-manifest", type=Path, default=Path("benchmark/verification-ablation/pilot/full-real/runs.jsonl"))
    summary_cmd.add_argument("--verification-ablation-labels", type=Path, default=Path("benchmark/verification-ablation/pilot/full-real/manual-labels.jsonl"))
    summary_cmd.add_argument("--json-output", type=Path)
    summary_cmd.add_argument("--markdown-output", type=Path)

    run_cmd = research_subparsers.add_parser("run", help="Run or dry-run the benchmark collection harness.")
    run_cmd.add_argument("--tasks", type=Path, default=Path("benchmark/tasks.jsonl"))
    run_cmd.add_argument("--output-dir", type=Path, required=True)
    run_cmd.add_argument("--prompt-dir", type=Path, default=Path("benchmark/prompts"))
    run_cmd.add_argument("--prompt-types", nargs="+", choices=["baseline", "intervention"], default=["baseline", "intervention"])
    run_cmd.add_argument("--task-id", action="append", dest="task_ids")
    run_cmd.add_argument("--codex-bin", default="codex")
    run_cmd.add_argument("--sandbox", default="workspace-write")
    run_cmd.add_argument("--timeout-seconds", type=int, default=300)
    run_cmd.add_argument("--dry-run", action="store_true")

    args = parser.parse_args(argv)

    if args.command == "collect":
        trace = parse_jsonl(args.trace)
        output = render_trace_json(trace)
        _write_or_print(output, args.output)
        return 0

    if args.command == "diagnose":
        trace = parse_jsonl(args.trace)
        diagnosis = diagnose(trace)
        output = render_json(trace, diagnosis) if args.format == "json" else render_markdown(trace, diagnosis)
        _write_or_print(output, args.output)
        return 0

    if args.command == "sandbox" and args.sandbox_command == "run":
        config = DockerRunConfig(
            image=args.image,
            cpus=args.cpus,
            memory=args.memory,
            timeout_seconds=args.timeout_seconds,
            network=args.network,
            command=args.docker_command,
            dry_run=args.dry_run,
        )
        rows = run_docker_benchmark(
            tasks_path=args.tasks,
            output_dir=args.output_dir,
            task_ids=args.task_ids,
            config=config,
        )
        manifest_path = args.output_dir / "docker-runs.jsonl"
        write_docker_run_manifest(rows, manifest_path)
        print(f"Wrote {len(rows)} Docker run record(s) to {manifest_path}")
        return 0

    if args.command == "sandbox" and args.sandbox_command == "smoke-check":
        result = smoke_check_fixture(args.task_id)
        print(result.stdout or "", end="")
        return 0 if result.returncode != 0 else 1

    if args.command == "research" and args.research_command == "prompt":
        tasks = {task.task_id: task for task in load_tasks(args.tasks)}
        if args.task_id not in tasks:
            raise SystemExit(f"Unknown task_id: {args.task_id}")
        print(render_prompt(tasks[args.task_id], args.prompt_type, args.prompt_dir))
        return 0

    if args.command == "research" and args.research_command == "aggregate":
        result = aggregate_runs(args.manifest)
        if args.csv_output:
            write_runs_csv(result, args.csv_output)
        if args.json_output or args.markdown_output:
            write_aggregate_outputs(result, args.json_output, args.markdown_output)
        if not (args.csv_output or args.json_output or args.markdown_output):
            print(render_aggregate_markdown(result), end="")
        return 0

    if args.command == "research" and args.research_command == "label-template":
        rows = generate_label_template(args.manifest, include_predictions=args.include_predictions)
        if args.output:
            write_label_template(rows, args.output)
        else:
            print(render_label_template_jsonl(rows), end="")
        return 0

    if args.command == "research" and args.research_command == "evaluate-labels":
        result = evaluate_detector_labels(args.manifest, args.labels)
        if args.json_output or args.markdown_output:
            write_label_evaluation_outputs(result, args.json_output, args.markdown_output)
        else:
            print(render_label_evaluation_markdown(result), end="")
        return 0

    if args.command == "research" and args.research_command == "paper-report":
        result = build_paper_report(args.manifest, labels_path=args.labels)
        if args.json_output or args.markdown_output:
            write_paper_report_outputs(result, args.json_output, args.markdown_output)
        else:
            print(render_paper_report_markdown(result), end="")
        return 0

    if args.command == "research" and args.research_command == "dashboard":
        result = build_dashboard_artifact(args.manifest)
        write_dashboard_artifact(result, args.output)
        print(f"Wrote {len(result['runs'])} dashboard run(s) to {args.output}")
        return 0

    if args.command == "research" and args.research_command == "summary":
        hard30_manifest = args.hard30_manifest if args.hard30_manifest.exists() else None
        hard30_labels = args.hard30_labels if args.hard30_labels.exists() else None
        full_process_labels = args.full_process_labels if args.full_process_labels.exists() else None
        detector_fixture_manifest = args.detector_fixture_manifest if args.detector_fixture_manifest.exists() else None
        detector_fixture_labels = args.detector_fixture_labels if args.detector_fixture_labels.exists() else None
        process_stress_manifest = args.process_stress_manifest if args.process_stress_manifest.exists() else None
        process_stress_labels = args.process_stress_labels if args.process_stress_labels.exists() else None
        verification_lift_manifest = args.verification_lift_manifest if args.verification_lift_manifest.exists() else None
        verification_lift_labels = args.verification_lift_labels if args.verification_lift_labels.exists() else None
        verification_lift_v2_manifest = args.verification_lift_v2_manifest if args.verification_lift_v2_manifest.exists() else None
        verification_ablation_manifest = args.verification_ablation_manifest if args.verification_ablation_manifest.exists() else None
        verification_ablation_labels = args.verification_ablation_labels if args.verification_ablation_labels.exists() else None
        result = build_results_summary(
            args.full_manifest,
            full_process_labels,
            detector_fixture_manifest,
            detector_fixture_labels,
            args.hard_manifest,
            args.hard_labels,
            hard30_manifest,
            hard30_labels,
            process_stress_manifest,
            process_stress_labels,
            verification_lift_manifest,
            verification_lift_labels,
            verification_lift_v2_manifest,
            verification_ablation_manifest,
            verification_ablation_labels,
        )
        if args.json_output or args.markdown_output:
            write_results_summary_outputs(result, args.json_output, args.markdown_output)
        else:
            print(render_results_summary_markdown(result), end="")
        return 0

    if args.command == "research" and args.research_command == "run":
        rows = run_benchmark(
            tasks_path=args.tasks,
            output_dir=args.output_dir,
            prompt_types=args.prompt_types,
            task_ids=args.task_ids,
            prompt_dir=args.prompt_dir,
            codex_bin=args.codex_bin,
            sandbox=args.sandbox,
            timeout_seconds=args.timeout_seconds,
            dry_run=args.dry_run,
        )
        manifest_path = args.output_dir / "runs.jsonl"
        write_run_manifest(rows, manifest_path)
        print(f"Wrote {len(rows)} run record(s) to {manifest_path}")
        return 0

    parser.print_help(sys.stderr)
    return 2


def render_trace_json(trace) -> str:
    import json

    return json.dumps(trace.to_dict(), ensure_ascii=False, indent=2) + "\n"


def _write_or_print(content: str, output: Path | None) -> None:
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding="utf-8")
    else:
        print(content, end="")


if __name__ == "__main__":
    raise SystemExit(main())
