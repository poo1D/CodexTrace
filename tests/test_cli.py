from codex_trace.cli import main


def test_label_template_cli_writes_output(tmp_path, capsys):
    output = tmp_path / "labels.jsonl"

    assert main(["research", "label-template", "benchmark/runs.example.jsonl", "--output", str(output)]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert output.read_text(encoding="utf-8").count("\n") == 4


def test_aggregate_csv_output_does_not_print_markdown(tmp_path, capsys):
    output = tmp_path / "runs.csv"

    assert main(["research", "aggregate", "benchmark/runs.example.jsonl", "--csv-output", str(output)]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "taxonomy_tags" in output.read_text(encoding="utf-8").splitlines()[0]


def test_paper_report_cli_writes_markdown(tmp_path, capsys):
    output = tmp_path / "paper-report.md"

    assert main([
        "research",
        "paper-report",
        "benchmark/runs.example.jsonl",
        "--labels",
        "benchmark/labels.example.jsonl",
        "--markdown-output",
        str(output),
    ]) == 0

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "RQ3 Baseline vs Intervention" in output.read_text(encoding="utf-8")
