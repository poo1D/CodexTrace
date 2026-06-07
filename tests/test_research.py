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

    assert len(tasks) == 26
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
