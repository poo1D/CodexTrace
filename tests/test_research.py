import json
from pathlib import Path

from scripts.finalize_hard30_pilot import finalize, preflight, render_preflight
from scripts.finalize_benchmark_pilot import (
    finalize as finalize_benchmark_pilot,
    preflight as preflight_benchmark_pilot,
    render_preflight as render_benchmark_pilot_preflight,
)
from scripts.audit_manual_labels import audit_manual_labels, render_audit
from scripts.audit_failure_taxonomy import build_failure_taxonomy_audit, render_failure_taxonomy_audit_markdown
from scripts.audit_metric_coverage import build_metric_coverage_audit, render_metric_coverage_audit_markdown
from scripts.audit_benchmark_trace_artifact import (
    build_benchmark_trace_artifact_audit,
    render_benchmark_trace_artifact_markdown,
)
from scripts.audit_paired_effects import build_paired_effects_audit, render_paired_effects_markdown
from scripts.audit_paired_effect_limitations import (
    build_paired_effect_limitations_audit,
    render_paired_effect_limitations_markdown,
)
from scripts.audit_demo import build_demo_audit, render_demo_audit_markdown
from scripts.audit_web_artifact import build_web_artifact_audit, render_web_artifact_markdown
from scripts.audit_cli_surface import build_cli_surface_audit, render_cli_surface_markdown
from scripts.audit_ci_surface import build_ci_surface_audit, render_ci_surface_markdown
from scripts.audit_schema_fields import build_schema_field_audit, render_schema_field_audit_markdown
from scripts.audit_parser_event_coverage import build_parser_event_coverage_audit, render_parser_event_coverage_markdown
from scripts.audit_failure_node_traceability import (
    build_failure_node_traceability_audit,
    render_failure_node_traceability_markdown,
)
from scripts.audit_phase_coverage import build_phase_coverage_audit, render_phase_coverage_markdown
from scripts.audit_task_category_coverage import build_task_category_coverage_audit, render_task_category_coverage_markdown
from scripts.audit_harness_protocol import build_harness_protocol_audit, render_harness_protocol_markdown
from scripts.audit_bibliography import build_bibliography_audit, render_bibliography_audit_markdown
from scripts.audit_claim_text_guard import audit_claim_text_guard, render_claim_text_guard_markdown
from scripts.audit_detector_evaluation import build_detector_evaluation_audit, render_detector_evaluation_markdown
from scripts.audit_goal_completion import build_goal_completion_audit, render_goal_completion_audit_markdown
from scripts.audit_hard30_task_diagnosis import build_task_diagnosis, render_task_diagnosis_markdown
from scripts.audit_headline_results import build_headline_results, render_headline_results_markdown
from scripts.audit_label_provenance import build_label_provenance_audit, render_label_provenance_markdown
from scripts.audit_label_limitations import build_label_limitations_audit, render_label_limitations_markdown
from scripts.audit_artifact_guide_sequence import (
    build_artifact_guide_sequence_audit,
    render_artifact_guide_sequence_markdown,
)
from scripts.audit_paper_numbers import build_paper_number_guard, render_paper_number_guard_markdown
from scripts.audit_paper_structure import build_paper_structure_audit, render_paper_structure_audit_markdown
from scripts.audit_paper_claims import build_claim_audit, render_claim_audit_markdown
from scripts.audit_paper_abstract import build_paper_abstract_audit, render_paper_abstract_audit_markdown
from scripts.audit_limitations_traceability import (
    build_limitations_traceability_audit,
    render_limitations_traceability_markdown,
)
from scripts.audit_expected_results_reconciliation import (
    build_expected_results_reconciliation,
    render_expected_results_reconciliation_markdown,
)
from scripts.audit_submission_readiness_plan import (
    build_submission_readiness_plan_audit,
    render_submission_readiness_plan_markdown,
)
from scripts.audit_process_stress_plan import audit_process_stress_plan
from scripts.audit_paper_contributions import build_paper_contribution_audit, render_paper_contribution_audit_markdown
from scripts.audit_paper_conclusion import build_paper_conclusion_audit, render_paper_conclusion_audit_markdown
from scripts.audit_method_pipeline import build_method_pipeline_audit, render_method_pipeline_markdown
from scripts.audit_reviewer_path import build_reviewer_path_audit, render_reviewer_path_audit_markdown
from scripts.audit_related_work import build_related_work_audit, render_related_work_audit_markdown
from scripts.audit_reproducibility import build_reproducibility_audit, render_reproducibility_audit_markdown
from scripts.audit_rule_implementation import build_rule_implementation_audit, render_rule_implementation_markdown
from scripts.audit_rq_table_consistency import (
    build_rq_table_consistency_audit,
    render_rq_table_consistency_markdown,
)
from scripts.audit_rq4_signals import build_rq4_signal_audit, render_rq4_signal_audit_markdown
from scripts.audit_submission_package import build_submission_package, render_submission_package_markdown
from scripts.audit_thesis_revision_decision import build_thesis_revision_decision, render_thesis_revision_decision_markdown
from scripts.audit_thesis_readiness import build_thesis_readiness, render_thesis_readiness_markdown
from scripts.audit_validity_threats import build_validity_threats_audit, render_validity_threats_markdown
from scripts.audit_verification_ablation_plan import audit_verification_ablation_plan
from scripts.audit_verification_lift_plan import audit_verification_lift_plan
from scripts.audit_verification_lift_v2_plan import audit_verification_lift_v2_plan
from scripts.audit_verification_saturation import (
    build_verification_saturation_audit,
    render_verification_saturation_markdown,
)
from scripts.audit_verification_behavior import (
    build_verification_behavior_audit,
    render_verification_behavior_markdown,
)
from scripts.audit_verification_lift_power import (
    build_verification_lift_power_audit,
    render_verification_lift_power_markdown,
)
from scripts.audit_verification_lift_next_experiment import (
    build_verification_lift_next_experiment_audit,
    render_verification_lift_next_experiment_markdown,
)
from scripts.merge_hard30_shards import merge_shards, rewrite_shard_row
from scripts.merge_benchmark_shards import (
    merge_shards as merge_benchmark_shards,
    rewrite_shard_row as rewrite_benchmark_shard_row,
)
from scripts.run_benchmark_shards import (
    build_shard_commands as build_benchmark_shard_commands,
    inspect_shard as inspect_benchmark_shard,
    render_status as render_benchmark_shard_status,
    select_task_ids as select_benchmark_task_ids,
    summarize_shards as summarize_benchmark_shards,
)
from scripts.run_hard30_shards import (
    build_shard_commands,
    filter_commands,
    inspect_shard,
    render_status,
    select_task_ids,
    summarize_shards,
)
from scripts.check_submission_readiness import (
    build_report,
    check_failure_taxonomy_audit_content,
    check_detector_evaluation_audit_content,
    check_goal_completion_audit_content,
    check_headline_results_content,
    check_hard30_task_diagnosis_content,
    check_metric_coverage_audit_content,
    check_benchmark_trace_artifact_content,
    check_paired_effects_audit_content,
    check_paired_effect_limitations_audit_content,
    check_demo_audit_content,
    check_web_artifact_audit_content,
    check_cli_surface_audit_content,
    check_ci_surface_audit_content,
    check_schema_field_audit_content,
    check_parser_event_coverage_content,
    check_failure_node_traceability_content,
    check_phase_coverage_audit_content,
    check_rq4_signal_audit_content,
    check_task_category_coverage_content,
    check_harness_protocol_audit_content,
    check_label_provenance_audit_content,
    check_label_limitations_audit_content,
    check_limitations_traceability_audit_content,
    check_expected_results_reconciliation_content,
    check_submission_readiness_plan_audit_content,
    check_paper_number_guard_content,
    check_artifact_guide_sequence_audit_content,
    check_paper_abstract_audit_content,
    check_bibliography_audit_content,
    check_paper_contribution_audit_content,
    check_paper_conclusion_audit_content,
    check_method_pipeline_audit_content,
    check_paper_structure_audit_content,
    check_related_work_audit_content,
    check_reproducibility_audit_content,
    check_reviewer_path_audit_content,
    check_rule_implementation_audit_content,
    check_rq_table_consistency_audit_content,
    check_claim_text_guard_content,
    check_submission_package_content,
    check_thesis_revision_decision_content,
    check_validity_threats_content,
    check_verification_ablation_plan_audit_content,
    check_verification_behavior_audit_content,
    check_verification_lift_power_audit_content,
    check_verification_saturation_audit_content,
    check_verification_lift_next_experiment_content,
    render_report,
)

from codex_trace.research import (
    aggregate_runs,
    build_paper_report,
    build_results_summary,
    evaluate_detector_labels,
    generate_label_template,
    load_tasks,
    render_label_template_jsonl,
    render_paper_report_markdown,
    render_results_summary_markdown,
    render_prompt,
    run_benchmark,
    run_success_check,
    write_run_manifest,
)


def test_load_tasks_and_render_prompts():
    tasks = {task.task_id: task for task in load_tasks("benchmark/tasks.jsonl")}

    baseline = render_prompt(tasks["CT-001"], "baseline")
    intervention = render_prompt(tasks["CT-001"], "intervention")

    assert len(tasks) == 30
    assert "Fix an off-by-one bug" in baseline
    assert "Complete the task with your normal coding workflow" in baseline
    assert "Run a focused verification command after the edit" in intervention


def test_hard_task_manifest_includes_first_expansion_fixtures():
    tasks = {task.task_id: task for task in load_tasks("benchmark/hard/tasks.jsonl")}

    assert len(tasks) == 50
    assert tasks["HARD-011"].repo_hint == "python/json_patch"
    assert tasks["HARD-011"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-011"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-012"].repo_hint == "python/http_client"
    assert tasks["HARD-012"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-012"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-013"].repo_hint == "typescript/filter_builder"
    assert tasks["HARD-013"].public_success_check == "npm test"
    assert tasks["HARD-013"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-014"].repo_hint == "python/permission_matrix"
    assert tasks["HARD-014"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-014"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-015"].repo_hint == "typescript/package_exports"
    assert tasks["HARD-015"].public_success_check == "npm run build"
    assert tasks["HARD-015"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-016"].repo_hint == "python/time_window"
    assert tasks["HARD-016"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-016"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-017"].repo_hint == "typescript/batch_queue"
    assert tasks["HARD-017"].public_success_check == "npm test"
    assert tasks["HARD-017"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-018"].repo_hint == "python/yaml_frontmatter"
    assert tasks["HARD-018"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-018"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-019"].repo_hint == "python/search_ranker"
    assert tasks["HARD-019"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-019"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-020"].repo_hint == "typescript/asset_loader"
    assert tasks["HARD-020"].public_success_check == "npm test"
    assert tasks["HARD-020"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-021"].repo_hint == "python/currency_parser"
    assert tasks["HARD-021"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-021"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-022"].repo_hint == "typescript/state_machine"
    assert tasks["HARD-022"].public_success_check == "npm test"
    assert tasks["HARD-022"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-023"].repo_hint == "python/cache_stampede"
    assert tasks["HARD-023"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-023"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-024"].repo_hint == "typescript/csv_stream"
    assert tasks["HARD-024"].public_success_check == "npm test"
    assert tasks["HARD-024"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-025"].repo_hint == "python/typing_protocol"
    assert tasks["HARD-025"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-025"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-026"].repo_hint == "python/rules_engine"
    assert tasks["HARD-026"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-026"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-027"].repo_hint == "typescript/date_formatter"
    assert tasks["HARD-027"].public_success_check == "npm test"
    assert tasks["HARD-027"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-028"].repo_hint == "python/path_normalizer"
    assert tasks["HARD-028"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-028"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-029"].repo_hint == "typescript/validation_pipeline"
    assert tasks["HARD-029"].public_success_check == "npm test"
    assert tasks["HARD-029"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-030"].repo_hint == "python/template_renderer"
    assert tasks["HARD-030"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-030"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-031"].repo_hint == "python/env_manifest_resolver"
    assert tasks["HARD-031"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-031"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-032"].repo_hint == "typescript/undoable_queue"
    assert tasks["HARD-032"].public_success_check == "npm test"
    assert tasks["HARD-032"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-033"].repo_hint == "python/log_redactor"
    assert tasks["HARD-033"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-033"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-034"].repo_hint == "python/feature_flags"
    assert tasks["HARD-034"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-034"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-035"].repo_hint == "python/retry_policy"
    assert tasks["HARD-035"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-035"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-036"].repo_hint == "typescript/metrics_window"
    assert tasks["HARD-036"].public_success_check == "npm test"
    assert tasks["HARD-036"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-037"].repo_hint == "python/sliding_limiter"
    assert tasks["HARD-037"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-037"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-038"].repo_hint == "typescript/source_map_ranges"
    assert tasks["HARD-038"].public_success_check == "npm test"
    assert tasks["HARD-038"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-039"].repo_hint == "python/cli_report_writer"
    assert tasks["HARD-039"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-039"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-040"].repo_hint == "python/ledger_reconciler"
    assert tasks["HARD-040"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-040"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-041"].repo_hint == "typescript/range_set"
    assert tasks["HARD-041"].public_success_check == "npm test"
    assert tasks["HARD-041"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-042"].repo_hint == "python/snapshot_manifest"
    assert tasks["HARD-042"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-042"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-043"].repo_hint == "python/migration_runner"
    assert tasks["HARD-043"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-043"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-044"].repo_hint == "typescript/icu_plural_format"
    assert tasks["HARD-044"].public_success_check == "npm test"
    assert tasks["HARD-044"].success_check == "node ../grader/check.mjs"
    assert tasks["HARD-045"].repo_hint == "python/stream_window_join"
    assert tasks["HARD-045"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-045"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-046"].repo_hint == "python/sqlite_migration_runner"
    assert tasks["HARD-046"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-046"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-047"].repo_hint == "python/webhook_replay_guard"
    assert tasks["HARD-047"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-047"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-048"].repo_hint == "python/cursor_pagination"
    assert tasks["HARD-048"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-048"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-049"].repo_hint == "python/test_sharder"
    assert tasks["HARD-049"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-049"].success_check == "python3 ../grader/check.py"
    assert tasks["HARD-050"].repo_hint == "python/config_overlay_resolver"
    assert tasks["HARD-050"].public_success_check == "python3 -m unittest discover -s tests"
    assert tasks["HARD-050"].success_check == "python3 ../grader/check.py"


def test_hard30_selection_is_balanced_and_runnable():
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")
    task_ids = selection_dir.joinpath("task_ids.txt").read_text().splitlines()
    tasks = {task.task_id: task for task in load_tasks(str(selection_dir / "tasks.jsonl"))}
    manifest = json.loads(selection_dir.joinpath("manifest.json").read_text())

    assert len(task_ids) == 30
    assert len(set(task_ids)) == 30
    assert task_ids[:10] == [f"HARD-{index:03d}" for index in range(1, 11)]
    assert list(tasks) == task_ids
    assert manifest["task_count"] == 30
    assert manifest["expected_run_records"] == 60
    assert set(manifest["category_counts"]) >= {
        "bug_fix",
        "ci_failure",
        "dependency_friction",
        "error_recovery",
        "feature",
        "multi_turn_change",
        "stateful_regression",
    }


def test_hard30_shard_commands_run_one_task_per_shard(tmp_path):
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")
    commands = build_shard_commands(
        ["HARD-001", "HARD-002"],
        selection_dir=selection_dir,
        run_dir=tmp_path / "hard30-real",
        timeout_seconds=900,
        codex_bin="codex-test",
        sandbox="danger-full-access",
        dry_run=True,
    )

    assert [command.task_id for command in commands] == ["HARD-001", "HARD-002"]
    assert commands[0].shard_dir == tmp_path / "hard30-real" / "shards" / "HARD-001"
    assert commands[0].metadata_path == commands[0].shard_dir / "shard-run.json"
    assert commands[0].command.count("--task-id") == 1
    assert commands[0].command[commands[0].command.index("--task-id") + 1] == "HARD-001"
    assert "--dry-run" in commands[0].command
    assert commands[0].command[commands[0].command.index("--timeout-seconds") + 1] == "900"
    assert commands[0].command[commands[0].command.index("--codex-bin") + 1] == "codex-test"
    assert commands[0].command[commands[0].command.index("--sandbox") + 1] == "danger-full-access"


def test_hard30_shard_task_selection_supports_safe_slices():
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")

    assert select_task_ids(selection_dir, offset=1, limit=3) == ["HARD-002", "HARD-003", "HARD-004"]
    assert select_task_ids(selection_dir, explicit_task_ids=["HARD-010"], offset=5, limit=2) == ["HARD-010"]


def test_hard30_shard_task_selection_rejects_invalid_slices():
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")

    try:
        select_task_ids(selection_dir, offset=-1)
    except ValueError as error:
        assert str(error) == "offset must be non-negative"
    else:
        raise AssertionError("negative offset should fail")

    try:
        select_task_ids(selection_dir, limit=0)
    except ValueError as error:
        assert str(error) == "limit must be at least 1"
    else:
        raise AssertionError("zero limit should fail")


def test_benchmark_shard_commands_target_verification_lift_v2_prompt_dir(tmp_path):
    tasks_path = Path("benchmark/verification-lift-v2/tasks.jsonl")
    prompt_dir = Path("benchmark/verification-lift-v2/prompts")
    selected = select_benchmark_task_ids(tasks_path, offset=1, limit=2)
    commands = build_benchmark_shard_commands(
        selected,
        tasks_path=tasks_path,
        prompt_dir=prompt_dir,
        run_dir=tmp_path / "verification-lift-v2-real",
        timeout_seconds=900,
        codex_bin="codex-test",
        sandbox="workspace-write",
        dry_run=True,
    )

    assert selected == ["VLV2-002", "VLV2-003"]
    assert len(commands) == 2
    assert commands[0].task_id == "VLV2-002"
    assert commands[0].shard_dir == tmp_path / "verification-lift-v2-real" / "shards" / "VLV2-002"
    assert commands[0].command[commands[0].command.index("--tasks") + 1] == str(tasks_path)
    assert commands[0].command[commands[0].command.index("--prompt-dir") + 1] == str(prompt_dir)
    assert commands[0].command[commands[0].command.index("--task-id") + 1] == "VLV2-002"
    assert commands[0].command[commands[0].command.index("--codex-bin") + 1] == "codex-test"
    assert commands[0].command[commands[0].command.index("--timeout-seconds") + 1] == "900"
    assert "--dry-run" in commands[0].command


def test_benchmark_shard_status_summary_reports_v2_readiness(tmp_path):
    tasks_path = Path("benchmark/verification-lift-v2/tasks.jsonl")
    prompt_dir = Path("benchmark/verification-lift-v2/prompts")
    commands = build_benchmark_shard_commands(
        ["VLV2-001", "VLV2-002"],
        tasks_path=tasks_path,
        prompt_dir=prompt_dir,
        run_dir=tmp_path / "verification-lift-v2-real",
        dry_run=True,
    )
    complete_rows = [
        {"task_id": "VLV2-001", "prompt_type": "baseline", "trace_path": "a", "codex_exit_code": 0},
        {"task_id": "VLV2-001", "prompt_type": "intervention", "trace_path": "b", "codex_exit_code": 0},
    ]
    commands[0].shard_dir.mkdir(parents=True)
    commands[0].shard_dir.joinpath("a").write_text("{}\n", encoding="utf-8")
    commands[0].shard_dir.joinpath("b").write_text("{}\n", encoding="utf-8")
    commands[0].shard_dir.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in complete_rows),
        encoding="utf-8",
    )

    status = inspect_benchmark_shard(commands[0])
    summary = summarize_benchmark_shards(commands)
    rendered = render_benchmark_shard_status(summary)

    assert status.complete is True
    assert summary["completed"] == ["VLV2-001"]
    assert summary["missing"] == ["VLV2-002"]
    assert summary["record_count"] == 2
    assert summary["expected_record_count"] == 4
    assert "Benchmark Shard Status" in rendered
    assert "Ready to merge: no" in rendered


def test_hard30_shard_skip_complete_filters_finished_manifests(tmp_path):
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")
    commands = build_shard_commands(
        ["HARD-001", "HARD-002"],
        selection_dir=selection_dir,
        run_dir=tmp_path / "hard30-real",
        dry_run=True,
    )
    completed = commands[0].shard_dir / "runs.jsonl"
    completed.parent.mkdir(parents=True)
    commands[0].shard_dir.joinpath("a").write_text("{}\n", encoding="utf-8")
    commands[0].shard_dir.joinpath("b").write_text("{}\n", encoding="utf-8")
    completed.write_text(
        "\n".join([
            json.dumps({"task_id": "HARD-001", "prompt_type": "baseline", "trace_path": "a", "codex_exit_code": 0}),
            json.dumps({"task_id": "HARD-001", "prompt_type": "intervention", "trace_path": "b", "codex_exit_code": 0}),
        ]) + "\n",
        encoding="utf-8",
    )

    assert inspect_shard(commands[0]).complete is True
    assert inspect_shard(commands[1]).complete is False
    assert filter_commands(commands, skip_complete=True) == [commands[1]]
    assert filter_commands(commands, skip_complete=False) == commands


def test_hard30_shard_status_summary_reports_readiness(tmp_path):
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")
    commands = build_shard_commands(
        ["HARD-001", "HARD-002", "HARD-003", "HARD-004"],
        selection_dir=selection_dir,
        run_dir=tmp_path / "hard30-real",
        dry_run=True,
    )
    complete_rows = [
        {"task_id": "HARD-001", "prompt_type": "baseline", "trace_path": "a", "codex_exit_code": 0},
        {"task_id": "HARD-001", "prompt_type": "intervention", "trace_path": "b", "codex_exit_code": 0},
    ]
    incomplete_rows = [
        {"task_id": "HARD-002", "prompt_type": "baseline", "trace_path": "c"},
    ]
    commands[0].shard_dir.mkdir(parents=True)
    commands[0].shard_dir.joinpath("a").write_text("{}\n", encoding="utf-8")
    commands[0].shard_dir.joinpath("b").write_text("{}\n", encoding="utf-8")
    commands[0].shard_dir.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in complete_rows),
        encoding="utf-8",
    )
    commands[1].shard_dir.mkdir(parents=True)
    commands[1].shard_dir.joinpath("c").write_text("{}\n", encoding="utf-8")
    commands[1].shard_dir.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in incomplete_rows),
        encoding="utf-8",
    )
    commands[2].shard_dir.mkdir(parents=True)
    commands[2].metadata_path.write_text(json.dumps({"returncode": 2}), encoding="utf-8")

    summary = summarize_shards(commands)
    rendered = render_status(summary)

    assert summary["task_count"] == 4
    assert summary["completed_count"] == 1
    assert summary["failed_count"] == 1
    assert summary["failed"] == ["HARD-003"]
    assert summary["incomplete"] == ["HARD-002"]
    assert summary["missing"] == ["HARD-003", "HARD-004"]
    assert summary["record_count"] == 3
    assert summary["expected_record_count"] == 8
    assert summary["ready_to_merge"] is False
    assert summary["shards"][0]["prompt_types"] == ["baseline", "intervention"]
    assert summary["shards"][2]["returncode"] == 2
    assert summary["shards"][2]["invalid_reasons"] == []
    assert summary["shards"][2]["metadata_path"].endswith("shard-run.json")
    assert "Ready to merge: no" in rendered
    assert "Failed shards: 1" in rendered
    assert "Failed: HARD-003" in rendered
    assert "Incomplete: HARD-002" in rendered
    assert "Missing: HARD-003, HARD-004" in rendered


def test_hard30_shard_status_rejects_failed_codex_or_empty_trace(tmp_path):
    selection_dir = Path("benchmark/hard/pilot/hard30-selection")
    commands = build_shard_commands(
        ["HARD-001"],
        selection_dir=selection_dir,
        run_dir=tmp_path / "hard30-real",
    )
    shard_dir = commands[0].shard_dir
    shard_dir.mkdir(parents=True)
    shard_dir.joinpath("empty.jsonl").write_text("", encoding="utf-8")
    shard_dir.joinpath("runs.jsonl").write_text(
        "\n".join([
            json.dumps({
                "task_id": "HARD-001",
                "prompt_type": "baseline",
                "trace_path": "empty.jsonl",
                "codex_exit_code": 1,
            }),
            json.dumps({
                "task_id": "HARD-001",
                "prompt_type": "intervention",
                "trace_path": "missing.jsonl",
                "codex_exit_code": 0,
            }),
        ]) + "\n",
        encoding="utf-8",
    )

    status = inspect_shard(commands[0])
    summary = summarize_shards(commands)

    assert status.complete is False
    assert status.record_count == 2
    assert "baseline codex_exit_code=1" in status.invalid_reasons
    assert "baseline empty trace: empty.jsonl" in status.invalid_reasons
    assert "intervention missing trace: missing.jsonl" in status.invalid_reasons
    assert summary["failed"] == ["HARD-001"]
    assert summary["incomplete"] == ["HARD-001"]


def test_merge_hard30_shards_rewrites_relative_paths(tmp_path):
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    selection_dir.joinpath("task_ids.txt").write_text("HARD-001\nHARD-002\n", encoding="utf-8")
    run_dir = tmp_path / "hard30-real"
    for task_id in ("HARD-001", "HARD-002"):
        shard_dir = run_dir / "shards" / task_id
        shard_dir.mkdir(parents=True)
        rows = [
            {
                "task_id": task_id,
                "prompt_type": "baseline",
                "trace_path": f"{task_id}/baseline/trace.jsonl",
                "outcome": "failure",
                "workdir": f"{task_id}/baseline/repo",
                "grader_path": f"{task_id}/baseline/grader",
                "prompt_path": f"{task_id}/baseline/prompt.md",
            },
            {
                "task_id": task_id,
                "prompt_type": "intervention",
                "trace_path": f"{task_id}/intervention/trace.jsonl",
                "outcome": "success",
                "workdir": f"{task_id}/intervention/repo",
                "grader_path": "",
                "prompt_path": f"{task_id}/intervention/prompt.md",
            },
        ]
        shard_dir.joinpath("runs.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    merged = merge_shards(run_dir=run_dir, selection_dir=selection_dir)
    manifest_rows = [
        json.loads(line)
        for line in run_dir.joinpath("runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(merged) == 4
    assert manifest_rows == merged
    assert manifest_rows[0]["trace_path"] == "shards/HARD-001/HARD-001/baseline/trace.jsonl"
    assert manifest_rows[0]["workdir"] == "shards/HARD-001/HARD-001/baseline/repo"
    assert manifest_rows[0]["grader_path"] == "shards/HARD-001/HARD-001/baseline/grader"
    assert manifest_rows[1]["grader_path"] == ""


def test_rewrite_shard_row_leaves_empty_paths_empty():
    row = rewrite_shard_row({"trace_path": "HARD-001/baseline/trace.jsonl", "grader_path": ""}, Path("shards/HARD-001"))

    assert row["trace_path"] == "shards/HARD-001/HARD-001/baseline/trace.jsonl"
    assert row["grader_path"] == ""


def test_merge_benchmark_shards_rewrites_relative_paths(tmp_path):
    tasks_path = tmp_path / "tasks.jsonl"
    task_ids = ["VLV2-001", "VLV2-002"]
    tasks_path.write_text(
        "".join(
            json.dumps({
                "task_id": task_id,
                "category": "verification_lift_v2",
                "instruction": "Fix it.",
                "success_check": "python3 ../grader/check.py",
                "fixture_path": ".",
            }) + "\n"
            for task_id in task_ids
        ),
        encoding="utf-8",
    )
    run_dir = tmp_path / "verification-lift-v2-real"
    for task_id in task_ids:
        shard_dir = run_dir / "shards" / task_id
        shard_dir.mkdir(parents=True)
        rows = [
            {
                "task_id": task_id,
                "prompt_type": "baseline",
                "trace_path": f"{task_id}/baseline/trace.jsonl",
                "outcome": "failure",
                "workdir": f"{task_id}/baseline/repo",
                "grader_path": f"{task_id}/baseline/grader",
                "prompt_path": f"{task_id}/baseline/prompt.md",
            },
            {
                "task_id": task_id,
                "prompt_type": "intervention",
                "trace_path": f"{task_id}/intervention/trace.jsonl",
                "outcome": "success",
                "workdir": f"{task_id}/intervention/repo",
                "grader_path": "",
                "prompt_path": f"{task_id}/intervention/prompt.md",
            },
        ]
        shard_dir.joinpath("runs.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    merged = merge_benchmark_shards(run_dir=run_dir, tasks_path=tasks_path)
    manifest_rows = [
        json.loads(line)
        for line in run_dir.joinpath("runs.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    assert len(merged) == 4
    assert manifest_rows == merged
    assert manifest_rows[0]["trace_path"] == "shards/VLV2-001/VLV2-001/baseline/trace.jsonl"
    assert manifest_rows[0]["workdir"] == "shards/VLV2-001/VLV2-001/baseline/repo"
    assert manifest_rows[1]["grader_path"] == ""


def test_rewrite_benchmark_shard_row_leaves_empty_paths_empty():
    row = rewrite_benchmark_shard_row({"trace_path": "VLV2-001/baseline/trace.jsonl", "grader_path": ""}, Path("shards/VLV2-001"))

    assert row["trace_path"] == "shards/VLV2-001/VLV2-001/baseline/trace.jsonl"
    assert row["grader_path"] == ""


def test_finalize_hard30_pilot_writes_report_artifacts(tmp_path):
    root = Path.cwd()
    runs = [
        {
            "task_id": "CT-001",
            "prompt_type": "baseline",
            "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
            "outcome": "failure",
        },
        {
            "task_id": "CT-001",
            "prompt_type": "intervention",
            "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
            "outcome": "success",
        },
    ]
    manifest = tmp_path / "runs.jsonl"
    manifest.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in runs), encoding="utf-8")

    written = finalize(tmp_path)

    expected = {
        "aggregate.json",
        "aggregate.md",
        "runs.csv",
        "paired-task-deltas.csv",
        "paired-task-summary.csv",
        "labels.jsonl",
        "paper-report.json",
        "paper-report.md",
    }
    assert {path.name for path in written} == expected
    assert all((tmp_path / name).exists() for name in expected)
    assert "suggested_tags" in (tmp_path / "labels.jsonl").read_text()
    paired_csv = (tmp_path / "paired-task-deltas.csv").read_text(encoding="utf-8")
    assert "task_id,baseline_outcome,intervention_outcome,success_delta" in paired_csv
    assert "CT-001,failure,success,1" in paired_csv
    paired_summary_csv = (tmp_path / "paired-task-summary.csv").read_text(encoding="utf-8")
    assert "metric,n,improved,regressed,unchanged,avg_delta" in paired_summary_csv
    assert "success_delta,1,1,0,0,1" in paired_summary_csv


def test_finalize_benchmark_pilot_writes_report_artifacts(tmp_path):
    root = Path.cwd()
    runs = [
        {
            "task_id": "VLV2-001",
            "prompt_type": "baseline",
            "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
            "outcome": "failure",
        },
        {
            "task_id": "VLV2-001",
            "prompt_type": "intervention",
            "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
            "outcome": "success",
        },
    ]
    tmp_path.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in runs),
        encoding="utf-8",
    )

    written = finalize_benchmark_pilot(tmp_path)

    expected = {
        "aggregate.json",
        "aggregate.md",
        "runs.csv",
        "paired-task-deltas.csv",
        "paired-task-summary.csv",
        "labels.jsonl",
        "paper-report.json",
        "paper-report.md",
    }
    assert {path.name for path in written} == expected
    assert all((tmp_path / name).exists() for name in expected)
    assert "VLV2-001,failure,success,1" in (tmp_path / "paired-task-deltas.csv").read_text(encoding="utf-8")


def test_benchmark_pilot_preflight_accepts_complete_manifest(tmp_path):
    root = Path.cwd()
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps({
            "task_id": "VLV2-001",
            "category": "verification_lift_v2",
            "instruction": "Fix it.",
            "success_check": "python3 ../grader/check.py",
            "fixture_path": ".",
        }) + "\n",
        encoding="utf-8",
    )
    rows = [
        {
            "task_id": "VLV2-001",
            "prompt_type": "baseline",
            "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
            "outcome": "failure",
        },
        {
            "task_id": "VLV2-001",
            "prompt_type": "intervention",
            "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
            "outcome": "success",
        },
    ]
    tmp_path.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    summary = preflight_benchmark_pilot(tmp_path, tasks)
    rendered = render_benchmark_pilot_preflight(summary)

    assert summary["ok"] is True
    assert summary["run_records"] == 2
    assert summary["missing_prompt_pairs"] == []
    assert summary["missing_trace_paths"] == []
    assert "Ready to finalize: yes" in rendered


def test_benchmark_pilot_preflight_rejects_missing_trace_and_prompt_pair(tmp_path):
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        json.dumps({
            "task_id": "VLV2-001",
            "category": "verification_lift_v2",
            "instruction": "Fix it.",
            "success_check": "python3 ../grader/check.py",
            "fixture_path": ".",
        }) + "\n",
        encoding="utf-8",
    )
    tmp_path.joinpath("runs.jsonl").write_text(
        json.dumps({
            "task_id": "VLV2-001",
            "prompt_type": "baseline",
            "trace_path": "missing/trace.jsonl",
            "outcome": "failure",
        }) + "\n",
        encoding="utf-8",
    )

    summary = preflight_benchmark_pilot(tmp_path, tasks)
    rendered = render_benchmark_pilot_preflight(summary)

    assert summary["ok"] is False
    assert summary["run_records"] == 1
    assert summary["missing_prompt_pairs"] == [{"task_id": "VLV2-001", "prompt_type": "intervention"}]
    assert summary["missing_trace_paths"] == [
        {"task_id": "VLV2-001", "prompt_type": "baseline", "trace_path": "missing/trace.jsonl"}
    ]
    assert "Ready to finalize: no" in rendered
    assert "Missing prompt pairs: VLV2-001/intervention" in rendered
    assert "Missing trace files: VLV2-001/baseline -> missing/trace.jsonl" in rendered


def test_hard30_preflight_accepts_complete_manifest(tmp_path):
    root = Path.cwd()
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    selection_dir.joinpath("task_ids.txt").write_text("HARD-001\n", encoding="utf-8")
    rows = [
        {
            "task_id": "HARD-001",
            "prompt_type": "baseline",
            "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
            "outcome": "failure",
        },
        {
            "task_id": "HARD-001",
            "prompt_type": "intervention",
            "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
            "outcome": "success",
        },
    ]
    tmp_path.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )

    summary = preflight(tmp_path, selection_dir)
    rendered = render_preflight(summary)

    assert summary["ok"] is True
    assert summary["run_records"] == 2
    assert summary["missing_prompt_pairs"] == []
    assert summary["missing_trace_paths"] == []
    assert "Ready to finalize: yes" in rendered


def test_hard30_preflight_rejects_missing_trace_and_prompt_pair(tmp_path):
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    selection_dir.joinpath("task_ids.txt").write_text("HARD-001\n", encoding="utf-8")
    tmp_path.joinpath("runs.jsonl").write_text(
        json.dumps({
            "task_id": "HARD-001",
            "prompt_type": "baseline",
            "trace_path": "missing/trace.jsonl",
            "outcome": "failure",
        }) + "\n",
        encoding="utf-8",
    )

    summary = preflight(tmp_path, selection_dir)
    rendered = render_preflight(summary)

    assert summary["ok"] is False
    assert summary["run_records"] == 1
    assert summary["missing_prompt_pairs"] == [{"task_id": "HARD-001", "prompt_type": "intervention"}]
    assert summary["missing_trace_paths"] == [
        {"task_id": "HARD-001", "prompt_type": "baseline", "trace_path": "missing/trace.jsonl"}
    ]
    assert "Ready to finalize: no" in rendered
    assert "Missing prompt pairs: HARD-001/intervention" in rendered
    assert "Missing trace files: HARD-001/baseline -> missing/trace.jsonl" in rendered


def test_submission_readiness_reports_blocking_missing_hard30_runs(tmp_path):
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    task_ids = [f"HARD-{index:03d}" for index in range(1, 31)]
    selection_dir.joinpath("task_ids.txt").write_text("\n".join(task_ids) + "\n", encoding="utf-8")
    selection_dir.joinpath("tasks.jsonl").write_text("{}\n", encoding="utf-8")
    selection_dir.joinpath("manifest.json").write_text("{}\n", encoding="utf-8")

    report = build_report(selection_dir, tmp_path / "missing-run-dir")
    markdown = render_report(report)

    assert report["ready"] is False
    assert "hard30 real runs" in report["blocking"]
    assert "hard30 finalized outputs" in report["blocking"]
    assert "hard30 manual labels" in report["blocking"]
    assert [action["name"] for action in report["next_actions"]] == [
        "collect hard30 five-task ramp",
        "collect remaining hard30 real traces",
        "merge completed hard30 shards",
        "preflight hard30 manifest",
        "finalize hard30 reports",
        "label hard30 failures",
        "audit hard30 manual labels",
        "evaluate hard30 labels",
    ]
    assert "run_hard30_shards.py" in report["next_actions"][0]["command"]
    assert "--limit 5" in report["next_actions"][0]["command"]
    assert "--max-parallel 15" in report["next_actions"][1]["command"]
    assert "audit_manual_labels.py" in report["next_actions"][-2]["command"]
    assert "## Next Actions" in markdown
    assert "Ready: no" in markdown


def test_submission_readiness_accepts_complete_synthetic_artifact(tmp_path):
    root = Path.cwd()
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    task_ids = [f"HARD-{index:03d}" for index in range(1, 31)]
    selection_dir.joinpath("task_ids.txt").write_text("\n".join(task_ids) + "\n", encoding="utf-8")
    selection_dir.joinpath("tasks.jsonl").write_text("{}\n", encoding="utf-8")
    selection_dir.joinpath("manifest.json").write_text("{}\n", encoding="utf-8")
    run_dir = tmp_path / "hard30-real"
    run_dir.mkdir()
    runs = []
    labels = []
    for task_id in task_ids:
        runs.extend([
            {
                "task_id": task_id,
                "prompt_type": "baseline",
                "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
                "outcome": "failure",
            },
            {
                "task_id": task_id,
                "prompt_type": "intervention",
                "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
                "outcome": "success",
            },
        ])
        labels.append({
            "task_id": task_id,
            "prompt_type": "baseline",
            "outcome": "failure",
            "failure_tags": ["hidden_semantic_edge_case"],
            "notes": "Hidden semantic edge case captured by the synthetic label.",
        })
    run_dir.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in runs),
        encoding="utf-8",
    )
    paired_summary = {
        metric: {"n": 30, "improved": 1, "regressed": 0, "unchanged": 29, "avg_delta": 0}
        for metric in ("success_delta", "verification_delta", "repeated_tool_call_delta", "token_usage_delta", "failure_score_delta")
    }
    labeled_report = {
        "detector_evaluation": {"summary": {"labels": 1}, "labels": {"hidden_semantic_edge_case": {"fn": 30}}},
        "paired_task_summary": paired_summary,
    }
    label_eval = {"summary": {"labels": 1}, "labels": {"hidden_semantic_edge_case": {"fn": 30}}}
    for name in (
        "aggregate.json",
        "aggregate.md",
        "runs.csv",
        "paired-task-deltas.csv",
        "paired-task-summary.csv",
        "labels.jsonl",
        "paper-report.json",
        "paper-report.md",
        "paper-report-labeled.md",
        "label-eval.md",
    ):
        run_dir.joinpath(name).write_text("{}\n", encoding="utf-8")
    run_dir.joinpath("paper-report-labeled.json").write_text(json.dumps(labeled_report) + "\n", encoding="utf-8")
    run_dir.joinpath("label-eval.json").write_text(json.dumps(label_eval) + "\n", encoding="utf-8")
    run_dir.joinpath("manual-labels.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in labels),
        encoding="utf-8",
    )

    report = build_report(selection_dir, run_dir)
    markdown = render_report(report)

    assert report["ready"] is True
    assert report["blocking"] == []
    assert report["next_actions"] == []
    assert "Ready: yes" in markdown
    assert "| rq4 signal audit | pass | `docs/rq4_signal_audit.md` |" in markdown
    assert "submission-ready hard30 artifact" in report["positioning"]
    paper_check = next(check for check in report["checks"] if check["name"] == "paper draft content")
    assert paper_check["ok"] is True
    protocol_check = next(check for check in report["checks"] if check["name"] == "experiment protocol content")
    assert protocol_check["ok"] is True


def test_submission_readiness_plan_matches_current_gate_status():
    text = Path("docs/submission_readiness_plan.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Current status: this gate passes for the stored hard30 artifact." in text
    assert "submission-ready hard30 artifact" in text
    assert "if traces, generated tables, or manual labels are missing" in normalized
    assert "repeat a hard-tier subset to estimate variance" in normalized
    assert "collect more natural observable process-failure positives" in normalized


def test_submission_readiness_plan_audit_preserves_remaining_work():
    result = build_submission_readiness_plan_audit()
    markdown = render_submission_readiness_plan_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["passed"] == 15
    assert all(row["passed"] for row in result["checks"])
    assert "submission-ready hard30 artifact" in markdown
    assert "repeat a hard-tier subset to estimate variance" in markdown
    assert "collect more natural observable process-failure positives" in markdown


def test_submission_readiness_rejects_low_quality_manual_labels(tmp_path):
    root = Path.cwd()
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    task_ids = [f"HARD-{index:03d}" for index in range(1, 31)]
    selection_dir.joinpath("task_ids.txt").write_text("\n".join(task_ids) + "\n", encoding="utf-8")
    selection_dir.joinpath("tasks.jsonl").write_text("{}\n", encoding="utf-8")
    selection_dir.joinpath("manifest.json").write_text("{}\n", encoding="utf-8")
    run_dir = tmp_path / "hard30-real"
    run_dir.mkdir()
    rows = []
    labels = []
    for task_id in task_ids:
        rows.extend([
            {
                "task_id": task_id,
                "prompt_type": "baseline",
                "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
                "outcome": "failure",
            },
            {
                "task_id": task_id,
                "prompt_type": "intervention",
                "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
                "outcome": "success",
            },
        ])
        labels.append({
            "task_id": task_id,
            "prompt_type": "baseline",
            "outcome": "failure",
            "failure_tags": ["not_a_taxonomy_tag"],
            "notes": "",
        })
    run_dir.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    paired_summary = {
        metric: {"n": 30, "improved": 1, "regressed": 0, "unchanged": 29, "avg_delta": 0}
        for metric in ("success_delta", "verification_delta", "repeated_tool_call_delta", "token_usage_delta", "failure_score_delta")
    }
    labeled_report = {
        "detector_evaluation": {"summary": {"labels": 1}, "labels": {"hidden_semantic_edge_case": {"fn": 30}}},
        "paired_task_summary": paired_summary,
    }
    label_eval = {"summary": {"labels": 1}, "labels": {"hidden_semantic_edge_case": {"fn": 30}}}
    for name in (
        "aggregate.json",
        "aggregate.md",
        "runs.csv",
        "paired-task-deltas.csv",
        "paired-task-summary.csv",
        "labels.jsonl",
        "paper-report.json",
        "paper-report.md",
        "paper-report-labeled.md",
        "label-eval.md",
    ):
        run_dir.joinpath(name).write_text("{}\n", encoding="utf-8")
    run_dir.joinpath("paper-report-labeled.json").write_text(json.dumps(labeled_report) + "\n", encoding="utf-8")
    run_dir.joinpath("label-eval.json").write_text(json.dumps(label_eval) + "\n", encoding="utf-8")
    run_dir.joinpath("manual-labels.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in labels),
        encoding="utf-8",
    )

    report = build_report(selection_dir, run_dir)
    label_check = next(check for check in report["checks"] if check["name"] == "hard30 manual labels")
    markdown = render_report(report)

    assert report["ready"] is False
    assert label_check["unknown_tags"] == ["not_a_taxonomy_tag"]
    assert len(label_check["missing_notes"]) == 30
    assert "hard30 manual labels" in report["blocking"]
    assert "unknown tags: not_a_taxonomy_tag" in markdown


def test_submission_readiness_rejects_missing_manifest_failure_label(tmp_path):
    root = Path.cwd()
    selection_dir = tmp_path / "selection"
    selection_dir.mkdir()
    task_ids = [f"HARD-{index:03d}" for index in range(1, 31)]
    selection_dir.joinpath("task_ids.txt").write_text("\n".join(task_ids) + "\n", encoding="utf-8")
    selection_dir.joinpath("tasks.jsonl").write_text("{}\n", encoding="utf-8")
    selection_dir.joinpath("manifest.json").write_text("{}\n", encoding="utf-8")
    run_dir = tmp_path / "hard30-real"
    run_dir.mkdir()
    rows = []
    labels = []
    for task_id in task_ids:
        rows.extend([
            {
                "task_id": task_id,
                "prompt_type": "baseline",
                "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
                "outcome": "failure",
            },
            {
                "task_id": task_id,
                "prompt_type": "intervention",
                "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
                "outcome": "success",
            },
        ])
        if task_id != "HARD-030":
            labels.append({
                "task_id": task_id,
                "prompt_type": "baseline",
                "outcome": "failure",
                "failure_tags": ["hidden_semantic_edge_case"],
                "notes": "Hidden semantic edge case captured by the synthetic label.",
            })
    run_dir.joinpath("runs.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    paired_summary = {
        metric: {"n": 30, "improved": 1, "regressed": 0, "unchanged": 29, "avg_delta": 0}
        for metric in ("success_delta", "verification_delta", "repeated_tool_call_delta", "token_usage_delta", "failure_score_delta")
    }
    labeled_report = {
        "detector_evaluation": {"summary": {"labels": 1}, "labels": {"hidden_semantic_edge_case": {"fn": 30}}},
        "paired_task_summary": paired_summary,
    }
    label_eval = {"summary": {"labels": 1}, "labels": {"hidden_semantic_edge_case": {"fn": 30}}}
    for name in (
        "aggregate.json",
        "aggregate.md",
        "runs.csv",
        "paired-task-deltas.csv",
        "paired-task-summary.csv",
        "labels.jsonl",
        "paper-report.json",
        "paper-report.md",
        "paper-report-labeled.md",
        "label-eval.md",
    ):
        run_dir.joinpath(name).write_text("{}\n", encoding="utf-8")
    run_dir.joinpath("paper-report-labeled.json").write_text(json.dumps(labeled_report) + "\n", encoding="utf-8")
    run_dir.joinpath("label-eval.json").write_text(json.dumps(label_eval) + "\n", encoding="utf-8")
    run_dir.joinpath("manual-labels.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in labels),
        encoding="utf-8",
    )

    report = build_report(selection_dir, run_dir)
    label_check = next(check for check in report["checks"] if check["name"] == "hard30 manual labels")
    markdown = render_report(report)

    assert report["ready"] is False
    assert label_check["missing_failure_labels"] == ["HARD-030/baseline"]
    assert "hard30 manual labels" in report["blocking"]
    assert "missing failure labels: HARD-030/baseline" in markdown


def test_audit_manual_labels_reports_quality_and_coverage(tmp_path):
    root = Path.cwd()
    manifest = tmp_path / "runs.jsonl"
    manifest.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in [
            {
                "task_id": "HARD-001",
                "prompt_type": "baseline",
                "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
                "outcome": "failure",
            },
            {
                "task_id": "HARD-001",
                "prompt_type": "intervention",
                "trace_path": str((root / "demo/healthy-codex-trace.jsonl").resolve()),
                "outcome": "success",
            },
            {
                "task_id": "HARD-002",
                "prompt_type": "baseline",
                "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
                "outcome": "failure",
            },
        ]),
        encoding="utf-8",
    )
    labels = tmp_path / "manual-labels.jsonl"
    labels.write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in [
            {
                "task_id": "HARD-001",
                "prompt_type": "baseline",
                "outcome": "failure",
                "failure_tags": ["verification_gap"],
                "notes": "No verification command after editing.",
            },
            {
                "task_id": "HARD-002",
                "prompt_type": "baseline",
                "outcome": "failure",
                "failure_tags": ["unknown_failure"],
                "notes": "",
            },
        ]),
        encoding="utf-8",
    )

    report = audit_manual_labels(manifest, labels)
    markdown = render_audit(report)

    assert report["ok"] is False
    assert report["failure_count"] == 2
    assert report["labeled_failure_count"] == 2
    assert report["missing_notes"] == ["HARD-002/baseline"]
    assert report["unknown_tags"] == ["unknown_failure"]
    assert report["tag_counts"] == {"verification_gap": 1}
    assert report["covered_process_tags"] == ["verification_gap"]
    assert "Ready: no" in markdown
    assert "| verification_gap | 1 |" in markdown


def test_audit_manual_labels_reports_missing_failure_rows(tmp_path):
    root = Path.cwd()
    manifest = tmp_path / "runs.jsonl"
    manifest.write_text(
        json.dumps({
            "task_id": "HARD-001",
            "prompt_type": "baseline",
            "trace_path": str((root / "demo/failing-codex-trace.jsonl").resolve()),
            "outcome": "failure",
        }) + "\n",
        encoding="utf-8",
    )
    labels = tmp_path / "manual-labels.jsonl"
    labels.write_text("", encoding="utf-8")

    report = audit_manual_labels(manifest, labels)

    assert report["ok"] is False
    assert report["missing_rows"] == ["HARD-001/baseline"]
    assert report["labeled_failure_count"] == 0


def test_aggregate_runs_baseline_vs_intervention():
    result = aggregate_runs("tests/fixtures/research/runs.jsonl")

    assert result["summary"]["baseline"]["n"] == 1
    assert result["summary"]["intervention"]["n"] == 1
    assert result["summary"]["baseline"]["success_rate"] == 0
    assert result["summary"]["intervention"]["success_rate"] == 1
    assert result["summary"]["baseline"]["avg_failure_score"] > result["summary"]["intervention"]["avg_failure_score"]
    assert result["deltas"]["success_rate"] == 1
    assert "avg_recover_events" in result["summary"]["baseline"]
    assert "retry_count" in result["runs"][0]
    assert "phase_verify_events" in result["runs"][0]


def test_evaluate_detector_labels():
    result = evaluate_detector_labels("benchmark/runs.example.jsonl", "benchmark/labels.example.jsonl")

    assert result["summary"]["micro_f1"] == 1
    assert result["labels"]["verification_gap"]["recall"] == 1
    assert result["labels"]["premature_completion"]["precision"] == 1


def test_generate_label_template_with_predictions():
    rows = generate_label_template("benchmark/runs.example.jsonl", include_predictions=True)
    baseline = rows[0]

    assert len(rows) == 4
    assert baseline["task_id"] == "CT-001"
    assert baseline["failure_tags"] == []
    assert "unrecovered_tool_error" in baseline["suggested_tags"]
    assert baseline["failure_score"] == 100
    assert render_label_template_jsonl(rows).count("\n") == 4


def test_build_paper_report_tables():
    result = build_paper_report("benchmark/runs.example.jsonl", "benchmark/labels.example.jsonl")
    markdown = render_paper_report_markdown(result)

    assert result["aggregate"]["summary"]["baseline"]["success_rate"] == 0
    assert "avg_turn_count" in result["aggregate"]["summary"]["baseline"]
    assert "avg_time_to_first_edit" in result["aggregate"]["summary"]["baseline"]
    assert "avg_time_to_first_test" in result["aggregate"]["summary"]["baseline"]
    assert result["detector_evaluation"]["summary"]["micro_f1"] == 1
    assert result["outcome_counts"]["failure"] == 2
    assert result["taxonomy_distribution"][0]["count"] == 2
    assert result["paired_task_deltas"][0]["task_id"] == "CT-001"
    assert result["paired_task_deltas"][0]["success_delta"] == 1
    assert result["paired_task_summary"]["success_delta"]["improved"] == 2
    assert result["paired_task_summary"]["token_usage_delta"]["improved"] == 1
    assert result["paired_task_summary"]["token_usage_delta"]["regressed"] == 1
    assert result["paired_task_summary"]["failure_score_delta"]["avg_delta"] == -100
    assert any(row["signal"] == "phase_recover_events" for row in result["signal_by_outcome"])
    assert any(row["failure_tag"] == "verification_gap" for row in result["signal_by_label"])
    assert any(row["signal"] == "failure_score" for row in result["signal_by_label"])
    assert "### Paired Task Deltas" in markdown
    assert "### Paired Task Summary" in markdown
    assert "## RQ4 Trace Signals By Outcome" in markdown
    assert "## RQ4 Trace Signals By Manual Label" in markdown
    assert "| avg_time_to_first_test |" in markdown
    assert "Outcome counts: failure=2, success=2, unknown=0." in markdown


def test_metric_coverage_audit_covers_experiment_design_metrics():
    result = build_metric_coverage_audit(Path("benchmark/runs.example.jsonl"))
    markdown = render_metric_coverage_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["manifest_count"] == 1
    assert result["summary"]["covered_metric_count"] == 11
    assert result["summary"]["prompt_summary_cell_count"] == 22
    assert result["summary"]["expected_prompt_summary_cell_count"] == 22
    assert result["summary"]["nullable_metric_count"] == 2
    assert len(result["nullable_metrics"]) == 2
    assert len(result["prompt_summary_metrics"]) == 22
    assert all(row["covered"] for row in result["metrics"])
    assert all(row["covered"] for row in result["prompt_summary_metrics"])
    assert "time_to_first_test" in markdown
    assert "avg_time_to_first_test" in markdown
    assert "## Prompt Summary Coverage" in markdown
    assert "| `benchmark/runs.example.jsonl` | `baseline` | 11 / 11 |" in markdown
    assert "| `benchmark/runs.example.jsonl` | `intervention` | 11 / 11 |" in markdown
    assert "## Nullable Metrics" in markdown
    assert "aggregate averages use present values only" in markdown

    default_result = build_metric_coverage_audit()
    default_markdown = render_metric_coverage_audit_markdown(default_result)

    assert default_result["summary"]["ready"] is True
    assert default_result["summary"]["manifest_count"] == 7
    assert default_result["summary"]["ready_manifest_count"] == 7
    assert default_result["summary"]["coverage_cell_count"] == 77
    assert default_result["summary"]["expected_coverage_cell_count"] == 77
    assert default_result["summary"]["prompt_summary_cell_count"] == 154
    assert default_result["summary"]["expected_prompt_summary_cell_count"] == 154
    assert default_result["summary"]["nullable_manifest_cells"] == 14
    assert default_result["summary"]["nullable_cells_with_observations"] == 14
    assert "Manifests checked: 7 / 7" in default_markdown
    assert "Prompt summary cells covered: 154 / 154" in default_markdown
    assert "| `benchmark/hard/pilot/hard30-real/runs.jsonl` | `baseline` | 11 / 11 |" in default_markdown
    assert "| `benchmark/hard/pilot/hard30-real/runs.jsonl` | `intervention` | 11 / 11 |" in default_markdown
    assert "Nullable metrics checked: 2" in default_markdown
    assert "benchmark/verification-ablation/pilot/full-real/runs.jsonl" in default_markdown


def test_paired_effects_audit_quantifies_rq3_waste_deltas():
    result = build_paired_effects_audit(bootstrap_samples=200)
    markdown = render_paired_effects_markdown(result)
    hard30 = {row["metric"]: row for row in result["metrics"] if row["study"] == "hard30"}

    assert result["summary"]["ready"] is True
    assert result["summary"]["study_count"] == 7
    assert result["summary"]["non_ablation_study_count"] == 6
    assert result["summary"]["non_ablation_repeated_improved"] == 6
    assert result["summary"]["non_ablation_token_improved"] == 6
    assert result["summary"]["non_ablation_verification_flat"] == 6
    assert result["summary"]["hard30_paired_tasks"] == 30
    studies = {row["study"]: row for row in result["studies"]}
    assert studies["hard30"]["role"] == "non_ablation_pilot"
    assert studies["hard30"]["success_check_verification_avg_delta"] == 0
    assert studies["verification_ablation"]["role"] == "auxiliary_ablation"
    claim_boundaries = {row["claim"]: row for row in result["claim_boundaries"]}
    assert claim_boundaries["Harness intervention reduces tool-call and token waste."]["verdict"] == "supported"
    assert claim_boundaries["Harness intervention improves hard30 success rate."]["verdict"] == "unsupported"
    assert claim_boundaries["Harness intervention improves success in at least one pilot slice."]["verdict"] == "pilot-qualified"
    assert claim_boundaries["Harness intervention improves ordinary-baseline verification rate."]["verdict"] == "unsupported"
    assert claim_boundaries["No-verify ablation shows harness control over verification behavior."]["verdict"] == "mechanism-check-only"
    assert hard30["repeated_tool_call_delta"]["avg_delta"] < 0
    assert hard30["repeated_tool_call_delta"]["ci_high"] < 0
    assert hard30["token_usage_delta"]["avg_delta"] < 0
    assert hard30["token_usage_delta"]["ci_high"] < 0
    assert hard30["verification_delta"]["avg_delta"] == 0
    assert "Non-ablation studies with lower repeated calls: 6 / 6" in markdown
    assert "Non-ablation studies with lower token usage: 6 / 6" in markdown
    assert "Non-ablation studies with flat broad and exact verification: 6 / 6" in markdown
    assert "Exact verification delta" in markdown
    assert "zero broad and exact visible-success-check verification deltas" in markdown
    assert "| verification_ablation | auxiliary_ablation |" in markdown
    assert "RQ3 Claim Boundary Verdicts" in markdown
    assert "Use as the primary RQ3 result and keep it task-paired" in markdown
    assert "Do not claim ordinary verification-rate lift; report verification saturation" in markdown
    assert "Use only as a mechanism check, not as ordinary-baseline evidence" in markdown
    assert "not population-level significance claims" in markdown


def test_paired_effect_limitations_audit_guards_population_overclaims():
    result = build_paired_effect_limitations_audit()
    markdown = render_paired_effect_limitations_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["passed"] == 13
    assert all(row["passed"] for row in result["checks"])
    assert "not population-level significance claims" in markdown
    assert "population-level significance claims out of the headline" in markdown


def test_demo_audit_runs_offline_reviewer_demo():
    result = build_demo_audit()
    markdown = render_demo_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_finding_count"] == 5
    assert result["summary"]["findings_with_event_ids"] == 5
    assert result["output_checks"]["json_report"] is True
    assert result["output_checks"]["markdown_report"] is True
    assert result["expected_findings"]["sandbox_or_permission_block"] is True
    assert "does not start the optional Web UI" in markdown


def test_web_artifact_audit_matches_demo_report_and_highlight_path():
    result = build_web_artifact_audit()
    markdown = render_web_artifact_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_findings"] == 5
    assert result["summary"]["report_checks"] == 5
    assert result["summary"]["source_checks"] == 9
    assert result["source_checks"]["fetch_report"] is True
    assert result["source_checks"]["highlighted_class"] is True
    assert result["source_checks"]["vite_build_script"] is True
    assert "does not install npm dependencies or start the Vite dev server" in markdown


def test_cli_surface_audit_covers_offline_entrypoints():
    result = build_cli_surface_audit()
    markdown = render_cli_surface_markdown(result)
    commands = {row["id"]: row for row in result["commands"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_command_count"] == 9
    assert result["summary"]["covered_subcommand_count"] == 9
    assert result["summary"]["covered_doc_check_count"] == 6
    assert commands["collect"]["covered"] is True
    assert commands["diagnose_json"]["covered"] is True
    assert commands["research_summary"]["covered"] is True
    assert commands["research_run_dry"]["covered"] is True
    assert "does not execute live Codex collection" in markdown


def test_ci_surface_audit_covers_ci_packaging_and_readiness_gate():
    result = build_ci_surface_audit()
    markdown = render_ci_surface_markdown(result)
    ci_checks = {row["id"]: row for row in result["ci_checks"]}
    packaging_checks = {row["id"]: row for row in result["packaging_checks"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_ci_check_count"] == 10
    assert result["summary"]["covered_packaging_check_count"] == 6
    assert result["summary"]["covered_make_check_count"] == 3
    assert ci_checks["submission_readiness"]["present"] is True
    assert ci_checks["web_build"]["present"] is True
    assert packaging_checks["console_script"]["present"] is True
    assert "does not execute GitHub Actions itself" in markdown


def test_benchmark_trace_artifact_audit_covers_hard30_pairs_and_traces():
    result = build_benchmark_trace_artifact_audit()
    markdown = render_benchmark_trace_artifact_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["task_count"] == 30
    assert result["summary"]["unique_task_count"] == 30
    assert result["summary"]["run_count"] == 60
    assert result["summary"]["paired_task_count"] == 30
    assert result["summary"]["trace_count"] == 60
    assert result["summary"]["nonempty_trace_count"] == 60
    assert result["summary"]["parseable_trace_count"] == 60
    assert result["summary"]["diagnosed_trace_count"] == 60
    assert result["summary"]["trace_sidecar_count"] == 60
    assert result["summary"]["manifest_provenance_field_count"] == 600
    assert result["summary"]["manifest_provenance_field_expected_count"] == 600
    assert result["summary"]["manifest_prompt_path_count"] == 60
    assert result["summary"]["success_check_recorded_count"] == 60
    assert result["summary"]["codex_exit_code_recorded_count"] == 60
    assert result["summary"]["manifest_grader_path_count"] == 0
    assert result["summary"]["manifest_workdir_count"] == 0
    assert result["summary"]["label_count"] == 60
    assert result["summary"]["outcome_rows_with_grader_count"] == 60
    assert result["summary"]["prompt_type_balance_ready"] is True
    prompt_balance = {row["prompt_type"]: row for row in result["prompt_type_balance"]}
    assert prompt_balance["baseline"]["run_rows"] == 30
    assert prompt_balance["baseline"]["nonempty_traces"] == 30
    assert prompt_balance["baseline"]["parseable_traces"] == 30
    assert prompt_balance["baseline"]["outcome_rows"] == 30
    assert prompt_balance["baseline"]["label_rows"] == 30
    assert prompt_balance["baseline"]["balanced"] is True
    assert prompt_balance["intervention"]["run_rows"] == 30
    assert prompt_balance["intervention"]["nonempty_traces"] == 30
    assert prompt_balance["intervention"]["parseable_traces"] == 30
    assert prompt_balance["intervention"]["outcome_rows"] == 30
    assert prompt_balance["intervention"]["label_rows"] == 30
    assert prompt_balance["intervention"]["balanced"] is True
    assert result["missing_run_keys"] == []
    assert result["missing_label_keys"] == []
    assert result["summary"]["trace_event_lines"] > 0
    assert result["summary"]["parsed_trace_events"] > 0
    assert "Parseable traces: 60 / 60" in markdown
    assert "Trace sidecar bundles: 60 / 60" in markdown
    assert "Run Manifest Provenance" in markdown
    assert "Run manifest provenance fields: 600 / 600" in markdown
    assert "| `grader_path` | 60 | 0 | hidden-grader path reference; grader directory is not committed |" in markdown
    assert "Prompt-type balance ready: yes" in markdown
    assert "| `baseline` | 30 | 30 | 30 | 30 | 30 | yes |" in markdown
    assert "| `intervention` | 30 | 30 | 30 | 30 | 30 | yes |" in markdown
    assert "does not rerun Codex or hidden graders" in markdown


def test_artifact_guide_sequence_audit_checks_reviewer_path_numbering(tmp_path):
    result = build_artifact_guide_sequence_audit()
    markdown = render_artifact_guide_sequence_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["step_count"] == 10
    assert result["summary"]["first_step"] == 1
    assert result["summary"]["last_step"] == 10
    assert result["summary"]["missing_numbers"] == []
    assert result["summary"]["duplicate_numbers"] == []
    assert result["summary"]["missing_phrases"] == []
    assert "docs/paired_effect_limitations_audit.md" in markdown
    assert "docs/detector_evaluation_audit.md" in markdown
    assert "docs/rq4_signal_audit.md" in markdown
    assert "failure-taxonomy coverage and evidence tiers" in markdown
    assert "RQ1 Distribution Boundary" in markdown
    assert "RQ3 Claim Boundary Verdicts" in markdown
    assert "RQ4 Signal Verdicts" in markdown

    broken = tmp_path / "artifact_guide.md"
    broken.write_text(
        "## Fifteen-Minute Core Path\n\n1. First\n1. Duplicate\n3. Third\n\n## Extended Evidence Path\n",
        encoding="utf-8",
    )
    failing = build_artifact_guide_sequence_audit(broken)

    assert failing["summary"]["ready"] is False
    assert failing["summary"]["duplicate_numbers"] == [1]
    assert failing["summary"]["missing_numbers"] == [2]
    assert "failure-taxonomy coverage and evidence tiers" in failing["summary"]["missing_phrases"]


def test_label_provenance_audit_covers_hard30_label_files_and_eval_outputs():
    result = build_label_provenance_audit()
    markdown = render_label_provenance_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["run_count"] == 60
    assert result["summary"]["template_label_count"] == 60
    assert result["summary"]["manual_label_count"] == 60
    assert result["summary"]["labeled_failure_count"] == 30
    assert result["summary"]["failure_note_count"] == 30
    assert result["summary"]["covered_field_count"] == 8
    assert result["summary"]["eval_summary_match_count"] == 5
    assert result["summary"]["eval_labels_match"] is True
    assert result["tag_counts"]["hidden_semantic_edge_case"] == 30
    assert result["tag_counts"]["repetitive_exploration"] == 4
    assert "does not prove inter-annotator agreement" in markdown


def test_label_limitations_audit_connects_provenance_to_paper_limits():
    result = build_label_limitations_audit()
    markdown = render_label_limitations_markdown(result)
    checks = {row["id"]: row for row in result["checks"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["passed"] == 8
    assert result["summary"]["checks"] == 8
    assert checks["single_artifact_caveat"]["passed"] is True
    assert checks["no_inter_annotator_claim"]["passed"] is True
    assert checks["provenance_inter_annotator_caveat"]["passed"] is True
    assert "single-artifact manual diagnostic labels" in markdown


def test_method_pipeline_audit_maps_paper_pipeline_to_code_and_cli_smoke():
    result = build_method_pipeline_audit()
    markdown = render_method_pipeline_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_stage_count"] == 7
    assert result["summary"]["covered_cli_check_count"] == 4
    assert result["summary"]["covered_smoke_check_count"] == 6
    assert result["summary"]["smoke_diagnosis_finding_count"] == 5
    assert result["summary"]["smoke_diagnosis_findings_with_event_ids"] == 5
    assert result["summary"]["smoke_aggregate_run_count"] == 4
    assert result["smoke"]["metrics"]["aggregate_prompt_types"] == ["baseline", "intervention"]
    assert {row["id"] for row in result["stages"]} == {
        "codex_jsonl_trace_input",
        "jsonl_event_parser",
        "normalized_trace_schema",
        "phase_segmentation",
        "failure_pattern_detector",
        "diagnosis_report",
        "baseline_vs_intervention_comparison",
    }
    assert all(row["covered"] for row in result["stages"])
    assert all(row["covered"] for row in result["smoke"]["checks"])
    assert "demo/real-codex-run.jsonl" in markdown
    assert "## Smoke Metrics" in markdown
    assert "Diagnosis findings: 5" in markdown
    assert "Findings with event IDs: 5 / 5" in markdown
    assert "Aggregate run rows: 4" in markdown
    assert "does not execute live Codex collection" in markdown


def test_schema_field_audit_maps_paper_schema_to_code():
    result = build_schema_field_audit()
    markdown = render_schema_field_audit_markdown(result)
    step_fields = {row["field"]: row for row in result["step_fields"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["objective_schema_fields_covered"] == 15
    assert result["summary"]["run_fields_covered"] == 4
    assert result["summary"]["step_fields_covered"] == 11
    assert step_fields["Step.timestamp"]["scope"] == "direct"
    assert step_fields["Step.tool_name"]["scope"] == "representational"
    assert step_fields["Step.token_usage"]["scope"] == "trace_level"
    assert step_fields["Step.failure_tags"]["scope"] == "derived"
    assert step_fields["Step.token_usage"]["boundary"] == "run/trace-level aggregate, not always a per-step field"
    assert "Objective schema fields checked: 15 / 15" in markdown
    assert "not all objective fields are direct `TraceEvent` attributes" in markdown
    assert "`Run.task_id`" in markdown
    assert "`Step.file_paths`" in markdown
    assert "schema mapping is representational" in markdown


def test_parser_event_coverage_audit_covers_parser_variants():
    result = build_parser_event_coverage_audit()
    markdown = render_parser_event_coverage_markdown(result)
    kinds = {row["kind"]: row for row in result["kinds"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_kind_count"] == 11
    assert result["summary"]["covered_phase_count"] == 7
    assert result["summary"]["covered_source_marker_count"] == 11
    assert kinds["mcp_tool"]["present"] is True
    assert kinds["unknown"]["event_count"] == 2
    assert result["feature_checks"]["usage_input_tokens"] is True
    assert result["feature_checks"]["file_paths"] is True
    assert "does not claim compatibility with every future Codex JSONL variant" in markdown


def test_failure_node_traceability_audit_covers_report_and_ui_path():
    result = build_failure_node_traceability_audit()
    markdown = render_failure_node_traceability_markdown(result)
    finding_rows = {row["code"]: row for row in result["findings"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["expected_demo_findings_present"] == 5
    assert result["summary"]["findings_with_event_ids"] == 5
    assert result["summary"]["json_event_id_findings"] == 5
    assert result["summary"]["markdown_event_id_lines"] == 5
    assert result["summary"]["benchmark_traces_checked"] == 60
    assert result["summary"]["benchmark_finding_count"] == 4
    assert result["summary"]["benchmark_findings_with_event_ids"] == 4
    assert result["summary"]["benchmark_missing_event_id_findings"] == 0
    assert result["source_checks"]["web_highlight_class"] is True
    assert result["benchmark_finding_counts"]["repeated_search_or_read"] == 4
    assert finding_rows["repeated_search_or_read"]["event_id_count"] == 2
    assert "Benchmark findings with event IDs: 4 / 4" in markdown
    assert "does not claim that hidden semantic failures have visible failure nodes" in markdown


def test_failure_taxonomy_audit_covers_process_labels():
    result = build_failure_taxonomy_audit()
    markdown = render_failure_taxonomy_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_label_count"] == 6
    assert result["summary"]["fixture_micro_f1"] == 1
    assert result["summary"]["real_pilot_positive_label_count"] == 2
    assert result["summary"]["ablation_positive_label_count"] == 2
    assert result["summary"]["fixture_only_label_count"] == 2
    assert result["summary"]["hidden_semantic_hard30_fn"] == 30
    assert {row["label"] for row in result["labels"]} == {
        "verification_gap",
        "unrecovered_tool_error",
        "repetitive_exploration",
        "context_drift",
        "premature_completion",
        "sandbox_permission_deadlock",
    }
    assert all(row["covered"] for row in result["labels"])
    tiers = {row["label"]: row["evidence_tier"] for row in result["labels"]}
    assert tiers["repetitive_exploration"] == "real-pilot-positive"
    assert tiers["sandbox_permission_deadlock"] == "real-pilot-positive"
    assert tiers["verification_gap"] == "ablation-positive"
    assert tiers["premature_completion"] == "ablation-positive"
    assert tiers["unrecovered_tool_error"] == "fixture-only"
    assert tiers["context_drift"] == "fixture-only"
    plan = {row["label"]: row for row in result["natural_coverage_plan"]}
    assert set(plan) == {"verification_gap", "unrecovered_tool_error", "context_drift", "premature_completion"}
    assert all(row["natural_positive_target"] == 2 for row in plan.values())
    assert "do not count controlled fixtures or no-verify ablation rows" in plan["verification_gap"]["acceptance_gate"]
    rq1_boundaries = {row["claim"]: row for row in result["rq1_boundaries"]}
    assert rq1_boundaries["CodexTrace defines the six target observable process-failure modes."]["verdict"] == "supported"
    assert rq1_boundaries["Current real pilots naturally expose all six process-failure modes."]["verdict"] == "unsupported"
    assert rq1_boundaries["Some target process modes are only visible in ablation or controlled traces so far."]["verdict"] == "boundary"
    assert rq1_boundaries["Hard30 outcome failures reveal an additional hidden-semantic boundary."]["verdict"] == "supported-boundary"
    assert "Fixture-only labels: 2 / 6" in markdown
    assert "RQ1 Distribution Boundary" in markdown
    assert "Natural Coverage Closure Plan" in markdown
    assert "Natural-positive target" in markdown
    assert "do not count controlled fixtures or no-verify ablation rows" in markdown
    assert "Report evidence tiers rather than claiming natural-frequency coverage for every label" in markdown
    assert "Describe hidden semantic failures separately from observable process-failure taxonomy" in markdown
    assert "rule-level taxonomy coverage" in markdown


def test_phase_coverage_audit_covers_schema_rows_and_rq4_signals():
    result = build_phase_coverage_audit()
    markdown = render_phase_coverage_markdown(result)
    phases = {row["phase"]: row for row in result["phases"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_phase_count"] == 7
    assert result["summary"]["phase_count"] == 7
    assert result["summary"]["rq4_core_signal_count"] == 4
    assert phases["setup"]["covered"] is True
    assert phases["inspect"]["rq4_signal"] is True
    assert phases["edit"]["rq4_signal"] is True
    assert phases["verify"]["rq4_signal"] is True
    assert phases["recover"]["rq4_signal"] is True
    assert phases["complete"]["run_level"] is True
    assert phases["other"]["run_level"] is True
    assert "Phases covered: 7 / 7" in markdown
    assert "RQ4 core phase signals: 4 / 4" in markdown


def test_task_category_coverage_audit_covers_experiment_design_categories():
    result = build_task_category_coverage_audit()
    markdown = render_task_category_coverage_markdown(result)
    rows = {row["category"]: row for row in result["required_categories"]}
    exemplars = {row["category"]: row for row in result["exemplars"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["seed_required_categories_covered"] == 7
    assert result["summary"]["hard_required_categories_covered"] == 6
    assert result["summary"]["hard_missing_required_categories"] == ["test_writing"]
    assert result["summary"]["hard_family_categories_covered"] == 6
    assert result["summary"]["hard_family_missing_required_categories"] == ["test_writing"]
    assert result["summary"]["hard30_family_categories_covered"] == 6
    assert result["summary"]["hard30_family_missing_required_categories"] == ["test_writing"]
    assert result["summary"]["required_design_categories"] == 7
    assert result["summary"]["design_task_count_min"] == 30
    assert result["summary"]["design_task_count_max"] == 50
    assert result["summary"]["seed_task_count"] == 30
    assert result["summary"]["hard_task_count"] == 50
    assert result["summary"]["hard30_task_count"] == 30
    assert result["summary"]["seed_in_design_window"] is True
    assert result["summary"]["hard_in_design_window"] is True
    assert result["summary"]["hard30_in_design_window"] is True
    assert rows["bug_fix"]["seed_count"] == 5
    assert rows["bug_fix"]["hard_family_count"] == 15
    assert rows["test_writing"]["seed_count"] == 5
    assert rows["multi_turn_change"]["seed_count"] == 3
    assert rows["test_writing"]["hard30_count"] == 0
    assert rows["test_writing"]["hard30_family_count"] == 0
    assert len(result["exemplars"]) == 7
    assert exemplars["bug_fix"]["seed_task_id"] == "CT-001"
    assert exemplars["ci_failure"]["hard30_task_id"] == "HARD-015"
    assert exemplars["ci_failure"]["hard30_public_success_check"] == "npm run build"
    assert exemplars["test_writing"]["hard30_task_id"] == "-"
    assert "Seed design categories covered: 7 / 7" in markdown
    assert "Design task-count window: 30-50" in markdown
    assert "Seed tasks in design window: yes" in markdown
    assert "Hard tasks in design window: yes" in markdown
    assert "Hard30 selected tasks in design window: yes" in markdown
    assert "## Category Exemplars" in markdown
    assert "`CT-001` / `python/toy_calc`" in markdown
    assert "`HARD-015` / `typescript/package_exports` (ci_failure)" in markdown
    assert "boundary: none" in markdown
    assert "Hard pool missing design categories: `test_writing`" in markdown
    assert "Hard Category Family Mapping" in markdown
    assert "missing direct or family-level design categories such as `test_writing`" in markdown
    assert "not required to preserve every seed category one-for-one" in markdown


def test_harness_protocol_audit_covers_intervention_constraints():
    result = build_harness_protocol_audit()
    markdown = render_harness_protocol_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_prompt_count"] == 4
    assert result["summary"]["prompt_count"] == 4
    assert result["summary"]["rule_count"] == 5
    assert result["summary"]["protocol_rule_count"] == 5
    assert result["summary"]["run_proxy_passed"] == 6
    assert result["summary"]["run_proxy_count"] == 6
    assert all(prompt["covered"] for prompt in result["prompts"])
    proxies = {row["id"]: row for row in result["run_proxy_checks"]}
    assert proxies["post_edit_verification_proxy"]["intervention"] == 1
    assert proxies["minimal_edit_proxy"]["delta"] < 0
    assert proxies["token_waste_proxy"]["delta"] < 0
    assert {row["id"] for row in result["protocol_rules"]} == {
        "inspect_first",
        "minimal_edit",
        "post_edit_verification",
        "failure_diagnosis_before_retry",
        "finish_with_evidence",
    }
    assert "Intervention prompts covered: 4 / 4" in markdown
    assert "Run-level proxy checks passed: 6 / 6" in markdown
    assert "Run-Level Proxy Checks" in markdown
    assert "`token_waste_proxy`" in markdown
    assert "does not prove that every model run obeyed each instruction" in markdown


def test_related_work_audit_covers_positioning_axes():
    result = build_related_work_audit()
    markdown = render_related_work_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_topic_count"] == 8
    assert {row["topic"] for row in result["topics"]} == {
        "software_engineering_benchmarks",
        "multi_turn_degradation",
        "coding_agents_and_interfaces",
        "tool_use_agents_and_feedback",
        "general_agent_evaluation",
        "program_repair_waste",
        "trace_based_agent_diagnosis",
        "codextrace_positioning",
    }
    assert all(row["covered"] for row in result["topics"])
    assert "not a full literature review" in markdown


def test_paper_structure_audit_covers_required_sections():
    result = build_paper_structure_audit()
    markdown = render_paper_structure_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_section_count"] == 11
    assert {row["id"] for row in result["sections"]} >= {
        "title_and_abstract",
        "introduction_and_rqs",
        "method_and_schema",
        "benchmark_and_measurement",
        "rq_results",
        "boundary_result_framing",
        "analysis_and_limitations",
        "artifact_and_conclusion",
        "references",
    }
    assert all(row["covered"] for row in result["sections"])
    assert "does not judge prose quality" in markdown


def test_reproducibility_audit_covers_key_commands():
    result = build_reproducibility_audit()
    markdown = render_reproducibility_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_command_count"] == 54
    assert result["summary"]["covered_semantic_phrase_count"] == 3
    assert result["summary"]["fences_balanced"] is True
    assert {row["id"] for row in result["commands"]} >= {
        "full30_aggregate",
        "controlled_fixture_eval",
        "detector_evaluation_audit",
        "rule_implementation_audit",
        "paired_effects_audit",
        "paired_effect_limitations_audit",
        "demo_audit",
        "web_artifact_audit",
        "cli_surface_audit",
        "ci_surface_audit",
        "benchmark_trace_artifact",
        "label_provenance_audit",
        "label_limitations_audit",
        "verification_saturation_audit",
        "verification_behavior_audit",
        "schema_field_audit",
        "parser_event_coverage",
        "failure_node_traceability",
        "phase_coverage_audit",
        "task_category_coverage_audit",
        "harness_protocol_audit",
        "bibliography_audit",
        "paper_abstract_audit",
        "paper_contribution_audit",
        "paper_conclusion_audit",
        "method_pipeline_audit",
        "rq_table_consistency_audit",
        "hard30_paper_report",
        "combined_summary",
        "headline_results",
        "verification_ablation_plan",
        "thesis_revision_decision",
        "validity_threats",
        "limitations_traceability_audit",
        "expected_results_reconciliation",
        "submission_readiness_plan_audit",
        "artifact_guide_sequence_audit",
        "submission_readiness_gate",
        "claim_text_guard",
    }
    assert all(row["present"] for row in result["commands"])
    assert all(row["present"] for row in result["semantic_phrases"])
    assert "Commands covered: 54 / 54" in markdown
    assert "Semantic phrases covered: 3 / 3" in markdown
    assert "nullable_timing_metrics" in markdown
    assert "task_design_family_mapping" in markdown
    assert "does not execute the full real Codex collection commands" in markdown


def test_rq_table_consistency_audit_guards_paper_result_tables():
    result = build_rq_table_consistency_audit()
    markdown = render_rq_table_consistency_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_check_count"] == 10
    assert result["summary"]["check_count"] == 10
    assert {row["rq"] for row in result["checks"]} == {"RQ1", "RQ2", "RQ3", "RQ4"}
    assert all(row["covered"] for row in result["checks"])
    assert "does not add new statistical evidence" in markdown


def test_rule_implementation_audit_maps_taxonomy_to_diagnosis_rules():
    result = build_rule_implementation_audit()
    markdown = render_rule_implementation_markdown(result)
    rules = {row["label"]: row for row in result["rules"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_rule_count"] == 6
    assert result["summary"]["context_proxy_disclosed"] is True
    assert result["summary"]["real_pilot_positive_rule_count"] == 2
    assert result["summary"]["ablation_positive_rule_count"] == 2
    assert result["summary"]["fixture_only_rule_count"] == 2
    assert rules["verification_gap"]["finding_code"] == "verification_gap"
    assert rules["verification_gap"]["evidence_tier"] == "ablation-positive"
    assert "post-edit file changes" in rules["verification_gap"]["detector_signal"]
    assert rules["unrecovered_tool_error"]["finding_code"] == "command_failure_unhandled"
    assert rules["unrecovered_tool_error"]["evidence_tier"] == "fixture-only"
    assert "failed commands" in rules["unrecovered_tool_error"]["detector_signal"]
    assert rules["repetitive_exploration"]["evidence_tier"] == "real-pilot-positive"
    assert "repeated search/read commands" in rules["repetitive_exploration"]["detector_signal"]
    assert rules["context_drift"]["finding_code"] == "long_context_no_progress"
    assert rules["context_drift"]["scope"] == "v1_proxy"
    assert "high context growth" in rules["context_drift"]["detector_signal"]
    assert "sandbox, permission, network" in rules["sandbox_permission_deadlock"]["detector_signal"]
    assert all(row["covered"] for row in result["rules"])
    assert "Rules covered: 6 / 6" in markdown
    assert "Detector signal" in markdown
    assert "post-edit file changes without later test/build/lint verification" in markdown
    assert "failed commands without a later similar recovery command or verification" in markdown
    assert "high context growth with weak edit or verification progress" in markdown
    assert "Real-pilot-positive rules: 2 / 6" in markdown
    assert "`fixture-only`" in markdown
    assert "not a full semantic task-keyword drift detector" in markdown


def test_detector_evaluation_audit_consolidates_rq2_evidence():
    result = build_detector_evaluation_audit()
    markdown = render_detector_evaluation_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["controlled_label_count"] == 6
    assert result["summary"]["controlled_micro_f1"] == 1
    assert result["summary"]["hard30_repetitive_tp"] == 4
    assert result["summary"]["full30_sandbox_tp"] == 1
    assert result["summary"]["ablation_verification_gap_tp"] == 4
    assert result["summary"]["ablation_premature_completion_tp"] == 3
    assert result["summary"]["hidden_semantic_fn_total"] == 36
    assert result["summary"]["real_pilot_positive_label_count"] == 2
    assert result["summary"]["ablation_positive_label_count"] == 2
    assert result["summary"]["fixture_only_label_count"] == 2
    assert result["summary"]["mechanism_row_count"] == 6
    claim_boundaries = {row["claim"]: row for row in result["claim_boundaries"]}
    assert claim_boundaries["Rules cover the six process-failure labels on controlled traces."]["verdict"] == "supported"
    assert claim_boundaries["Rules detect observed process-positive slices in real or ablation pilots."]["verdict"] == "supported-with-boundary"
    assert claim_boundaries["Rules detect most real-world outcome failures."]["verdict"] == "unsupported"
    assert claim_boundaries["Rules detect hidden semantic correctness failures."]["verdict"] == "contradicted"
    tiers = {row["label"]: row["evidence_tier"] for row in result["process_label_evidence_tiers"]}
    assert tiers["repetitive_exploration"] == "real-pilot-positive"
    assert tiers["sandbox_permission_deadlock"] == "real-pilot-positive"
    assert tiers["verification_gap"] == "ablation-positive"
    assert tiers["unrecovered_tool_error"] == "fixture-only"
    mechanisms = {row["label"]: row for row in result["process_rule_mechanisms"]}
    assert mechanisms["context_drift"]["finding_code"] == "long_context_no_progress"
    assert mechanisms["context_drift"]["boundary_note"] == "V1 proxy; not a semantic task-keyword drift detector."
    assert mechanisms["sandbox_permission_deadlock"]["trace_signal"] == "sandbox, permission, network, or access-denied tool errors"
    assert "Controlled process labels covered: 6 / 6" in markdown
    assert "Hidden semantic false negatives: 36" in markdown
    assert "Evidence Tier By Process Label" in markdown
    assert "Process Rule Mechanism Map" in markdown
    assert "V1 proxy; not a semantic task-keyword drift detector." in markdown
    assert "Claim Boundary Verdicts" in markdown
    assert "Do not claim majority real-world failure detection" in markdown
    assert "State that hidden semantic failures require stronger task oracles or semantic checks" in markdown
    assert "| `context_drift` | yes | 0 | 0 | `fixture-only` |" in markdown
    assert "do not detect hidden semantic correctness failures" in markdown


def test_build_results_summary_from_stored_pilots():
    result = build_results_summary(
        "benchmark/pilot/full30-real/runs.jsonl",
        "benchmark/pilot/full30-real/process-labels.jsonl",
        "benchmark/detector-fixtures/runs.jsonl",
        "benchmark/detector-fixtures/labels.jsonl",
        "benchmark/hard/pilot/hard10-real/runs.jsonl",
        "benchmark/hard/pilot/hard10-real/manual-labels.jsonl",
        "benchmark/hard/pilot/hard30-real/runs.jsonl",
        "benchmark/hard/pilot/hard30-real/manual-labels.jsonl",
        "benchmark/process-stress/pilot/full-real/runs.jsonl",
        "benchmark/process-stress/pilot/full-real/manual-labels.jsonl",
        "benchmark/verification-lift/pilot/full-real/runs.jsonl",
        "benchmark/verification-lift/pilot/full-real/manual-labels.jsonl",
        "benchmark/verification-lift-v2/pilot/full-real/runs.jsonl",
        "benchmark/verification-ablation/pilot/full-real/runs.jsonl",
        "benchmark/verification-ablation/pilot/full-real/manual-labels.jsonl",
    )
    markdown = render_results_summary_markdown(result)

    assert result["full30"]["summary"]["baseline"]["n"] == 30
    assert result["full30_process_label_evaluation"]["labels"]["sandbox_permission_deadlock"]["tp"] == 1
    assert result["detector_fixture_label_evaluation"]["summary"]["micro_f1"] == 1
    assert set(result["detector_fixture_label_evaluation"]["labels"]) >= {
        "verification_gap",
        "unrecovered_tool_error",
        "repetitive_exploration",
        "context_drift",
        "premature_completion",
        "sandbox_permission_deadlock",
    }
    assert result["hard10"]["summary"]["baseline"]["success_rate"] == 0.7
    assert result["hard30"]["summary"]["baseline"]["n"] == 30
    assert result["hard30"]["summary"]["baseline"]["success_rate"] == 0.5
    assert "avg_turn_count" in result["hard30"]["summary"]["baseline"]
    assert "avg_time_to_first_edit" in result["hard30"]["summary"]["baseline"]
    assert "avg_time_to_first_test" in result["hard30"]["summary"]["baseline"]
    assert result["hard10_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 5
    assert result["hard30_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 30
    assert result["hard30_label_evaluation"]["labels"]["repetitive_exploration"]["tp"] == 4
    assert result["process_stress"]["summary"]["baseline"]["n"] == 12
    assert result["process_stress"]["summary"]["baseline"]["success_rate"] == 0.9167
    assert result["process_stress"]["deltas"]["success_check_verification_rate"] == 0
    assert result["process_stress_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 2
    assert result["verification_lift"]["summary"]["baseline"]["n"] == 8
    assert result["verification_lift"]["summary"]["baseline"]["verification_rate"] == 1
    assert result["verification_lift"]["deltas"]["success_check_verification_rate"] == 0
    assert result["verification_lift_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 2
    assert result["verification_lift_v2"]["summary"]["baseline"]["n"] == 8
    assert result["verification_lift_v2"]["summary"]["baseline"]["verification_rate"] == 1
    assert result["verification_lift_v2"]["deltas"]["success_check_verification_rate"] == 0
    assert result["verification_lift_v2"]["summary"]["baseline"]["avg_repeated_tool_calls"] > result["verification_lift_v2"]["summary"]["intervention"]["avg_repeated_tool_calls"]
    assert result["verification_lift_v2"]["summary"]["baseline"]["avg_token_usage"] > result["verification_lift_v2"]["summary"]["intervention"]["avg_token_usage"]
    assert result["verification_ablation"]["summary"]["baseline"]["n"] == 4
    assert result["verification_ablation"]["deltas"]["verification_rate"] == 1
    assert result["verification_ablation"]["deltas"]["success_check_verification_rate"] == 1
    assert result["verification_ablation_label_evaluation"]["labels"]["verification_gap"]["tp"] == 4
    assert result["verification_ablation_label_evaluation"]["labels"]["premature_completion"]["tp"] == 3
    assert "## RQ3 Baseline vs Intervention" in markdown
    assert "### Headline Result Snapshot" in markdown
    assert "| hard30 waste | 12.93 repeated calls / 355.0k tokens | 9.2 repeated calls / 256.3k tokens |" in markdown
    assert "| verification-lift stress | 1.00 broad / 1.00 exact | 1.00 broad / 1.00 exact |" in markdown
    assert "| verification-lift-v2 ordinary retest | 1.00 broad / 1.00 exact | 1.00 broad / 1.00 exact |" in markdown
    assert "| no-verify ablation | 0.00 broad / 0.00 exact | 1.00 broad / 1.00 exact |" in markdown
    assert "### Hard30 Pilot" in markdown
    assert "| unresolved_error_rate | 0.00 | 0.00 | 0.00 |" in markdown
    assert "| avg_time_to_first_test |" in markdown
    assert "### Process-Stress Pilot" in markdown
    assert "### Verification-Lift Pilot" in markdown
    assert "### Verification-Lift-V2 Pilot" in markdown
    assert "### Verification Ablation Pilot" in markdown
    assert "### Full30 Process-Positive Detector Check" in markdown
    assert "### Controlled Detector Fixture Check" in markdown
    assert "## RQ4 Trace Signals By Outcome" in markdown
    assert "| failure_score | 1.833 | 2.833 | 1 |" in markdown
    assert "hidden_semantic_edge_case" in markdown
    assert "repetitive_exploration" in markdown
    assert "30 false negatives" in markdown
    assert "2 trace-only false negatives" in markdown
    assert "verification-lift-v2 verification remains 100% -> 100%" in markdown


def test_headline_results_table_tracks_actual_evidence_boundaries():
    result = build_headline_results()
    markdown = render_headline_results_markdown(result)
    rows = {row["id"]: row for row in result["rows"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["ordinary_verification_rate_lift_supported"] is False
    assert result["summary"]["waste_reduction_supported"] is True
    assert rows["hard30_success"]["baseline"] == 0.5
    assert rows["hard30_success"]["intervention"] == 0.5
    assert rows["hard30_repeated_tool_calls"]["baseline"] == 12.9333
    assert rows["hard30_repeated_tool_calls"]["intervention"] == 9.2
    assert rows["hard30_token_usage"]["baseline"] == 354971.1
    assert rows["hard30_token_usage"]["intervention"] == 256314.3333
    assert rows["verification_lift_v2_verification"]["delta"] == 0
    assert rows["verification_lift_v2_exact_verification"]["delta"] == 0
    assert rows["no_verify_ablation_verification"]["delta"] == 1
    assert rows["no_verify_ablation_exact_verification"]["delta"] == 1
    assert "Ordinary verification-rate lift supported: no" in markdown
    assert "no_verify_ablation_verification" in markdown
    assert "not an ordinary baseline" in markdown


def test_thesis_revision_decision_records_boundary_result_reframe():
    result = build_thesis_revision_decision()
    markdown = render_thesis_revision_decision_markdown(result)
    decisions = {row["id"]: row for row in result["decisions"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["decision"] == "revise_to_boundary_result_paper"
    assert result["summary"]["ready_for_original_thesis"] is False
    assert result["summary"]["ready_for_boundary_result_paper"] is True
    assert result["summary"]["claim_revision_required"] is True
    assert result["summary"]["additional_ordinary_baseline_experiment_required"] is False
    assert result["summary"]["ordinary_verification_rate_lift_supported"] is False
    assert result["summary"]["verification_headroom_baseline_runs"] == 98
    assert result["summary"]["verification_headroom_empirical_rate"] == 0
    assert result["summary"]["ordinary_expansion_can_close_verification_claim"] is False
    assert decisions["verification_rate_lift"]["decision"] == "drop_as_finding"
    assert "Headroom audit: 98 non-ablation baseline run(s)" in decisions["verification_rate_lift"]["evidence"]
    assert "same-style ordinary expansion can close claim=no" in decisions["verification_rate_lift"]["evidence"]
    assert decisions["no_verify_ablation"]["decision"] == "keep_as_mechanism_check"
    assert decisions["waste_reduction"]["decision"] == "keep"
    assert decisions["success_lift"]["decision"] == "qualify"
    assert "Decision: revise_to_boundary_result_paper" in markdown
    assert "Ordinary verification-rate lift supported: no" in markdown
    assert "Headroom audit: 98 non-ablation baseline run(s)" in markdown
    assert "same-style ordinary expansion can close claim=no" in markdown
    assert "drops the ordinary verification-rate-lift finding" in markdown


def test_validity_threats_audit_maps_boundary_paper_limits():
    result = build_validity_threats_audit()
    markdown = render_validity_threats_markdown(result)
    threats = {row["id"]: row for row in result["threats"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_count"] == 7
    assert result["summary"]["required_count"] == 7
    assert result["summary"]["boundary_decision"] == "revise_to_boundary_result_paper"
    assert result["summary"]["ordinary_verification_rate_lift_supported"] is False
    assert threats["construct_validity"]["paper_language"] == "Verification-rate lift is a negative boundary result, not a supported headline claim."
    assert threats["detector_validity"]["paper_language"] == "Detector results are boundary results for observable process failures; hidden semantic recall is 0.00 with FN=30."
    assert threats["ablation_validity"]["paper_language"] == "No-verify ablation is not ordinary-baseline evidence."
    assert threats["external_validity"]["paper_language"] == "Results are pilot-scale and Codex-CLI-specific."
    assert "Threats covered: 7 / 7" in markdown
    assert "internal_validity" in markdown
    assert "construct_validity" in markdown
    assert "conclusion_validity" in markdown
    assert "hidden semantic recall is 0.00 with FN=30" in markdown


def test_limitations_traceability_audit_maps_validity_threats_into_paper():
    result = build_limitations_traceability_audit()
    markdown = render_limitations_traceability_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["covered_threat_count"] == 7
    assert result["summary"]["threat_count"] == 7
    assert any(
        row["id"] == "detector_validity" and row["paper_language_present"]
        for row in result["threats"]
    )
    assert {row["id"] for row in result["threats"]} >= {
        "internal_validity",
        "construct_validity",
        "ablation_validity",
        "reproducibility_validity",
    }
    assert all(row["covered"] for row in result["threats"])
    assert "hidden semantic recall is 0.00 with FN=30" in markdown
    assert "does not judge whether the prose is sufficient" in markdown


def test_expected_results_reconciliation_replaces_aspirational_table():
    result = build_expected_results_reconciliation()
    markdown = render_expected_results_reconciliation_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["clean_paper_file_count"] == 7
    assert result["summary"]["paper_file_count"] == 7
    assert result["summary"]["headline_phrase_present_count"] == 7
    assert result["summary"]["headline_phrase_count"] == 7
    assert result["summary"]["replacement_count"] == 5
    replacements = {row["sketch_metric"]: row for row in result["expected_sketch_replacements"]}
    assert replacements["verification_rate"]["paper_status"] == "ordinary-baseline verification-rate lift unsupported"
    assert replacements["token_usage"]["stored_evidence"] == "hard30 355.0k -> 256.3k"
    assert all(row["clean"] for row in result["paper_files"])
    assert {row["path"] for row in result["paper_files"]} >= {
        "docs/artifact_guide.md",
        "docs/paper_outline.md",
    }
    assert all(row["present"] for row in result["headline_checks"])
    assert "aspirational expected-results table" in markdown
    assert "Paper files clean: 7 / 7" in markdown
    assert "`docs/artifact_guide.md`" in markdown
    assert "`docs/paper_outline.md`" in markdown
    assert "## Expected Sketch Replacement Map" in markdown
    assert "Ordinary verification-rate lift supported: no" in markdown


def test_paper_abstract_audit_covers_supported_boundary_claims():
    result = build_paper_abstract_audit()
    markdown = render_paper_abstract_audit_markdown(result)
    checks = {row["id"]: row for row in result["checks"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["passed"] == 18
    assert result["summary"]["checks"] == 18
    assert checks["verification_negative"]["passed"] is True
    assert checks["hard30_success_flat"]["passed"] is True
    assert checks["hard30_repeated_calls"]["passed"] is True
    assert checks["hidden_semantic_boundary"]["passed"] is True
    assert checks["detector_evidence_tiers"]["passed"] is True
    assert checks["hard30_category_diagnosis"]["passed"] is True
    assert checks["harness_proxy_checks"]["passed"] is True
    assert checks["no_unqualified_verification_lift"]["passed"] is True
    assert "Checks passed: 18 / 18" in markdown
    assert "verification_negative" in markdown
    assert "no_unqualified_verification_lift" in markdown


def test_paper_contribution_audit_covers_supported_contributions():
    result = build_paper_contribution_audit()
    markdown = render_paper_contribution_audit_markdown(result)
    checks = {row["id"]: row for row in result["checks"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["passed"] == 13
    assert result["summary"]["checks"] == 13
    assert checks["taxonomy_contribution"]["passed"] is True
    assert checks["benchmark_contribution"]["passed"] is True
    assert checks["codextrace_contribution"]["passed"] is True
    assert checks["empirical_boundary_contribution"]["passed"] is True
    assert checks["detector_evidence_tiers"]["passed"] is True
    assert checks["category_lost_task_diagnosis"]["passed"] is True
    assert checks["harness_proxy_checks"]["passed"] is True
    assert checks["verification_behavior_boundary"]["passed"] is True
    assert checks["no_verification_lift_contribution"]["passed"] is True
    assert "Checks passed: 13 / 13" in markdown
    assert "no_verification_lift_contribution" in markdown


def test_paper_conclusion_audit_covers_boundary_result_close():
    result = build_paper_conclusion_audit()
    markdown = render_paper_conclusion_audit_markdown(result)
    checks = {row["id"]: row for row in result["checks"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["passed"] == 16
    assert result["summary"]["checks"] == 16
    assert checks["ordinary_verification_boundary"]["passed"] is True
    assert checks["hidden_semantic_boundary"]["passed"] is True
    assert checks["semantic_oracles"]["passed"] is True
    assert checks["detector_evidence_tiers_boundary"]["passed"] is True
    assert checks["hard_tier_test_writing_boundary"]["passed"] is True
    assert checks["nullable_timing_boundary"]["passed"] is True
    assert checks["metric_coverage_link"]["passed"] is True
    assert checks["paired_effect_limitations_link"]["passed"] is True
    assert checks["no_verification_lift_overclaim"]["passed"] is True
    assert checks["no_hidden_correctness_overclaim"]["passed"] is True
    assert "Checks passed: 16 / 16" in markdown
    assert "ordinary_verification_boundary" in markdown


def test_bibliography_audit_covers_related_work_sources():
    result = build_bibliography_audit()
    markdown = render_bibliography_audit_markdown(result)
    refs = {row["id"]: row for row in result["references"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["paper_has_references"] is True
    assert result["summary"]["covered_reference_count"] == 12
    assert result["summary"]["reference_count"] == 12
    assert refs["swe_bench"]["covered"] is True
    assert refs["llms_get_lost"]["covered"] is True
    assert refs["react"]["covered"] is True
    assert refs["toolformer"]["covered"] is True
    assert refs["reflexion"]["covered"] is True
    assert refs["codex_cli_repo"]["covered"] is True
    assert refs["agentrx"]["covered"] is True
    assert "References covered: 12 / 12" in markdown
    assert "does not replace venue-specific citation formatting" in markdown


def test_build_results_summary_prefers_finalized_outputs(tmp_path):
    full_dir = tmp_path / "full30"
    hard_dir = tmp_path / "hard10"
    hard30_dir = tmp_path / "hard30"
    for directory in (full_dir, hard_dir, hard30_dir):
        directory.mkdir()

    full_dir.joinpath("aggregate.json").write_text(
        json.dumps({
            "runs": [],
            "summary": {
                "baseline": {"n": 30, "success_rate": 0.25, "avg_repeated_tool_calls": 99},
                "intervention": {"n": 30, "success_rate": 0.5, "avg_repeated_tool_calls": 11},
            },
            "deltas": {"success_rate": 0.25, "avg_repeated_tool_calls": -88},
        }),
        encoding="utf-8",
    )
    paper_report = {
        "aggregate": {
            "runs": [],
            "summary": {
                "baseline": {"n": 10, "success_rate": 0.4, "verification_rate": 1},
                "intervention": {"n": 10, "success_rate": 0.9, "verification_rate": 1},
            },
            "deltas": {"success_rate": 0.5, "verification_rate": 0},
        },
        "detector_evaluation": {
            "labels": {"hidden_semantic_edge_case": {"tp": 0, "fp": 0, "fn": 7, "precision": 0, "recall": 0, "f1": 0}},
            "summary": {"micro_f1": 0, "macro_f1": 0},
            "runs": [],
        },
        "taxonomy_distribution": [],
        "outcome_counts": {"success": 3, "failure": 7, "unknown": 0},
        "signal_by_outcome": [
            {"signal": "verification_rate", "failure_mean": 1, "success_mean": 1, "delta_success_minus_failure": 0}
        ],
        "paired_task_summary": {},
    }
    hard_dir.joinpath("paper-report-labeled.json").write_text(json.dumps(paper_report), encoding="utf-8")

    hard30_report = dict(paper_report)
    hard30_report["aggregate"] = {
        "runs": [],
        "summary": {
            "baseline": {"n": 30, "success_rate": 0.1, "verification_rate": 1},
            "intervention": {"n": 30, "success_rate": 0.2, "verification_rate": 1},
        },
        "deltas": {"success_rate": 0.1, "verification_rate": 0},
    }
    hard30_report["detector_evaluation"] = {
        "labels": {
            "hidden_semantic_edge_case": {"tp": 0, "fp": 0, "fn": 30, "precision": 0, "recall": 0, "f1": 0},
            "repetitive_exploration": {"tp": 4, "fp": 0, "fn": 0, "precision": 1, "recall": 1, "f1": 1},
        },
        "summary": {"micro_f1": 0.2, "macro_f1": 0.5},
        "runs": [],
    }
    hard30_report["outcome_counts"] = {"success": 6, "failure": 24, "unknown": 0}
    hard30_report["paired_task_summary"] = {
        "token_usage_delta": {"n": 30, "improved": 26, "regressed": 4},
        "repeated_tool_call_delta": {"n": 30, "improved": 25, "regressed": 5},
        "success_delta": {"n": 30, "improved": 3, "regressed": 0},
    }
    hard30_dir.joinpath("paper-report-labeled.json").write_text(json.dumps(hard30_report), encoding="utf-8")

    result = build_results_summary(
        full_dir / "runs.jsonl",
        None,
        None,
        None,
        hard_dir / "runs.jsonl",
        hard_dir / "manual-labels.jsonl",
        hard30_dir / "runs.jsonl",
        hard30_dir / "manual-labels.jsonl",
    )

    assert result["full30"]["summary"]["baseline"]["avg_repeated_tool_calls"] == 99
    assert result["hard10"]["summary"]["intervention"]["success_rate"] == 0.9
    assert result["hard30"]["summary"]["baseline"]["success_rate"] == 0.1
    assert result["hard30_label_evaluation"]["labels"]["repetitive_exploration"]["tp"] == 4


def test_hard30_task_diagnosis_identifies_lost_tasks_and_waste_patterns():
    result = build_task_diagnosis()
    markdown = render_task_diagnosis_markdown(result)

    assert result["summary"]["task_count"] == 30
    assert result["summary"]["double_failure_count"] == 14
    assert result["summary"]["intervention_repair_count"] == 1
    assert result["summary"]["intervention_regression_count"] == 1
    assert result["summary"]["token_improved_count"] == 26
    categories = {row["category"]: row for row in result["category_diagnosis"]}
    assert categories["dependency_friction"]["double_failure_count"] == 3
    assert categories["multi_turn_change"]["intervention_repair_count"] == 1
    assert categories["refactor"]["intervention_regression_count"] == 1
    assert categories["error_recovery"]["token_improved_count"] == 3
    assert result["intervention_repairs"][0]["task_id"] == "HARD-050"
    assert result["intervention_regressions"][0]["task_id"] == "HARD-007"
    assert result["top_waste_reductions"][0]["task_id"] == "HARD-033"
    assert result["top_lostness_tasks"][0]["task_id"] == "HARD-033"
    assert result["top_lostness_tasks"][0]["paired_lostness_score"] > 300
    assert "## Category-Level Diagnosis" in markdown
    assert "## Top Lostness Ranking" in markdown
    assert "| dependency_friction | 3 | 3 | 0 | 0 |" in markdown
    assert "| HARD-033 | both_failed | error_recovery | hidden_semantic_edge_case, repetitive_exploration |" in markdown
    assert "## Double-Failure Tasks" in markdown
    assert "HARD-050" in markdown
    assert "HARD-007" in markdown


def test_paper_claim_audit_marks_overclaims_as_unsupported():
    result = build_claim_audit()
    markdown = render_claim_audit_markdown(result)
    claims = {row["claim"]: row for row in result["claims"]}

    assert result["summary"]["hard30_tasks"] == 30
    assert result["summary"]["hard30_runs"] == 60
    assert result["summary"]["hard30_repetitive_exploration_tp"] == 4
    assert result["summary"]["full30_sandbox_permission_tp"] == 1
    assert result["summary"]["full30_sandbox_permission_fp"] == 0
    assert result["summary"]["full30_sandbox_permission_fn"] == 0
    assert result["summary"]["detector_fixture_labels"] == 6
    assert result["summary"]["detector_fixture_micro_f1"] == 1
    assert result["summary"]["process_stress_tasks"] == 12
    assert result["summary"]["process_stress_runs"] == 24
    assert result["summary"]["process_stress_failures"] == 2
    assert result["summary"]["verification_lift_tasks"] == 8
    assert result["summary"]["verification_lift_runs"] == 16
    assert result["summary"]["verification_lift_failures"] == 2
    assert result["summary"]["verification_lift_verification_delta"] == 0
    assert result["summary"]["verification_lift_success_check_delta"] == 0
    assert result["summary"]["verification_ablation_tasks"] == 4
    assert result["summary"]["verification_ablation_runs"] == 8
    assert result["summary"]["verification_ablation_verification_delta"] == 1
    assert result["summary"]["verification_ablation_success_check_delta"] == 1
    assert result["summary"]["rq4_signal_audit_ready"] is True
    assert result["summary"]["hard30_double_failure_tasks"] == 14
    assert result["summary"]["hard30_intervention_repairs"] == 1
    assert result["summary"]["hard30_intervention_regressions"] == 1
    assert result["summary"]["hard30_task_token_improved"] == 26
    assert result["summary"]["status_counts"]["supported"] >= 3
    assert claims["Harness intervention increases verification rate."]["status"] == "unsupported"
    assert claims["Harness constraints can control verification behavior under a no-verify ablation."]["status"] == "supported"
    assert claims["Task-level hard30 diagnosis identifies where agents get lost and where intervention helps or hurts."]["status"] == "supported"
    assert claims["Trace-based process rules detect most failure processes."]["status"] == "partial"
    assert claims["Trace signals explain observable process failures and the hidden-semantic boundary."]["status"] == "supported"
    assert claims["Harness intervention increases success rate."]["status"] == "partial"
    assert claims["Harness intervention reduces repeated tool-call and token waste."]["status"] == "supported"
    assert "Do not state `unsupported` claims as findings" in markdown


def test_claim_text_guard_prevents_unsupported_claim_drift(tmp_path):
    result = audit_claim_text_guard()
    markdown = render_claim_text_guard_markdown(result)

    assert result["ok"] is True
    assert result["problem_count"] == 0
    assert result["required_caveat_count"] == 7
    assert len(result["files"]) == 7
    caveats = {row["path"]: row for row in result["caveats"]}
    assert caveats["docs/paper_draft.md"]["phrase_count"] == 8
    assert caveats["docs/artifact_guide.md"]["phrase_count"] == 4
    assert caveats["README.md"]["phrase_count"] == 5
    assert all(not row["missing"] for row in result["caveats"])
    assert {row["path"] for row in result["files"]} >= {
        "docs/artifact_guide.md",
        "docs/submission_package.md",
    }
    assert "Required caveats checked: 7" in markdown
    assert "## Caveat Coverage" in markdown
    assert "| `docs/artifact_guide.md` | 4 | - |" in markdown
    assert "docs/artifact_guide.md" in markdown
    assert "docs/submission_package.md" in markdown
    assert "No unsupported-claim drift detected." in markdown

    draft = tmp_path / "draft.md"
    draft.write_text("Harness intervention increases verification rate on ordinary baselines.\n", encoding="utf-8")

    failing = audit_claim_text_guard((draft,))

    assert failing["ok"] is False
    assert failing["problems"][0]["kind"] == "unqualified_overclaim"


def test_paper_draft_contains_submission_polish_sections():
    text = Path("docs/paper_draft.md").read_text(encoding="utf-8")

    assert "## 10. Artifact Availability" in text
    assert "| Work line | Primary question | Typical evidence | CodexTrace difference |" in text
    assert "| Tier | Tasks | Runs | Baseline | Intervention | Outcome oracle | Primary use |" in text
    assert "| Design coverage slice | Covered design families | Missing design families | Use in paper |" in text
    assert "| hard30 paper-facing tier | 6 / 7 | `test_writing` |" in text
    assert "| Schema object | Fields | Purpose |" in text
    assert "| Paper field | Implementation source | Notes |" in text
    assert "`Step.event_type`" in text
    assert "`Step.tool_name`" in text
    assert "`Step.file_paths`" in text
    assert "`Step.failure_tags`" in text
    assert "| Taxonomy label | Implementation finding | Detector signal |" in text
    assert "| `verification_gap` | `verification_gap` |" in text
    assert "| `unrecovered_tool_error` | `command_failure_unhandled` |" in text
    assert "generated detector mechanism map" in text
    assert "v1 proxy rather than a semantic task-keyword drift detector" in text
    assert "| Evidence slice | Baseline | Intervention | Interpretation |" in text
    assert "| unresolved_error_rate | 0.00 | 0.00 | 0.00 |" in text
    assert "No model training, fine-tuning, embedding index, or GPU inference is used" in text
    assert "Trace diagnosis is less suited for proving semantic correctness" in text
    assert "docs/submission_package.md" in text
    assert "docs/paper_number_guard.md" in text
    assert "docs/task_category_coverage.md" in text
    assert "run-manifest provenance" in text
    assert "grader and workdir paths are retained as manifest references rather than committed directories" in text
    assert "docs/harness_protocol_audit.md" in text
    assert "docs/failure_taxonomy_audit.md" in text
    assert "docs/related_work_audit.md" in text
    assert "docs/bibliography_audit.md" in text
    assert "## References" in text
    assert "docs/paper_structure_audit.md" in text
    assert "docs/method_pipeline_audit.md" in text
    assert "docs/paper_conclusion_audit.md" in text
    assert "docs/rq_table_consistency_audit.md" in text
    assert "docs/reproducibility_audit.md" in text
    assert "docs/benchmark_trace_artifact.md" in text
    assert "docs/label_provenance_audit.md" in text
    assert "docs/label_limitations_audit.md" in text
    assert "docs/verification_saturation_audit.md" in text
    assert "docs/limitations_traceability_audit.md" in text
    assert "docs/expected_results_reconciliation.md" in text
    assert "docs/submission_readiness_plan_audit.md" in text
    assert "generated map from each RQ to its reviewer-facing verdict table" in text
    assert "docs/failure_taxonomy_audit.md#RQ1 Distribution Boundary" in text
    assert "docs/detector_evaluation_audit.md#Claim Boundary Verdicts" in text
    assert "docs/paired_effects_audit.md#RQ3 Claim Boundary Verdicts" in text
    assert "docs/rq4_signal_audit.md#RQ4 Signal Verdicts" in text
    assert "docs/verification_behavior_audit.md" in text
    assert "earlier and leaner verification path" in text
    assert "`construct_validity`" in text
    assert "No-verify ablation is not ordinary-baseline evidence." in text
    assert "docs/paired_effects_audit.md" in text
    assert "docs/paired_effect_limitations_audit.md" in text
    assert "docs/demo_audit.md" in text
    assert "docs/web_artifact_audit.md" in text
    assert "docs/cli_surface_audit.md" in text
    assert "docs/ci_surface_audit.md" in text
    assert "docs/schema_field_audit.md" in text
    assert "docs/parser_event_coverage.md" in text
    assert "docs/failure_node_traceability.md" in text
    assert "docs/phase_coverage_audit.md" in text


def test_reviewer_docs_surface_hard30_task_diagnosis():
    readme = Path("README.md").read_text(encoding="utf-8")
    guide = Path("docs/artifact_guide.md").read_text(encoding="utf-8")
    checklist = Path("docs/reproducibility_checklist.md").read_text(encoding="utf-8")

    assert "docs/hard30_task_diagnosis.md" in readme
    assert "docs/goal_completion_audit.md" in readme
    assert "docs/verification_lift_next_experiment.md" in readme
    assert "docs/thesis_revision_decision.md" in readme
    assert "docs/validity_threats.md" in readme
    assert "docs/limitations_traceability_audit.md" in readme
    assert "docs/expected_results_reconciliation.md" in readme
    assert "docs/submission_readiness_plan_audit.md" in readme
    assert "docs/verification_saturation_audit.md" in readme
    assert "docs/verification_lift_power_audit.md" in readme
    assert "docs/paper_abstract_audit.md" in readme
    assert "docs/paper_contribution_audit.md" in readme
    assert "docs/paper_conclusion_audit.md" in readme
    assert "docs/method_pipeline_audit.md" in readme
    assert "docs/verification_lift_v2_plan_audit.md" in readme
    assert "docs/verification_ablation_plan_audit.md" in readme
    assert "docs/headline_results.md" in readme
    assert "benchmark/verification-lift-v2/pilot/full-real" in readme
    assert "verification-lift-v2 | 8 | 16 | 2" in readme
    assert "completed claim-closure retest" in readme
    assert "docs/submission_package.md" in readme
    assert "docs/paper_number_guard.md" in readme
    assert "docs/reviewer_path_audit.md" in readme
    assert "docs/artifact_guide_sequence_audit.md" in readme
    assert "docs/benchmark_trace_artifact.md" in readme
    assert "docs/label_provenance_audit.md" in readme
    assert "docs/label_limitations_audit.md" in readme
    assert "docs/detector_evaluation_audit.md" in readme
    assert "docs/rule_implementation_audit.md" in readme
    assert "docs/paired_effects_audit.md" in readme
    assert "docs/paired_effect_limitations_audit.md" in readme
    assert "The main RQ claim-boundary verdict tables are in" in readme
    assert "`docs/failure_taxonomy_audit.md` (RQ1)" in readme
    assert "`docs/detector_evaluation_audit.md`" in readme
    assert "`docs/paired_effects_audit.md` (RQ3)" in readme
    assert "`docs/rq4_signal_audit.md` (RQ4)" in readme
    assert "docs/demo_audit.md" in readme
    assert "docs/web_artifact_audit.md" in readme
    assert "docs/cli_surface_audit.md" in readme
    assert "docs/ci_surface_audit.md" in readme
    assert "docs/schema_field_audit.md" in readme
    assert "docs/parser_event_coverage.md" in readme
    assert "docs/failure_node_traceability.md" in readme
    assert "docs/task_category_coverage.md" in readme
    assert "docs/harness_protocol_audit.md" in readme
    assert "docs/failure_taxonomy_audit.md" in readme
    assert "docs/related_work_audit.md" in readme
    assert "docs/bibliography_audit.md" in readme
    assert "docs/paper_structure_audit.md" in readme
    assert "docs/reproducibility_audit.md" in readme
    assert "docs/phase_coverage_audit.md" in readme
    assert "docs/rq_table_consistency_audit.md" in readme
    assert "scripts/audit_hard30_task_diagnosis.py" in readme
    assert "scripts/run_benchmark_shards.py" in readme
    assert "scripts/merge_benchmark_shards.py" in readme
    assert "scripts/finalize_benchmark_pilot.py" in readme
    assert "scripts/audit_goal_completion.py --markdown-output docs/goal_completion_audit.md" in readme
    assert "scripts/audit_thesis_revision_decision.py --markdown-output docs/thesis_revision_decision.md" in readme
    assert "scripts/audit_validity_threats.py --markdown-output docs/validity_threats.md" in readme
    assert "scripts/audit_limitations_traceability.py --markdown-output docs/limitations_traceability_audit.md" in readme
    assert "scripts/audit_expected_results_reconciliation.py --markdown-output docs/expected_results_reconciliation.md" in readme
    assert "scripts/audit_submission_readiness_plan.py --markdown-output docs/submission_readiness_plan_audit.md" in readme
    assert "scripts/audit_verification_saturation.py --markdown-output docs/verification_saturation_audit.md" in readme
    assert "scripts/audit_verification_lift_power.py --markdown-output docs/verification_lift_power_audit.md" in readme
    assert "scripts/audit_verification_behavior.py --markdown-output docs/verification_behavior_audit.md" in readme
    assert "scripts/audit_paper_abstract.py --markdown-output docs/paper_abstract_audit.md" in readme
    assert "scripts/audit_paper_contributions.py --markdown-output docs/paper_contribution_audit.md" in readme
    assert "scripts/audit_paper_conclusion.py --markdown-output docs/paper_conclusion_audit.md" in readme
    assert "scripts/audit_method_pipeline.py --markdown-output docs/method_pipeline_audit.md" in readme
    assert "scripts/audit_verification_lift_next_experiment.py --markdown-output docs/verification_lift_next_experiment.md" in readme
    assert "scripts/audit_verification_lift_v2_plan.py --markdown-output docs/verification_lift_v2_plan_audit.md" in readme
    assert "scripts/audit_verification_ablation_plan.py --markdown-output docs/verification_ablation_plan_audit.md" in readme
    assert "scripts/audit_phase_coverage.py --markdown-output docs/phase_coverage_audit.md" in readme
    assert "scripts/audit_headline_results.py --markdown-output docs/headline_results.md" in readme
    assert "scripts/audit_paper_numbers.py --markdown-output docs/paper_number_guard.md" in readme
    assert "scripts/audit_reviewer_path.py --markdown-output docs/reviewer_path_audit.md" in readme
    assert "scripts/audit_artifact_guide_sequence.py --markdown-output docs/artifact_guide_sequence_audit.md" in readme
    assert "scripts/audit_benchmark_trace_artifact.py --markdown-output docs/benchmark_trace_artifact.md" in readme
    assert "scripts/audit_label_provenance.py --markdown-output docs/label_provenance_audit.md" in readme
    assert "scripts/audit_label_limitations.py --markdown-output docs/label_limitations_audit.md" in readme
    assert "scripts/audit_submission_package.py --markdown-output docs/submission_package.md" in readme
    assert "scripts/audit_detector_evaluation.py --markdown-output docs/detector_evaluation_audit.md" in readme
    assert "scripts/audit_rule_implementation.py --markdown-output docs/rule_implementation_audit.md" in readme
    assert "scripts/audit_paired_effects.py --markdown-output docs/paired_effects_audit.md" in readme
    assert "scripts/audit_paired_effect_limitations.py --markdown-output docs/paired_effect_limitations_audit.md" in readme
    assert "scripts/audit_demo.py --markdown-output docs/demo_audit.md" in readme
    assert "scripts/audit_web_artifact.py --markdown-output docs/web_artifact_audit.md" in readme
    assert "scripts/audit_cli_surface.py --markdown-output docs/cli_surface_audit.md" in readme
    assert "scripts/audit_ci_surface.py --markdown-output docs/ci_surface_audit.md" in readme
    assert "scripts/audit_schema_fields.py --markdown-output docs/schema_field_audit.md" in readme
    assert "scripts/audit_parser_event_coverage.py --markdown-output docs/parser_event_coverage.md" in readme
    assert "scripts/audit_failure_node_traceability.py --markdown-output docs/failure_node_traceability.md" in readme
    assert "scripts/audit_task_category_coverage.py --markdown-output docs/task_category_coverage.md" in readme
    assert "scripts/audit_harness_protocol.py --markdown-output docs/harness_protocol_audit.md" in readme
    assert "scripts/audit_failure_taxonomy.py --markdown-output docs/failure_taxonomy_audit.md" in readme
    assert "scripts/audit_related_work.py --markdown-output docs/related_work_audit.md" in readme
    assert "scripts/audit_bibliography.py --markdown-output docs/bibliography_audit.md" in readme
    assert "scripts/audit_paper_structure.py --markdown-output docs/paper_structure_audit.md" in readme
    assert "scripts/audit_rq_table_consistency.py --markdown-output docs/rq_table_consistency_audit.md" in readme
    assert "scripts/audit_reproducibility.py --markdown-output docs/reproducibility_audit.md" in readme
    assert "scripts/audit_thesis_readiness.py --markdown-output docs/thesis_readiness.md" in readme
    assert "scripts/audit_claim_text_guard.py --markdown-output docs/claim_text_guard.md" in readme
    assert "docs/hard30_task_diagnosis.md" in guide
    assert "docs/submission_package.md" in guide
    assert "docs/headline_results.md" in guide
    assert "docs/thesis_revision_decision.md" in guide
    assert "docs/validity_threats.md" in guide
    assert "docs/limitations_traceability_audit.md" in guide
    assert "docs/expected_results_reconciliation.md" in guide
    assert "docs/verification_saturation_audit.md" in guide
    assert "docs/verification_lift_power_audit.md" in guide
    assert "Is there verification-rate headroom for the original expected table?" in guide
    assert "docs/paper_abstract_audit.md" in guide
    assert "docs/paper_contribution_audit.md" in guide
    assert "docs/paper_conclusion_audit.md" in guide
    assert "docs/artifact_guide_sequence_audit.md" in guide
    assert "docs/method_pipeline_audit.md" in guide
    assert "docs/claim_text_guard.md" in guide
    assert "docs/paper_number_guard.md" in guide
    assert "docs/verification_ablation_plan_audit.md" in guide
    assert "docs/detector_evaluation_audit.md" in guide
    assert "docs/rule_implementation_audit.md" in guide
    assert "docs/benchmark_trace_artifact.md" in guide
    assert "Is hard30 run-manifest provenance explicit?" in guide
    assert "traces and prompts are committed for all 60 runs" in guide
    assert "docs/label_provenance_audit.md" in guide
    assert "docs/label_limitations_audit.md" in guide
    assert "docs/paired_effects_audit.md" in guide
    assert "docs/paired_effect_limitations_audit.md" in guide
    assert "docs/demo_audit.md" in guide
    assert "docs/web_artifact_audit.md" in guide
    assert "docs/cli_surface_audit.md" in guide
    assert "docs/ci_surface_audit.md" in guide
    assert "docs/schema_field_audit.md" in guide
    assert "docs/parser_event_coverage.md" in guide
    assert "docs/failure_node_traceability.md" in guide
    assert "docs/task_category_coverage.md" in guide
    assert "docs/harness_protocol_audit.md" in guide
    assert "docs/failure_taxonomy_audit.md" in guide
    assert "docs/related_work_audit.md" in guide
    assert "docs/bibliography_audit.md" in guide
    assert "docs/paper_structure_audit.md" in guide
    assert "docs/reproducibility_audit.md" in guide
    assert "docs/phase_coverage_audit.md" in guide
    assert "docs/rq_table_consistency_audit.md" in guide
    assert "| Which tasks get lost? |" in guide
    assert "| Which claims are safe to write? |" in guide
    assert "| Did paper text drift from evidence? |" in guide
    assert "`HARD-050` repaired, `HARD-007` regressed" in guide
    assert "204-run benchmark" in guide
    assert "| verification-lift-v2 | 8 | 16 | Ordinary-baseline verification-rate retest" in guide
    assert "| verification-lift-v2 repeated tool calls | `8.62 -> 5.50` |" in guide
    assert "scripts/audit_hard30_task_diagnosis.py" in checklist
    assert "scripts/run_benchmark_shards.py" in checklist
    assert "scripts/merge_benchmark_shards.py" in checklist
    assert "scripts/finalize_benchmark_pilot.py" in checklist
    assert "scripts/audit_goal_completion.py" in checklist
    assert "scripts/audit_thesis_revision_decision.py" in checklist
    assert "scripts/audit_validity_threats.py" in checklist
    assert "scripts/audit_limitations_traceability.py" in checklist
    assert "scripts/audit_expected_results_reconciliation.py" in checklist
    assert "scripts/audit_submission_readiness_plan.py" in checklist
    assert "scripts/audit_verification_saturation.py" in checklist
    assert "scripts/audit_verification_lift_power.py" in checklist
    assert "scripts/audit_verification_behavior.py" in checklist
    assert "scripts/audit_paper_abstract.py" in checklist
    assert "scripts/audit_paper_contributions.py" in checklist
    assert "scripts/audit_paper_conclusion.py" in checklist
    assert "scripts/audit_artifact_guide_sequence.py" in checklist
    assert "scripts/audit_method_pipeline.py" in checklist
    assert "scripts/audit_verification_lift_next_experiment.py" in checklist
    assert "scripts/audit_verification_lift_v2_plan.py" in checklist
    assert "scripts/audit_verification_ablation_plan.py" in checklist
    assert "scripts/audit_headline_results.py" in checklist
    assert "scripts/audit_submission_package.py" in checklist
    assert "--markdown-output /tmp/limitations-traceability-audit.md" in checklist
    assert "--markdown-output /tmp/expected-results-reconciliation.md" in checklist
    assert "--markdown-output /tmp/paper-conclusion-audit.md" in checklist
    assert "--markdown-output /tmp/label-limitations-audit.md" in checklist
    assert "scripts/audit_paper_numbers.py" in checklist
    assert "scripts/audit_reviewer_path.py" in checklist
    assert "scripts/audit_benchmark_trace_artifact.py" in checklist
    assert "Run Manifest Provenance table" in checklist
    assert "grader/workdir paths are provenance references rather than committed directories" in checklist
    assert "scripts/audit_label_provenance.py" in checklist
    assert "scripts/audit_label_limitations.py" in checklist
    assert "scripts/audit_detector_evaluation.py" in checklist
    assert "scripts/audit_rule_implementation.py" in checklist
    assert "scripts/audit_paired_effects.py" in checklist
    assert "scripts/audit_paired_effect_limitations.py" in checklist
    assert "scripts/audit_demo.py" in checklist
    assert "scripts/audit_web_artifact.py" in checklist
    assert "scripts/audit_cli_surface.py" in checklist
    assert "scripts/audit_ci_surface.py" in checklist
    assert "scripts/audit_schema_fields.py" in checklist
    assert "scripts/audit_parser_event_coverage.py" in checklist
    assert "scripts/audit_failure_node_traceability.py" in checklist
    assert "scripts/audit_task_category_coverage.py" in checklist
    assert "scripts/audit_harness_protocol.py" in checklist
    assert "scripts/audit_failure_taxonomy.py" in checklist
    assert "scripts/audit_related_work.py" in checklist
    assert "scripts/audit_bibliography.py" in checklist
    assert "scripts/audit_paper_structure.py" in checklist
    assert "scripts/audit_rq_table_consistency.py" in checklist
    assert "scripts/audit_reproducibility.py" in checklist
    assert "scripts/audit_phase_coverage.py" in checklist
    assert "--markdown-output /tmp/hard30-task-diagnosis.md" in checklist
    assert "--output-dir /tmp/codextrace-verification-lift-v2-dry" in checklist
    assert "--status-json /tmp/verification-lift-v2-shard-status.json" in checklist
    assert "--preflight-json /tmp/verification-lift-v2-preflight.json" in checklist
    assert "--markdown-output /tmp/verification-ablation-plan-audit.md" in checklist
    assert "--markdown-output /tmp/detector-evaluation-audit.md" in checklist
    assert "--markdown-output /tmp/rule-implementation-audit.md" in checklist
    assert "--markdown-output /tmp/benchmark-trace-artifact.md" in checklist
    assert "--markdown-output /tmp/label-provenance-audit.md" in checklist
    assert "--markdown-output /tmp/verification-saturation-audit.md" in checklist
    assert "--markdown-output /tmp/verification-behavior-audit.md" in checklist
    assert "--markdown-output /tmp/paired-effects-audit.md" in checklist
    assert "--markdown-output /tmp/demo-audit.md" in checklist
    assert "--markdown-output /tmp/web-artifact-audit.md" in checklist
    assert "--markdown-output /tmp/cli-surface-audit.md" in checklist
    assert "--markdown-output /tmp/ci-surface-audit.md" in checklist
    assert "--markdown-output /tmp/rq-table-consistency-audit.md" in checklist
    assert "--markdown-output /tmp/schema-field-audit.md" in checklist
    assert "--markdown-output /tmp/parser-event-coverage.md" in checklist
    assert "--markdown-output /tmp/failure-node-traceability.md" in checklist
    assert "benchmark/verification-lift-v2/pilot/full-real/aggregate.md" in checklist
    assert "completed claim-closure retest" in checklist
    assert "repeated calls improve `8.62 -> 5.50`" in checklist
    assert "--markdown-output /tmp/headline-results.md" in checklist
    assert "--markdown-output /tmp/thesis-revision-decision.md" in checklist
    assert "--markdown-output /tmp/validity-threats.md" in checklist
    assert "--markdown-output /tmp/paper-abstract-audit.md" in checklist
    assert "--markdown-output /tmp/paper-contribution-audit.md" in checklist
    assert "--markdown-output /tmp/method-pipeline-audit.md" in checklist
    assert "--markdown-output /tmp/task-category-coverage.md" in checklist
    assert "--markdown-output /tmp/phase-coverage-audit.md" in checklist
    assert "--markdown-output /tmp/harness-protocol-audit.md" in checklist
    assert "--markdown-output /tmp/bibliography-audit.md" in checklist


def test_paper_outline_tracks_current_boundary_result():
    outline = Path("docs/paper_outline.md").read_text(encoding="utf-8")
    normalized = " ".join(outline.split())

    assert "A task-level hard30 diagnosis identifies 14 double-failure" in normalized
    assert "one intervention repair (`HARD-050`)" in normalized
    assert "one intervention regression" in normalized
    assert "task-level waste delta" in normalized
    assert "verification is saturated" in normalized
    assert "verification-lift-v2" in normalized
    assert "negative evidence for a verification-rate-lift claim" in normalized
    assert "repeated tool calls improve 8.62 -> 5.50" in normalized


def test_experiment_protocol_maps_rqs_to_evidence():
    text = Path("docs/experiment_protocol.md").read_text(encoding="utf-8")
    normalized = " ".join(text.lower().split())

    assert "## RQ-To-Evidence Map" in text
    assert "| RQ1 failure modes |" in text
    assert "| RQ2 trace-only detection |" in text
    assert "| RQ3 intervention effect |" in text
    assert "| RQ4 explanatory signals |" in text
    assert "docs/hard30_task_diagnosis.md" in text
    assert "one intervention repair (`HARD-050`), one intervention regression" in text
    assert "ordinary and weak-baseline verification rates are saturated" in normalized
    assert "benchmark/verification-lift-v2/pilot/full-real" in text
    assert "verification remain `1.00 -> 1.00` in both tiers" in text
    assert "Future dataset extension:" in text


def test_thesis_readiness_identifies_original_thesis_gaps():
    result = build_thesis_readiness()
    markdown = render_thesis_readiness_markdown(result)
    requirements = {row["id"]: row for row in result["requirements"]}

    assert result["summary"]["ready_for_original_thesis"] is False
    assert result["summary"]["ready_for_boundary_result_paper"] is True
    assert requirements["taxonomy"]["status"] == "satisfied"
    assert requirements["benchmark"]["status"] == "satisfied"
    assert requirements["verification_lift"]["status"] == "missing"
    assert requirements["process_rule_detection"]["status"] == "satisfied"
    assert requirements["verification_behavior"]["status"] == "satisfied"
    assert requirements["rq4_explanation"]["status"] == "satisfied"
    assert result["summary"]["status_counts"]["satisfied"] == 7
    assert "full30 sandbox_permission_deadlock has TP=1" in markdown
    assert "controlled detector fixtures cover 6 labels" in markdown
    assert "task diagnosis: double failures=14, repairs=1, regressions=1" in markdown
    assert "verification behavior audit shows saturated non-ablation tiers=6/6" in markdown
    assert "intervention reaches verification earlier with fewer verify-phase events" in markdown
    assert "Headroom audit: 98 non-ablation baseline run(s)" in markdown
    assert "empirical headroom=0.00" in markdown
    assert "ordinary expansion can close claim=no" in markdown
    assert "Boundary-style RQ4 is supported" in markdown
    assert "optional process-stress expansion" in markdown
    assert "verification-lift tier" in markdown
    assert "Verification-Lift-V2 Experiment" in markdown
    assert "Current verification-lift-v2 pilot" in markdown
    assert "verification is saturated" in markdown
    assert result["next_experiment"]["current_scaffold"]["ready"] is True
    assert result["verification_lift_experiment"]["current_scaffold"]["ready"] is True
    assert result["verification_lift_experiment"]["current_scaffold"]["task_count"] == 8
    verification_pilot = result["verification_lift_experiment"]["current_scaffold"]["pilot"]
    assert verification_pilot["tasks"] == 8
    assert verification_pilot["runs"] == 16
    assert verification_pilot["baseline_verification_rate"] == verification_pilot["intervention_verification_rate"]
    assert verification_pilot["baseline_success_check_verification_rate"] == verification_pilot["intervention_success_check_verification_rate"]
    ablation_pilot = result["verification_ablation_experiment"]["current_scaffold"]["pilot"]
    assert ablation_pilot["tasks"] == 4
    assert ablation_pilot["runs"] == 8
    assert ablation_pilot["baseline_verification_rate"] == 0
    assert ablation_pilot["intervention_verification_rate"] == 1
    assert ablation_pilot["baseline_success_check_verification_rate"] == 0
    assert ablation_pilot["intervention_success_check_verification_rate"] == 1
    v2_pilot = result["verification_lift_v2_experiment"]["current_scaffold"]["pilot"]
    assert v2_pilot["tasks"] == 8
    assert v2_pilot["runs"] == 16
    assert v2_pilot["baseline_verification_rate"] == v2_pilot["intervention_verification_rate"]
    assert v2_pilot["baseline_repeated_calls"] > v2_pilot["intervention_repeated_calls"]
    assert v2_pilot["baseline_token_usage"] > v2_pilot["intervention_token_usage"]
    power = result["verification_lift_power_audit"]["summary"]
    assert power["baseline_runs"] == 98
    assert power["baseline_unverified_broad"] == 0
    assert power["ordinary_expansion_can_close_claim"] is False
    pilot = result["next_experiment"]["current_scaffold"]["pilot"]
    assert pilot["tasks"] == 12
    assert pilot["runs"] == 24
    assert pilot["baseline_success_rate"] == pilot["intervention_success_rate"]
    assert pilot["baseline_repeated_calls"] > pilot["intervention_repeated_calls"]
    assert pilot["baseline_token_usage"] > pilot["intervention_token_usage"]


def test_submission_package_maps_rqs_to_safe_paper_claims():
    package = build_submission_package()
    markdown = render_submission_package_markdown(package)

    assert package["summary"]["rq_count"] == 4
    assert package["summary"]["package_ready_for_boundary_paper"] is True
    assert package["summary"]["ready_for_original_thesis"] is False
    assert package["summary"]["unsupported_claim_count"] == 2
    assert package["summary"]["required_boundary"] == "ordinary verification-rate lift remains unsupported; no-verify lift is an ablation only"
    assert "docs/artifact_guide.md" in package["required_files"]
    assert "docs/submission_package.md" in package["required_files"]
    assert "docs/goal_completion_audit.md" in package["required_files"]
    assert "docs/thesis_revision_decision.md" in package["required_files"]
    assert "docs/validity_threats.md" in package["required_files"]
    assert "docs/limitations_traceability_audit.md" in package["required_files"]
    assert "docs/expected_results_reconciliation.md" in package["required_files"]
    assert "docs/submission_readiness_plan.md" in package["required_files"]
    assert "docs/submission_readiness_plan_audit.md" in package["required_files"]
    assert "docs/verification_lift_next_experiment.md" in package["required_files"]
    assert "docs/verification_lift_v2_plan_audit.md" in package["required_files"]
    assert "docs/verification_ablation_plan_audit.md" in package["required_files"]
    assert "docs/headline_results.md" in package["required_files"]
    assert "docs/paper_draft.md" in package["required_files"]
    assert "docs/paper_abstract_audit.md" in package["required_files"]
    assert "docs/paper_contribution_audit.md" in package["required_files"]
    assert "docs/paper_conclusion_audit.md" in package["required_files"]
    assert "docs/method_pipeline_audit.md" in package["required_files"]
    assert "docs/rq_table_consistency_audit.md" in package["required_files"]
    assert "docs/paper_structure_audit.md" in package["required_files"]
    assert "docs/experiment_protocol.md" in package["required_files"]
    assert "docs/paper_outline.md" in package["required_files"]
    assert "docs/paper_number_guard.md" in package["required_files"]
    assert "docs/reviewer_path_audit.md" in package["required_files"]
    assert "docs/artifact_guide_sequence_audit.md" in package["required_files"]
    assert "docs/benchmark_trace_artifact.md" in package["required_files"]
    assert "docs/label_provenance_audit.md" in package["required_files"]
    assert "docs/label_limitations_audit.md" in package["required_files"]
    assert "docs/verification_saturation_audit.md" in package["required_files"]
    assert "docs/verification_lift_power_audit.md" in package["required_files"]
    assert "docs/metric_coverage_audit.md" in package["required_files"]
    assert "docs/paired_effects_audit.md" in package["required_files"]
    assert "docs/paired_effect_limitations_audit.md" in package["required_files"]
    assert "docs/demo_audit.md" in package["required_files"]
    assert "docs/web_artifact_audit.md" in package["required_files"]
    assert "docs/cli_surface_audit.md" in package["required_files"]
    assert "docs/ci_surface_audit.md" in package["required_files"]
    assert "docs/schema_field_audit.md" in package["required_files"]
    assert "docs/parser_event_coverage.md" in package["required_files"]
    assert "docs/failure_node_traceability.md" in package["required_files"]
    assert "docs/detector_evaluation_audit.md" in package["required_files"]
    assert "docs/rule_implementation_audit.md" in package["required_files"]
    assert "docs/rq4_signal_audit.md" in package["required_files"]
    assert "docs/phase_coverage_audit.md" in package["required_files"]
    assert "docs/task_category_coverage.md" in package["required_files"]
    assert "docs/harness_protocol_audit.md" in package["required_files"]
    assert "docs/failure_taxonomy_audit.md" in package["required_files"]
    assert "docs/related_work.md" in package["required_files"]
    assert "docs/related_work_audit.md" in package["required_files"]
    assert "docs/bibliography_audit.md" in package["required_files"]
    assert "docs/reproducibility_audit.md" in package["required_files"]
    assert "docs/verification_behavior_audit.md" in package["required_files"]
    assert [row["rq"] for row in package["rq_rows"]] == ["RQ1", "RQ2", "RQ3", "RQ4"]
    verdict_tables = {row["rq"]: row["verdict_table"] for row in package["rq_rows"]}
    assert verdict_tables["RQ1"] == "docs/failure_taxonomy_audit.md#RQ1 Distribution Boundary"
    assert verdict_tables["RQ2"] == "docs/detector_evaluation_audit.md#Claim Boundary Verdicts"
    assert verdict_tables["RQ3"] == "docs/paired_effects_audit.md#RQ3 Claim Boundary Verdicts"
    assert verdict_tables["RQ4"] == "docs/rq4_signal_audit.md#RQ4 Signal Verdicts"
    assert package["rq_rows"][2]["status"] == "supported"
    assert "ordinary verification-rate lift is unsupported" in package["rq_rows"][2]["claim_boundary"]
    assert "docs/verification_lift_power_audit.md" in package["rq_rows"][2]["primary_evidence"]
    assert "docs/verification_behavior_audit.md" in package["rq_rows"][2]["primary_evidence"]
    assert any(row["claim"] == "Harness intervention increases verification rate." for row in package["unsupported_claims"])
    assert "verification-lift-v2 verification delta is +0.00" in markdown
    assert "## RQ-To-Evidence Map" in markdown
    assert "docs/hard30_task_diagnosis.md" in markdown
    assert "docs/detector_evaluation_audit.md" in markdown
    assert "docs/detector_evaluation_audit.md#Claim Boundary Verdicts" in markdown
    assert "docs/rule_implementation_audit.md" in markdown
    assert "docs/benchmark_trace_artifact.md" in markdown
    assert "docs/artifact_guide_sequence_audit.md" in markdown
    assert "docs/submission_readiness_plan_audit.md" in markdown
    assert "docs/label_provenance_audit.md" in markdown
    assert "docs/label_limitations_audit.md" in markdown
    assert "docs/verification_saturation_audit.md" in markdown
    assert "docs/paired_effects_audit.md" in markdown
    assert "docs/paired_effect_limitations_audit.md" in markdown
    assert "docs/demo_audit.md" in markdown
    assert "docs/web_artifact_audit.md" in markdown
    assert "docs/verification_ablation_plan_audit.md" in markdown
    assert "docs/task_category_coverage.md" in markdown
    assert "docs/harness_protocol_audit.md" in markdown
    assert "docs/failure_taxonomy_audit.md" in markdown
    assert "docs/related_work_audit.md" in markdown
    assert "docs/bibliography_audit.md" in markdown
    assert "docs/paper_structure_audit.md" in markdown
    assert "docs/reproducibility_audit.md" in markdown
    assert "docs/rq4_signal_audit.md" in markdown
    assert "docs/cli_surface_audit.md" in markdown
    assert "docs/ci_surface_audit.md" in markdown
    assert "docs/schema_field_audit.md" in markdown
    assert "docs/parser_event_coverage.md" in markdown
    assert "docs/failure_node_traceability.md" in markdown
    assert "docs/phase_coverage_audit.md" in markdown
    assert "docs/headline_results.md" in markdown
    assert "docs/thesis_revision_decision.md" in markdown
    assert "docs/validity_threats.md" in markdown
    assert "docs/limitations_traceability_audit.md" in markdown
    assert "docs/expected_results_reconciliation.md" in markdown
    assert "docs/submission_readiness_plan_audit.md" in markdown
    assert "docs/paper_abstract_audit.md" in markdown
    assert "docs/paper_contribution_audit.md" in markdown
    assert "docs/paper_conclusion_audit.md" in markdown
    assert "docs/method_pipeline_audit.md" in markdown
    assert "docs/rq_table_consistency_audit.md" in markdown
    assert "Unsupported Claims To Avoid" in markdown


def test_submission_readiness_validates_submission_package_content(tmp_path):
    broken = tmp_path / "submission_package.md"
    broken.write_text("# CodexTrace Submission Package Map\n", encoding="utf-8")

    check = check_submission_package_content(broken)

    assert check["ok"] is False
    assert "missing rq map" in check["problems"]
    assert "missing verdict table column" in check["problems"]
    assert "missing rq1 verdict anchor" in check["problems"]
    assert "missing rq2 verdict anchor" in check["problems"]
    assert "missing rq3 verdict anchor" in check["problems"]
    assert "missing rq4 verdict anchor" in check["problems"]
    assert "missing required boundary" in check["problems"]
    assert "missing verification overclaim guard" in check["problems"]


def test_submission_readiness_validates_headline_results_content(tmp_path):
    broken = tmp_path / "headline_results.md"
    broken.write_text("# Headline Results Table\nReady: no\n", encoding="utf-8")

    check = check_headline_results_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing verification lift unsupported" in check["problems"]
    assert "missing not ordinary baseline" in check["problems"]


def test_submission_readiness_validates_thesis_revision_decision_content(tmp_path):
    broken = tmp_path / "thesis_revision_decision.md"
    broken.write_text("# Thesis Revision Decision\nReady: no\n", encoding="utf-8")

    check = check_thesis_revision_decision_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing decision" in check["problems"]
    assert "missing headroom baseline runs" in check["problems"]
    assert "missing drop finding" in check["problems"]


def test_submission_readiness_validates_validity_threats_content(tmp_path):
    broken = tmp_path / "validity_threats.md"
    broken.write_text("# Validity Threats Audit\nReady: no\n", encoding="utf-8")

    check = check_validity_threats_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing construct validity" in check["problems"]


def test_submission_readiness_validates_limitations_traceability_audit_content(tmp_path):
    broken = tmp_path / "limitations_traceability_audit.md"
    broken.write_text("# Limitations Traceability Audit\nReady: no\n", encoding="utf-8")

    check = check_limitations_traceability_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing internal validity" in check["problems"]
    assert "missing construct validity" in check["problems"]
    assert "missing venue caveat" in check["problems"]


def test_submission_readiness_validates_expected_results_reconciliation_content(tmp_path):
    broken = tmp_path / "expected_results_reconciliation.md"
    broken.write_text("# Expected Results Reconciliation Audit\nReady: no\n", encoding="utf-8")

    check = check_expected_results_reconciliation_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing paper files clean" in check["problems"]
    assert "missing headline phrases" in check["problems"]
    assert "missing artifact guide scanned" in check["problems"]
    assert "missing paper outline scanned" in check["problems"]
    assert "missing ordinary lift unsupported" in check["problems"]
    assert "missing expected sketch caveat" in check["problems"]


def test_submission_readiness_validates_submission_readiness_plan_audit_content(tmp_path):
    broken = tmp_path / "submission_readiness_plan_audit.md"
    broken.write_text("# Submission Readiness Plan Audit\nReady: no\n", encoding="utf-8")

    check = check_submission_readiness_plan_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing boundary positioning" in check["problems"]
    assert "missing remaining process positives" in check["problems"]
    assert "missing no original complete overclaim" in check["problems"]


def test_paper_number_guard_keeps_draft_numbers_in_sync(tmp_path):
    result = build_paper_number_guard()
    markdown = render_paper_number_guard_markdown(result)

    assert result["ok"] is True
    assert result["summary"]["checked"] == 10
    assert result["summary"]["missing"] == 0
    assert "full30 failure-score row" in markdown
    assert "hard10 token row" in markdown
    assert "verification-lift-v2 paragraph" in markdown

    stale = tmp_path / "paper_draft.md"
    stale.write_text("success rate stays flat at 50%\n", encoding="utf-8")
    failing = build_paper_number_guard(paper_draft_path=stale)

    assert failing["ok"] is False
    assert any(row["name"] == "hard10 token row" for row in failing["missing"])


def test_submission_readiness_validates_paper_number_guard_content(tmp_path):
    broken = tmp_path / "paper_number_guard.md"
    broken.write_text("# Paper Number Guard\nOK: no\n", encoding="utf-8")

    check = check_paper_number_guard_content(broken)

    assert check["ok"] is False
    assert "missing ok" in check["problems"]
    assert "missing missing count" in check["problems"]


def test_submission_readiness_validates_paper_abstract_audit_content(tmp_path):
    broken = tmp_path / "paper_abstract_audit.md"
    broken.write_text("# Paper Abstract Audit\nReady: no\n", encoding="utf-8")

    check = check_paper_abstract_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing verification negative" in check["problems"]
    assert "missing detector evidence tiers" in check["problems"]
    assert "missing hard30 category diagnosis" in check["problems"]
    assert "missing harness proxy checks" in check["problems"]


def test_submission_readiness_validates_paper_contribution_audit_content(tmp_path):
    broken = tmp_path / "paper_contribution_audit.md"
    broken.write_text("# Paper Contribution Audit\nReady: no\n", encoding="utf-8")

    check = check_paper_contribution_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing taxonomy" in check["problems"]


def test_submission_readiness_validates_paper_conclusion_audit_content(tmp_path):
    broken = tmp_path / "paper_conclusion_audit.md"
    broken.write_text("# Paper Conclusion Audit\nReady: no\n", encoding="utf-8")

    check = check_paper_conclusion_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing ordinary verification boundary" in check["problems"]
    assert "missing hidden semantic boundary" in check["problems"]
    assert "missing detector evidence tiers boundary" in check["problems"]
    assert "missing hard-tier test writing boundary" in check["problems"]
    assert "missing nullable timing boundary" in check["problems"]
    assert "missing metric coverage link" in check["problems"]
    assert "missing paired effect limitations" in check["problems"]
    assert "missing no verification overclaim" in check["problems"]


def test_reviewer_path_audit_covers_required_artifacts(tmp_path):
    result = build_reviewer_path_audit()
    markdown = render_reviewer_path_audit_markdown(result)

    assert result["ok"] is True
    assert result["summary"]["missing"] == 0
    assert result["summary"]["guide_missing"] == 0
    assert result["summary"]["checklist_missing"] == 0
    assert result["summary"]["path_check_missing"] == 0
    assert result["summary"]["boundary_check_missing"] == 0
    assert result["summary"]["boundary_checks"] == 8
    assert result["summary"]["core_step_count"] == 10
    assert result["summary"]["extended_step_count"] >= 30
    assert any(row["path"] == "docs/artifact_guide.md" for row in result["coverage"])
    assert any(row["path"] == "docs/experiment_protocol.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paper_outline.md" for row in result["coverage"])
    assert any(row["path"] == "docs/reviewer_path_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/detector_evaluation_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/rule_implementation_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/verification_ablation_plan_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/verification_behavior_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paired_effects_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paired_effect_limitations_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/demo_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/web_artifact_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/cli_surface_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/schema_field_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/parser_event_coverage.md" for row in result["coverage"])
    assert any(row["path"] == "docs/failure_node_traceability.md" for row in result["coverage"])
    assert any(row["path"] == "docs/phase_coverage_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/task_category_coverage.md" for row in result["coverage"])
    assert any(row["path"] == "docs/harness_protocol_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/failure_taxonomy_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/related_work_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/bibliography_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paper_structure_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/reproducibility_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/artifact_guide_sequence_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/submission_readiness_plan_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/headline_results.md" for row in result["coverage"])
    assert any(row["path"] == "docs/thesis_revision_decision.md" for row in result["coverage"])
    assert any(row["path"] == "docs/validity_threats.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paper_abstract_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paper_contribution_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/paper_conclusion_audit.md" for row in result["coverage"])
    assert any(row["path"] == "docs/label_limitations_audit.md" for row in result["coverage"])
    assert "Missing from reproducibility checklist: 0" in markdown
    assert "Core path structure: ok" in markdown
    assert "Core path steps: 10" in markdown
    assert "Path structure checks failed: 0" in markdown
    assert "Entry boundary checks failed: 0" in markdown
    assert "`readme_detector_evidence_tiers` | `README.md` | pass" in markdown
    assert "`guide_hard_tier_test_writing_boundary` | `docs/artifact_guide.md` | pass" in markdown
    assert "`readme_nullable_timing_boundary` | `README.md` | pass" in markdown
    assert "`readme_verification_headroom_boundary` | `README.md` | pass" in markdown
    assert "`guide_verification_headroom_boundary` | `docs/artifact_guide.md` | pass" in markdown
    assert "`core_path_step_count` | pass" in markdown

    package = tmp_path / "submission_package.json"
    package.write_text(json.dumps({"required_files": ["docs/not-linked.md"]}), encoding="utf-8")
    failing = build_reviewer_path_audit(submission_package_path=package)

    assert failing["ok"] is False
    assert failing["missing"][0]["path"] == "docs/not-linked.md"

    broken_guide = tmp_path / "artifact_guide.md"
    broken_guide.write_text(
        "# CodexTrace Artifact Guide\n\n"
        "## Fifteen-Minute Review Path\n\n"
        "1. One\n2. Two\n\n"
        "## Main Evidence\n",
        encoding="utf-8",
    )
    bad_path = build_reviewer_path_audit(artifact_guide_path=broken_guide)

    assert bad_path["ok"] is False
    assert "core_path_step_count" in {row["id"] for row in bad_path["path_check_missing"]}
    assert "old_long_path_removed" in {row["id"] for row in bad_path["path_check_missing"]}
    assert "guide_detector_evidence_tiers" in {row["id"] for row in bad_path["boundary_check_missing"]}


def test_submission_readiness_validates_reviewer_path_audit_content(tmp_path):
    broken = tmp_path / "reviewer_path_audit.md"
    broken.write_text("# Reviewer Path Audit\nOK: no\n", encoding="utf-8")

    check = check_reviewer_path_audit_content(broken)

    assert check["ok"] is False
    assert "missing ok" in check["problems"]
    assert "missing checklist coverage" in check["problems"]
    assert "missing core path structure" in check["problems"]
    assert "missing entry boundary checks" in check["problems"]
    assert "missing entry boundary table" in check["problems"]
    assert "missing verification headroom boundary" in check["problems"]


def test_submission_readiness_validates_artifact_guide_sequence_audit_content(tmp_path):
    broken = tmp_path / "artifact_guide_sequence_audit.md"
    broken.write_text("# Artifact Guide Sequence Audit\nReady: no\n", encoding="utf-8")

    check = check_artifact_guide_sequence_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing step count" in check["problems"]
    assert "missing no duplicate numbers" in check["problems"]
    assert "missing required links" in check["problems"]
    assert "missing rq2 detector link" in check["problems"]
    assert "missing rq4 signal link" in check["problems"]
    assert "missing taxonomy evidence tiers" in check["problems"]
    assert "missing tier labels" in check["problems"]
    assert "missing rq1 verdict phrase" in check["problems"]
    assert "missing rq3 verdict phrase" in check["problems"]
    assert "missing rq4 verdict phrase" in check["problems"]


def test_submission_readiness_validates_claim_text_guard_content(tmp_path):
    broken = tmp_path / "claim_text_guard.md"
    broken.write_text("# Claim Text Guard\nStatus: fail\nFiles checked: 5\n", encoding="utf-8")

    check = check_claim_text_guard_content(broken)

    assert check["ok"] is False
    assert "missing status" in check["problems"]
    assert "missing file count" in check["problems"]
    assert "missing caveat count" in check["problems"]
    assert "missing problem count" in check["problems"]
    assert "missing artifact guide target" in check["problems"]
    assert "missing submission package target" in check["problems"]


def test_submission_readiness_validates_metric_coverage_audit_content(tmp_path):
    broken = tmp_path / "metric_coverage_audit.md"
    broken.write_text("# Metric Coverage Audit\nReady: no\n", encoding="utf-8")

    check = check_metric_coverage_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing manifest count" in check["problems"]
    assert "missing coverage count" in check["problems"]
    assert "missing coverage cells" in check["problems"]
    assert "missing prompt summary cells" in check["problems"]
    assert "missing prompt summary section" in check["problems"]
    assert "missing hard30 baseline prompt summary" in check["problems"]
    assert "missing hard30 intervention prompt summary" in check["problems"]
    assert "missing time to first test" in check["problems"]
    assert "missing verification ablation manifest" in check["problems"]


def test_submission_readiness_validates_hard30_task_diagnosis_content(tmp_path):
    broken = tmp_path / "hard30_task_diagnosis.md"
    broken.write_text("# Hard30 Task Diagnosis\nTasks: 30\n", encoding="utf-8")

    check = check_hard30_task_diagnosis_content(broken)

    assert check["ok"] is False
    assert "missing double failures" in check["problems"]
    assert "missing category diagnosis" in check["problems"]
    assert "missing dependency friction" in check["problems"]


def test_submission_readiness_validates_paired_effects_audit_content(tmp_path):
    broken = tmp_path / "paired_effects_audit.md"
    broken.write_text("# Paired Effects Audit\nReady: no\n", encoding="utf-8")

    check = check_paired_effects_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing study coverage" in check["problems"]
    assert "missing hard30 paired tasks" in check["problems"]
    assert "missing non-ablation repeated" in check["problems"]
    assert "missing non-ablation token" in check["problems"]
    assert "missing ablation role" in check["problems"]
    assert "missing rq3 claim verdicts" in check["problems"]
    assert "missing waste supported" in check["problems"]
    assert "missing hard30 success unsupported" in check["problems"]
    assert "missing verification unsupported" in check["problems"]
    assert "missing ablation mechanism" in check["problems"]
    assert "missing bootstrap caveat" in check["problems"]


def test_submission_readiness_validates_paired_effect_limitations_audit_content(tmp_path):
    broken = tmp_path / "paired_effect_limitations_audit.md"
    broken.write_text("# Paired Effect Limitations Audit\nReady: no\n", encoding="utf-8")

    check = check_paired_effect_limitations_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing checks passed" in check["problems"]
    assert "missing population caveat" in check["problems"]
    assert "missing overclaim guard" in check["problems"]


def test_submission_readiness_validates_demo_audit_content(tmp_path):
    broken = tmp_path / "demo_audit.md"
    broken.write_text("# Demo Audit\nReady: no\n", encoding="utf-8")

    check = check_demo_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing finding coverage" in check["problems"]
    assert "missing event ids" in check["problems"]
    assert "missing web ui caveat" in check["problems"]


def test_submission_readiness_validates_web_artifact_audit_content(tmp_path):
    broken = tmp_path / "web_artifact_audit.md"
    broken.write_text("# Web Artifact Audit\nReady: no\n", encoding="utf-8")

    check = check_web_artifact_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing event ids" in check["problems"]
    assert "missing source checks" in check["problems"]
    assert "missing install caveat" in check["problems"]


def test_submission_readiness_validates_schema_field_audit_content(tmp_path):
    broken = tmp_path / "schema_field_audit.md"
    broken.write_text("# Schema Field Audit\nReady: no\n", encoding="utf-8")

    check = check_schema_field_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing objective schema coverage" in check["problems"]
    assert "missing run coverage" in check["problems"]
    assert "missing step coverage" in check["problems"]
    assert "missing failure tags" in check["problems"]


def test_submission_readiness_validates_cli_surface_audit_content(tmp_path):
    broken = tmp_path / "cli_surface_audit.md"
    broken.write_text("# CLI Surface Audit\nReady: no\n", encoding="utf-8")

    check = check_cli_surface_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing command coverage" in check["problems"]
    assert "missing subcommand coverage" in check["problems"]
    assert "missing live collection caveat" in check["problems"]


def test_submission_readiness_validates_ci_surface_audit_content(tmp_path):
    broken = tmp_path / "ci_surface_audit.md"
    broken.write_text("# CI Surface Audit\nReady: no\n", encoding="utf-8")

    check = check_ci_surface_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing ci coverage" in check["problems"]
    assert "missing packaging coverage" in check["problems"]
    assert "missing actions caveat" in check["problems"]


def test_submission_readiness_validates_benchmark_trace_artifact_content(tmp_path):
    broken = tmp_path / "benchmark_trace_artifact.md"
    broken.write_text("# Benchmark Trace Artifact Audit\nReady: no\n", encoding="utf-8")

    check = check_benchmark_trace_artifact_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing task coverage" in check["problems"]
    assert "missing trace coverage" in check["problems"]
    assert "missing parseable traces" in check["problems"]
    assert "missing trace sidecars" in check["problems"]
    assert "missing prompt balance ready" in check["problems"]
    assert "missing prompt balance table" in check["problems"]
    assert "missing baseline balance" in check["problems"]
    assert "missing intervention balance" in check["problems"]
    assert "missing rerun caveat" in check["problems"]


def test_submission_readiness_validates_label_provenance_audit_content(tmp_path):
    broken = tmp_path / "label_provenance_audit.md"
    broken.write_text("# Label Provenance Audit\nReady: no\n", encoding="utf-8")

    check = check_label_provenance_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing template label rows" in check["problems"]
    assert "missing manual label rows" in check["problems"]
    assert "missing eval match" in check["problems"]
    assert "missing inter annotator caveat" in check["problems"]


def test_submission_readiness_validates_label_limitations_audit_content(tmp_path):
    broken = tmp_path / "label_limitations_audit.md"
    broken.write_text("# Label Limitations Audit\nReady: no\n", encoding="utf-8")

    check = check_label_limitations_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage" in check["problems"]
    assert "missing single artifact caveat" in check["problems"]
    assert "missing inter annotator caveat" in check["problems"]


def test_submission_readiness_validates_method_pipeline_audit_content(tmp_path):
    broken = tmp_path / "method_pipeline_audit.md"
    broken.write_text("# Method Pipeline Audit\nReady: no\n", encoding="utf-8")

    check = check_method_pipeline_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing stage coverage" in check["problems"]
    assert "missing smoke coverage" in check["problems"]
    assert "missing smoke metrics" in check["problems"]
    assert "missing diagnosis findings" in check["problems"]
    assert "missing findings with event ids" in check["problems"]
    assert "missing aggregate run rows" in check["problems"]
    assert "missing live collection caveat" in check["problems"]


def test_submission_readiness_validates_rq_table_consistency_audit_content(tmp_path):
    broken = tmp_path / "rq_table_consistency_audit.md"
    broken.write_text("# RQ Table Consistency Audit\nReady: no\n", encoding="utf-8")

    check = check_rq_table_consistency_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing rq coverage" in check["problems"]
    assert "missing table coverage" in check["problems"]
    assert "missing drift caveat" in check["problems"]


def test_submission_readiness_validates_parser_event_coverage_content(tmp_path):
    broken = tmp_path / "parser_event_coverage.md"
    broken.write_text("# Parser Event Coverage Audit\nReady: no\n", encoding="utf-8")

    check = check_parser_event_coverage_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing event kind coverage" in check["problems"]
    assert "missing phase coverage" in check["problems"]
    assert "missing future caveat" in check["problems"]


def test_submission_readiness_validates_failure_node_traceability_content(tmp_path):
    broken = tmp_path / "failure_node_traceability.md"
    broken.write_text("# Failure Node Traceability Audit\nReady: no\n", encoding="utf-8")

    check = check_failure_node_traceability_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing expected findings" in check["problems"]
    assert "missing finding event ids" in check["problems"]
    assert "missing benchmark traces" in check["problems"]
    assert "missing benchmark event ids" in check["problems"]
    assert "missing web highlight" in check["problems"]


def test_submission_readiness_validates_detector_evaluation_audit_content(tmp_path):
    broken = tmp_path / "detector_evaluation_audit.md"
    broken.write_text("# Detector Evaluation Audit\nReady: no\n", encoding="utf-8")

    check = check_detector_evaluation_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing controlled coverage" in check["problems"]
    assert "missing hard30 repetitive" in check["problems"]
    assert "missing hidden semantic" in check["problems"]
    assert "missing claim boundary verdicts" in check["problems"]
    assert "missing no majority outcome claim" in check["problems"]
    assert "missing hidden semantic contradicted" in check["problems"]


def test_submission_readiness_validates_rule_implementation_audit_content(tmp_path):
    broken = tmp_path / "rule_implementation_audit.md"
    broken.write_text("# Rule Implementation Audit\nReady: no\n", encoding="utf-8")

    check = check_rule_implementation_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage count" in check["problems"]
    assert "missing context proxy" in check["problems"]
    assert "missing detector signal column" in check["problems"]
    assert "missing verification detector signal" in check["problems"]
    assert "missing unrecovered error detector signal" in check["problems"]
    assert "missing context detector signal" in check["problems"]
    assert "missing semantic caveat" in check["problems"]


def test_submission_readiness_validates_rq4_signal_audit_content(tmp_path):
    broken = tmp_path / "rq4_signal_audit.md"
    broken.write_text("# RQ4 Signal Audit\nReady: no\n", encoding="utf-8")

    check = check_rq4_signal_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing fixture labels" in check["problems"]
    assert "missing hidden semantic boundary" in check["problems"]
    assert "missing recover phase" in check["problems"]
    assert "missing expected signal detail" in check["problems"]
    assert "missing verification detail" in check["problems"]
    assert "missing sandbox detail" in check["problems"]
    assert "missing rq4 signal verdicts" in check["problems"]
    assert "missing hidden semantic unsupported" in check["problems"]
    assert "missing task oracle pairing" in check["problems"]


def test_submission_readiness_validates_phase_coverage_audit_content(tmp_path):
    broken = tmp_path / "phase_coverage_audit.md"
    broken.write_text("# Phase Segmentation Coverage Audit\nReady: no\n", encoding="utf-8")

    check = check_phase_coverage_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing phase coverage" in check["problems"]
    assert "missing rq4 signals" in check["problems"]
    assert "missing run key" in check["problems"]


def test_submission_readiness_validates_task_category_coverage_content(tmp_path):
    broken = tmp_path / "task_category_coverage.md"
    broken.write_text("# Task Category Coverage Audit\nReady: no\n", encoding="utf-8")

    check = check_task_category_coverage_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing seed coverage" in check["problems"]
    assert "missing hard pool coverage" in check["problems"]
    assert "missing hard pool missing" in check["problems"]
    assert "missing task-count window" in check["problems"]
    assert "missing seed task-count window" in check["problems"]
    assert "missing hard task-count window" in check["problems"]
    assert "missing hard30 task-count window" in check["problems"]
    assert "missing category exemplars" in check["problems"]
    assert "missing seed exemplar" in check["problems"]
    assert "missing hard30 ci exemplar" in check["problems"]
    assert "missing test writing boundary exemplar" in check["problems"]
    assert "missing visible verification command" in check["problems"]
    assert "missing multi-turn change" in check["problems"]


def test_submission_readiness_validates_harness_protocol_audit_content(tmp_path):
    broken = tmp_path / "harness_protocol_audit.md"
    broken.write_text("# Harness Protocol Audit\nReady: no\n", encoding="utf-8")

    check = check_harness_protocol_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing prompt coverage" in check["problems"]
    assert "missing failure diagnosis" in check["problems"]


def test_submission_readiness_validates_failure_taxonomy_audit_content(tmp_path):
    broken = tmp_path / "failure_taxonomy_audit.md"
    broken.write_text("# Failure Taxonomy Coverage Audit\nReady: no\n", encoding="utf-8")

    check = check_failure_taxonomy_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage count" in check["problems"]
    assert "missing fixture f1" in check["problems"]
    assert "missing real pilot evidence tier" in check["problems"]
    assert "missing fixture only evidence tier" in check["problems"]
    assert "missing hard30 hidden semantic" in check["problems"]
    assert "missing rq1 distribution boundary" in check["problems"]
    assert "missing natural coverage plan" in check["problems"]
    assert "missing natural coverage unsupported" in check["problems"]
    assert "missing hidden semantic separate" in check["problems"]


def test_submission_readiness_validates_related_work_audit_content(tmp_path):
    broken = tmp_path / "related_work_audit.md"
    broken.write_text("# Related Work Coverage Audit\nReady: no\n", encoding="utf-8")

    check = check_related_work_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage count" in check["problems"]
    assert "missing swe bench" in check["problems"]


def test_submission_readiness_validates_bibliography_audit_content(tmp_path):
    broken = tmp_path / "bibliography_audit.md"
    broken.write_text("# Bibliography Audit\nReady: no\n", encoding="utf-8")

    check = check_bibliography_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing references section" in check["problems"]
    assert "missing coverage count" in check["problems"]


def test_submission_readiness_validates_paper_structure_audit_content(tmp_path):
    broken = tmp_path / "paper_structure_audit.md"
    broken.write_text("# Paper Structure Audit\nReady: no\n", encoding="utf-8")

    check = check_paper_structure_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage count" in check["problems"]
    assert "missing boundary framing" in check["problems"]


def test_submission_readiness_validates_reproducibility_audit_content(tmp_path):
    broken = tmp_path / "reproducibility_audit.md"
    broken.write_text("# Reproducibility Checklist Audit\nReady: no\n", encoding="utf-8")

    check = check_reproducibility_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing coverage count" in check["problems"]
    assert "missing semantic coverage count" in check["problems"]
    assert "missing balanced fences" in check["problems"]


def test_goal_completion_audit_keeps_original_goal_open():
    result = build_goal_completion_audit()
    markdown = render_goal_completion_audit_markdown(result)

    assert result["summary"]["original_goal_complete"] is False
    assert result["summary"]["boundary_result_paper_ready"] is True
    assert result["summary"]["should_mark_goal_complete"] is False
    assert result["summary"]["blocking_items"] == 1
    assert result["blocking_items"][0]["id"] == "verification_lift"
    assert "verification_behavior" in markdown
    assert "does not close ordinary verification-rate lift" in markdown
    assert "Should mark active goal complete: no" in markdown
    assert "Headroom audit: 98 non-ablation baseline run(s)" in markdown
    assert "ordinary expansion can close claim=no" in markdown
    assert "Revise the thesis to a boundary-result paper" in markdown
    assert "verification-lift-v2 retest is complete and remains saturated" in markdown


def test_verification_lift_next_experiment_audit_keeps_ablation_in_bounds():
    result = build_verification_lift_next_experiment_audit()
    markdown = render_verification_lift_next_experiment_markdown(result)

    assert result["ok"] is True
    assert result["original_verification_lift_closed"] is False
    assert result["next_experiment_required"] is False
    assert result["additional_ordinary_baseline_experiment_required"] is False
    assert result["claim_revision_required"] is True
    assert result["current_evidence"]["verification_lift"]["verification_delta"] == 0
    assert result["current_evidence"]["verification_lift"]["success_check_verification_delta"] == 0
    assert result["current_evidence"]["verification_lift"]["baseline_saturated"] is True
    assert result["current_evidence"]["verification_ablation"]["verification_delta"] == 1
    assert result["current_evidence"]["verification_ablation"]["success_check_verification_delta"] == 1
    assert result["current_evidence"]["verification_lift_v2"]["exists"] is True
    assert result["current_evidence"]["verification_lift_v2"]["verification_delta"] == 0
    assert result["current_evidence"]["verification_lift_v2"]["success_check_verification_delta"] == 0
    assert result["current_evidence"]["verification_lift_v2"]["baseline_saturated"] is True
    assert result["prompt_constraints"]["ablation_baseline_forbids_verification"] is True
    assert result["planned_v2_scaffold"]["ready"] is True
    assert result["planned_v2_scaffold"]["pilot_collected"] is True
    assert result["planned_v2_scaffold"]["task_count"] == 8
    assert result["planned_v2_scaffold"]["baseline_prompt_is_ordinary"] is True
    assert result["planned_v2_scaffold"]["intervention_is_evidence_gated"] is True
    assert any(gate["id"] == "ordinary_baseline" for gate in result["acceptance_gates"])
    assert "No-verify ablation cannot close the ordinary-baseline claim" in markdown
    assert "Additional ordinary-baseline experiment required: no" in markdown
    assert "Claim revision required: yes" in markdown
    assert "Planned Ordinary-Baseline V2 Scaffold" in markdown


def test_verification_saturation_audit_bounds_ordinary_lift_claim():
    result = build_verification_saturation_audit()
    markdown = render_verification_saturation_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["summary"]["non_ablation_tier_count"] == 6
    assert result["summary"]["saturated_non_ablation_tier_count"] == 6
    assert result["summary"]["ordinary_verification_lift_supported"] is False
    assert result["summary"]["ordinary_exact_verification_lift_supported"] is False
    assert result["summary"]["ablation_mechanism_positive"] is True
    assert all(row["verification_delta"] == 0 for row in result["non_ablation_tiers"])
    assert all(row["success_check_verification_delta"] == 0 for row in result["non_ablation_tiers"])
    assert result["ablation"]["verification_delta"] == 1
    assert result["ablation"]["success_check_verification_delta"] == 1
    assert "cannot close the ordinary-baseline claim" in markdown


def test_verification_lift_power_audit_quantifies_saturated_headroom():
    result = build_verification_lift_power_audit()
    markdown = render_verification_lift_power_markdown(result)
    summary = result["summary"]

    assert summary["ready"] is True
    assert summary["baseline_runs"] == 98
    assert summary["baseline_unverified_broad"] == 0
    assert summary["baseline_unverified_exact"] == 0
    assert summary["empirical_rate_headroom"] == 0
    assert summary["expected_table_compatible"] is False
    assert summary["ordinary_expansion_can_close_claim"] is False
    assert summary["rule_of_three_nonverification_upper_bound"] < summary["expected_table_delta"]
    assert "Expected 51% -> 83% table compatible: no" in markdown
    assert "0/98 broad baseline runs lack verification" in markdown
    assert "not a substitute for a new positive experiment" in markdown


def test_submission_readiness_validates_verification_lift_power_audit_content(tmp_path):
    broken = tmp_path / "verification_lift_power_audit.md"
    broken.write_text("# Missing\n", encoding="utf-8")

    check = check_verification_lift_power_audit_content(broken)

    assert check["ok"] is False
    assert "missing baseline run count" in check["problems"]
    assert "missing expected table incompatible" in check["problems"]


def test_submission_readiness_validates_verification_lift_next_experiment_content(tmp_path):
    broken = tmp_path / "verification_lift_next_experiment.md"
    broken.write_text("# Verification-Lift Next Experiment Audit\nOriginal verification-lift claim closed: yes\n", encoding="utf-8")

    check = check_verification_lift_next_experiment_content(broken)

    assert check["ok"] is False
    assert "missing original claim still open" in check["problems"]
    assert "missing claim revision required" in check["problems"]
    assert "missing no additional ordinary experiment" in check["problems"]


def test_submission_readiness_validates_verification_saturation_audit_content(tmp_path):
    broken = tmp_path / "verification_saturation_audit.md"
    broken.write_text("# Verification Saturation Audit\nReady: no\n", encoding="utf-8")

    check = check_verification_saturation_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing saturated tiers" in check["problems"]
    assert "missing ordinary lift unsupported" in check["problems"]
    assert "missing ablation positive" in check["problems"]
    assert "missing claim closure caveat" in check["problems"]


def test_verification_behavior_audit_captures_saturated_rate_process_effect():
    result = build_verification_behavior_audit()
    markdown = render_verification_behavior_markdown(result)
    verdicts = {row["claim"]: row for row in result["claim_boundaries"]}

    assert result["summary"]["ready"] is True
    assert result["summary"]["saturated_non_ablation_tier_count"] == 6
    assert result["summary"]["earlier_verification_count"] == 6
    assert result["summary"]["leaner_verify_phase_count"] == 6
    assert verdicts["Harness intervention improves ordinary-baseline verification rate."]["verdict"] == "unsupported"
    assert verdicts["Harness intervention reaches verification earlier under saturated ordinary pilots."]["verdict"] == "supported"
    assert verdicts["Harness intervention makes ordinary-pilot verification deeper."]["verdict"] == "contradicted"
    assert verdicts["No-verify ablation shows harness control over verification behavior."]["verdict"] == "mechanism-check-only"
    assert "Non-ablation tiers with earlier verification: 6 / 6" in markdown
    assert "Use leaner verification path, not deeper verification." in markdown


def test_submission_readiness_validates_verification_behavior_audit_content(tmp_path):
    broken = tmp_path / "verification_behavior_audit.md"
    broken.write_text("# Verification Behavior Audit\nReady: no\n", encoding="utf-8")

    check = check_verification_behavior_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing saturated tiers" in check["problems"]
    assert "missing earlier verification" in check["problems"]
    assert "missing leaner verify phase" in check["problems"]
    assert "missing not deeper verification" in check["problems"]


def test_submission_readiness_validates_verification_ablation_plan_audit_content(tmp_path):
    broken = tmp_path / "verification_ablation_plan_audit.md"
    broken.write_text("# Verification Ablation Plan Audit\nReady: no\n", encoding="utf-8")

    check = check_verification_ablation_plan_audit_content(broken)

    assert check["ok"] is False
    assert "missing ready" in check["problems"]
    assert "missing task count" in check["problems"]
    assert "missing materialized fixtures" in check["problems"]


def test_submission_readiness_validates_goal_completion_audit_content(tmp_path):
    broken = tmp_path / "goal_completion_audit.md"
    broken.write_text("# Goal Completion Audit\nOriginal goal complete: yes\n", encoding="utf-8")

    check = check_goal_completion_audit_content(broken)

    assert check["ok"] is False
    assert "missing original incomplete" in check["problems"]
    assert "missing do not complete" in check["problems"]


def test_process_stress_plan_covers_target_failure_tags():
    result = audit_process_stress_plan()

    assert result["ok"] is True
    assert result["task_count"] == 12
    assert result["materialized_count"] == 12
    assert result["tag_counts"] == {
        "verification_gap": 3,
        "unrecovered_tool_error": 3,
        "repetitive_exploration": 3,
        "context_drift": 3,
        "premature_completion": 4,
        "sandbox_permission_deadlock": 2,
    }


def test_verification_lift_plan_covers_prompt_contrast():
    result = audit_verification_lift_plan()
    tasks = load_tasks("benchmark/verification-lift/tasks.jsonl")
    baseline_prompt = render_prompt(tasks[0], "baseline", "benchmark/verification-lift/prompts")
    intervention_prompt = render_prompt(tasks[0], "intervention", "benchmark/verification-lift/prompts")

    assert result["ok"] is True
    assert result["task_count"] == 8
    assert result["materialized_count"] == 8
    assert result["tag_counts"]["verification_gap"] == 8
    assert "skip command execution" in baseline_prompt
    assert "Run the visible success check" in intervention_prompt


def test_verification_lift_v2_plan_covers_ordinary_baseline_contrast():
    result = audit_verification_lift_v2_plan()
    tasks = load_tasks("benchmark/verification-lift-v2/tasks.jsonl")
    baseline_prompt = render_prompt(tasks[0], "baseline", "benchmark/verification-lift-v2/prompts")
    intervention_prompt = render_prompt(tasks[0], "intervention", "benchmark/verification-lift-v2/prompts")

    assert result["ok"] is True
    assert result["task_count"] == 8
    assert result["materialized_count"] == 8
    assert result["tag_counts"]["verification_gap"] == 8
    assert result["baseline_prompt_is_ordinary"] is True
    assert result["intervention_is_evidence_gated"] is True
    assert result["forbidden_baseline_phrase_hits"] == []
    assert "normal coding workflow" in baseline_prompt
    assert "use your judgment" in baseline_prompt
    assert "skip command execution" not in baseline_prompt
    assert "Do not run test" not in baseline_prompt
    assert "Run the visible success check" in intervention_prompt


def test_verification_ablation_plan_covers_no_verify_prompt_contrast():
    result = audit_verification_ablation_plan()
    tasks = load_tasks("benchmark/verification-ablation/tasks.jsonl")
    baseline_prompt = render_prompt(tasks[0], "baseline", "benchmark/verification-ablation/prompts")
    intervention_prompt = render_prompt(tasks[0], "intervention", "benchmark/verification-ablation/prompts")

    assert result["ok"] is True
    assert result["task_count"] == 4
    assert result["materialized_count"] == 4
    assert "Do not run test, build, lint, grader" in baseline_prompt
    assert "Run the visible success check" in intervention_prompt


def test_rq4_signal_audit_explains_boundary_and_process_signals():
    result = build_rq4_signal_audit()
    markdown = render_rq4_signal_audit_markdown(result)

    assert result["summary"]["ready"] is True
    assert result["hard30_hidden_boundary"]["verification_delta_success_minus_failure"] == 0
    assert result["hard30_hidden_boundary"]["success_check_verification_delta_success_minus_failure"] == 0
    assert result["hard30_hidden_boundary"]["unresolved_error_delta_success_minus_failure"] == 0
    assert result["summary"]["detector_fixture_label_count"] == 6
    assert result["summary"]["detector_fixture_expected_signal_failures"] == 0
    assert result["summary"]["detector_fixture_expected_signal_checks"] == 6
    assert result["hard30_hidden_boundary"]["false_negatives"] == 30
    assert result["hard30_hidden_boundary"]["recall"] == 0
    assert len(result["detector_fixture_expected_signal_details"]) == 18
    detail_keys = {
        (row["label"], row["signal"])
        for row in result["detector_fixture_expected_signal_details"]
    }
    assert ("verification_gap", "time_to_first_test") in detail_keys
    assert ("sandbox_permission_deadlock", "phase_recover_events") in detail_keys
    assert ("repetitive_exploration", "repeated_tool_call_count") in detail_keys
    assert result["hard30_repetitive_exploration_top_signals"][0]["signal"] == "token_usage"
    assert any(row["signal"] == "repeated_tool_call_count" for row in result["hard30_repetitive_exploration_top_signals"])
    assert any(row["signal"] == "phase_recover_events" for row in result["full30_sandbox_permission_top_signals"])
    expected_checks = {
        row["label"]: row
        for row in result["detector_fixture_expected_signal_checks"]
    }
    assert expected_checks["repetitive_exploration"]["nonzero_expected_signals"] >= 2
    assert expected_checks["sandbox_permission_deadlock"]["nonzero_expected_signals"] == 3
    assert expected_checks["verification_gap"]["passed"] is True
    signal_verdicts = {row["claim"]: row for row in result["signal_verdicts"]}
    assert signal_verdicts["Trace signals explain controlled observable process labels."]["verdict"] == "supported"
    assert signal_verdicts["Trace signals explain observed real process positives."]["verdict"] == "supported-with-boundary"
    assert signal_verdicts["Trace signals predict hidden semantic outcome failures."]["verdict"] == "unsupported"
    assert "FN=30" in signal_verdicts["Trace signals predict hidden semantic outcome failures."]["evidence"]
    assert signal_verdicts["Failure score or token usage alone ranks hidden correctness."]["verdict"] == "unsupported"
    assert "Hidden Semantic Boundary" in markdown
    assert "Hard30 hidden semantic false negatives: 30" in markdown
    assert "| detector_recall | 0.00 | Process detectors miss 30 hidden semantic failures. |" in markdown
    assert "Expected Label-Signal Checks" in markdown
    assert "Expected Signal Detail" in markdown
    assert "RQ4 Signal Verdicts" in markdown
    assert "Claim explanation for reviewed observable process positives, not all outcomes" in markdown
    assert "Keep token/failure-score claims process-scoped and pair them with task oracles" in markdown
    assert "| verification_gap | time_to_first_test |" in markdown
    assert "| sandbox_permission_deadlock | phase_recover_events |" in markdown
    assert "Expected label-signal checks passed: 6 / 6" in markdown


def test_process_stress_fixtures_start_failing_visible_checks():
    tasks = load_tasks("benchmark/process-stress/tasks.jsonl")
    results = [run_success_check(task.fixture_path, task.public_success_check, timeout_seconds=30) for task in tasks]

    assert len(results) == 12
    assert all(result.returncode != 0 for result in results)


def test_smoke_fixture_success_check_starts_failing():
    tasks = {task.task_id: task for task in load_tasks("benchmark/smoke/tasks.jsonl")}

    result = run_success_check(tasks["SM-001"].fixture_path, tasks["SM-001"].success_check)

    assert result.returncode != 0
    assert "FAILED" in result.stdout or "FAIL" in result.stdout


def test_dry_run_materializes_prompts_and_manifest(tmp_path):
    rows = run_benchmark(
        tasks_path="benchmark/smoke/tasks.jsonl",
        output_dir=tmp_path,
        prompt_types=["intervention"],
        task_ids=["SM-001"],
        dry_run=True,
    )
    manifest = tmp_path / "runs.jsonl"
    write_run_manifest(rows, manifest)

    prompt = tmp_path / "SM-001" / "intervention" / "prompt.md"
    repo_file = tmp_path / "SM-001" / "intervention" / "repo" / "src" / "calc.py"
    git_dir = tmp_path / "SM-001" / "intervention" / "repo" / ".git"

    assert len(rows) == 1
    assert rows[0]["outcome"] == "not_run"
    assert prompt.exists()
    assert repo_file.exists()
    assert git_dir.exists()
    assert "Run a focused verification command after the edit" in prompt.read_text(encoding="utf-8")
    assert manifest.read_text(encoding="utf-8").count("\n") == 1


def test_dry_run_materializes_external_grader(tmp_path):
    repo = tmp_path / "repo"
    grader = tmp_path / "grader"
    repo.mkdir()
    grader.mkdir()
    (repo / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
    (grader / "check.py").write_text("print('ok')\n", encoding="utf-8")
    tasks = tmp_path / "tasks.jsonl"
    tasks.write_text(
        '{"task_id":"T-001","category":"bug_fix","fixture_path":"repo","grader_path":"grader",'
        '"repo_hint":"python/example","instruction":"Fix the value.",'
        '"public_success_check":"python3 -m unittest discover -s tests",'
        '"success_check":"python3 ../grader/check.py"}\n',
        encoding="utf-8",
    )

    rows = run_benchmark(
        tasks_path=tasks,
        output_dir=tmp_path / "runs",
        prompt_types=["baseline"],
        dry_run=True,
    )

    copied_grader = tmp_path / "runs" / "T-001" / "baseline" / "grader" / "check.py"
    prompt = tmp_path / "runs" / "T-001" / "baseline" / "prompt.md"

    assert rows[0]["grader_path"] == "T-001/baseline/grader"
    assert copied_grader.exists()
    assert "../grader" not in prompt.read_text(encoding="utf-8")
    assert "python3 -m unittest discover -s tests" in prompt.read_text(encoding="utf-8")
