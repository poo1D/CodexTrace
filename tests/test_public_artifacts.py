from scripts.check_public_artifacts import ROOT, find_violations, tracked_paths


def test_rejects_raw_stderr_and_personal_home_paths(tmp_path):
    stderr = tmp_path / "codex.stderr"
    stderr.write_text("runtime log", encoding="utf-8")
    report = tmp_path / "report.json"
    account = "alice"
    personal_path = "/" + "Users" + f"/{account}/project"
    report.write_text(f'{{"workdir":"{personal_path}"}}', encoding="utf-8")
    trace = tmp_path / "trace.jsonl"
    permissions = "-rw-r--r--"
    trace.write_text(
        f'{{"output":"total 8\\n{permissions}  1 {account}  staff  10 Jul 11 00:00 note.txt"}}',
        encoding="utf-8",
    )
    secret = tmp_path / "secret.txt"
    secret.write_text("sk-" + ("A" * 32), encoding="utf-8")

    violations = find_violations([stderr, report, trace, secret], root=tmp_path)

    assert [violation.reason for violation in violations] == [
        "raw codex.stderr must not be tracked",
        "machine-specific home path uses non-placeholder account 'alice'",
        "captured directory listing uses non-placeholder owner 'alice'",
        "possible OpenAI-style API key in tracked text",
    ]


def test_allows_explicit_home_path_placeholders(tmp_path):
    fixture = tmp_path / "trace.jsonl"
    fixture.write_text(
        "\n".join([
            '{"cache":"/Users/REDACTED/Library/Caches/pip"}',
            '{"workspace":"/home/runner/work/CodexTrace"}',
            '{"example":"C:/Users/EXAMPLE/project"}',
        ]),
        encoding="utf-8",
    )

    assert find_violations([fixture], root=tmp_path) == []


def test_tracked_public_tree_passes_hygiene_gate():
    # This covers the exact tracked tree that a pull request publishes.
    assert find_violations(tracked_paths(ROOT), root=ROOT) == []
