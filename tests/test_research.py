from codex_trace.research import (
    aggregate_runs,
    evaluate_detector_labels,
    generate_label_template,
    load_tasks,
    render_label_template_jsonl,
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


def test_aggregate_runs_baseline_vs_intervention():
    result = aggregate_runs("tests/fixtures/research/runs.jsonl")

    assert result["summary"]["baseline"]["n"] == 1
    assert result["summary"]["intervention"]["n"] == 1
    assert result["summary"]["baseline"]["success_rate"] == 0
    assert result["summary"]["intervention"]["success_rate"] == 1
    assert result["summary"]["baseline"]["avg_failure_score"] > result["summary"]["intervention"]["avg_failure_score"]
    assert result["deltas"]["success_rate"] == 1


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
