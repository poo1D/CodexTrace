import json
from pathlib import Path

from scripts.finalize_hard30_pilot import finalize, preflight, render_preflight
from scripts.audit_manual_labels import audit_manual_labels, render_audit
from scripts.audit_paper_claims import build_claim_audit, render_claim_audit_markdown
from scripts.audit_process_stress_plan import audit_process_stress_plan
from scripts.audit_rq4_signals import build_rq4_signal_audit, render_rq4_signal_audit_markdown
from scripts.audit_thesis_readiness import build_thesis_readiness, render_thesis_readiness_markdown
from scripts.audit_verification_ablation_plan import audit_verification_ablation_plan
from scripts.audit_verification_lift_plan import audit_verification_lift_plan
from scripts.merge_hard30_shards import merge_shards, rewrite_shard_row
from scripts.run_hard30_shards import (
    build_shard_commands,
    filter_commands,
    inspect_shard,
    render_status,
    select_task_ids,
    summarize_shards,
)
from scripts.check_submission_readiness import build_report, render_report

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
    assert "submission-ready hard30 artifact" in report["positioning"]


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
    assert "Outcome counts: failure=2, success=2, unknown=0." in markdown


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
    assert result["hard10_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 5
    assert result["hard30_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 30
    assert result["hard30_label_evaluation"]["labels"]["repetitive_exploration"]["tp"] == 4
    assert result["process_stress"]["summary"]["baseline"]["n"] == 12
    assert result["process_stress"]["summary"]["baseline"]["success_rate"] == 0.9167
    assert result["process_stress_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 2
    assert result["verification_lift"]["summary"]["baseline"]["n"] == 8
    assert result["verification_lift"]["summary"]["baseline"]["verification_rate"] == 1
    assert result["verification_lift_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 2
    assert result["verification_ablation"]["summary"]["baseline"]["n"] == 4
    assert result["verification_ablation"]["deltas"]["verification_rate"] == 1
    assert result["verification_ablation_label_evaluation"]["labels"]["verification_gap"]["tp"] == 4
    assert result["verification_ablation_label_evaluation"]["labels"]["premature_completion"]["tp"] == 3
    assert "## RQ3 Baseline vs Intervention" in markdown
    assert "### Hard30 Pilot" in markdown
    assert "### Process-Stress Pilot" in markdown
    assert "### Verification-Lift Pilot" in markdown
    assert "### Verification Ablation Pilot" in markdown
    assert "### Full30 Process-Positive Detector Check" in markdown
    assert "### Controlled Detector Fixture Check" in markdown
    assert "## RQ4 Trace Signals By Outcome" in markdown
    assert "| failure_score | 1.833 | 2.833 | 1 |" in markdown
    assert "hidden_semantic_edge_case" in markdown
    assert "repetitive_exploration" in markdown
    assert "30 false negatives" in markdown
    assert "2 trace-only false negatives" in markdown
    assert "verification remains 100% -> 100%" in markdown


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
    assert result["summary"]["verification_ablation_tasks"] == 4
    assert result["summary"]["verification_ablation_runs"] == 8
    assert result["summary"]["verification_ablation_verification_delta"] == 1
    assert result["summary"]["rq4_signal_audit_ready"] is True
    assert result["summary"]["status_counts"]["supported"] >= 3
    assert claims["Harness intervention increases verification rate."]["status"] == "unsupported"
    assert claims["Harness constraints can control verification behavior under a no-verify ablation."]["status"] == "supported"
    assert claims["Trace-based process rules detect most failure processes."]["status"] == "partial"
    assert claims["Trace signals explain observable process failures and the hidden-semantic boundary."]["status"] == "supported"
    assert claims["Harness intervention increases success rate."]["status"] == "partial"
    assert claims["Harness intervention reduces repeated tool-call and token waste."]["status"] == "supported"
    assert "Do not state `unsupported` claims as findings" in markdown


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
    assert requirements["rq4_explanation"]["status"] == "satisfied"
    assert result["summary"]["status_counts"]["satisfied"] == 6
    assert "full30 sandbox_permission_deadlock has TP=1" in markdown
    assert "controlled detector fixtures cover 6 labels" in markdown
    assert "Boundary-style RQ4 is supported" in markdown
    assert "process-stress tier" in markdown
    assert "verification-lift tier" in markdown
    assert "verification is saturated" in markdown
    assert result["next_experiment"]["current_scaffold"]["ready"] is True
    assert result["verification_lift_experiment"]["current_scaffold"]["ready"] is True
    assert result["verification_lift_experiment"]["current_scaffold"]["task_count"] == 8
    verification_pilot = result["verification_lift_experiment"]["current_scaffold"]["pilot"]
    assert verification_pilot["tasks"] == 8
    assert verification_pilot["runs"] == 16
    assert verification_pilot["baseline_verification_rate"] == verification_pilot["intervention_verification_rate"]
    ablation_pilot = result["verification_ablation_experiment"]["current_scaffold"]["pilot"]
    assert ablation_pilot["tasks"] == 4
    assert ablation_pilot["runs"] == 8
    assert ablation_pilot["baseline_verification_rate"] == 0
    assert ablation_pilot["intervention_verification_rate"] == 1
    pilot = result["next_experiment"]["current_scaffold"]["pilot"]
    assert pilot["tasks"] == 12
    assert pilot["runs"] == 24
    assert pilot["baseline_success_rate"] == pilot["intervention_success_rate"]
    assert pilot["baseline_repeated_calls"] > pilot["intervention_repeated_calls"]
    assert pilot["baseline_token_usage"] > pilot["intervention_token_usage"]


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
    assert result["hard30_hidden_boundary"]["unresolved_error_delta_success_minus_failure"] == 0
    assert result["summary"]["detector_fixture_label_count"] == 6
    assert result["hard30_repetitive_exploration_top_signals"][0]["signal"] == "token_usage"
    assert any(row["signal"] == "repeated_tool_call_count" for row in result["hard30_repetitive_exploration_top_signals"])
    assert any(row["signal"] == "phase_recover_events" for row in result["full30_sandbox_permission_top_signals"])
    assert "Hidden Semantic Boundary" in markdown


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
