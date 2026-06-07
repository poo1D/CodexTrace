import json
from pathlib import Path

from scripts.finalize_hard30_pilot import finalize

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
        "labels.jsonl",
        "paper-report.json",
        "paper-report.md",
    }
    assert {path.name for path in written} == expected
    assert all((tmp_path / name).exists() for name in expected)
    assert "suggested_tags" in (tmp_path / "labels.jsonl").read_text()


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
    assert any(row["signal"] == "phase_recover_events" for row in result["signal_by_outcome"])
    assert "## RQ4 Trace Signals By Outcome" in markdown
    assert "Outcome counts: failure=2, success=2, unknown=0." in markdown


def test_build_results_summary_from_stored_pilots():
    result = build_results_summary(
        "benchmark/pilot/full30-real/runs.jsonl",
        "benchmark/hard/pilot/hard10-real/runs.jsonl",
        "benchmark/hard/pilot/hard10-real/manual-labels.jsonl",
    )
    markdown = render_results_summary_markdown(result)

    assert result["full30"]["summary"]["baseline"]["n"] == 30
    assert result["hard10"]["summary"]["baseline"]["success_rate"] == 0.7
    assert result["hard10_label_evaluation"]["labels"]["hidden_semantic_edge_case"]["fn"] == 5
    assert "## RQ3 Baseline vs Intervention" in markdown
    assert "## RQ4 Trace Signals By Outcome" in markdown
    assert "| failure_score | 0 | 0 | 0 |" in markdown
    assert "hidden_semantic_edge_case" in markdown


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
