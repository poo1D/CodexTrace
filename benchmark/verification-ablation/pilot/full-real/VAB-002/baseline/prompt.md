You are Codex working on a coding benchmark ablation task.

Task ID: VAB-002
Category: verification_ablation
Repository hint: python/cli_args

User request:
Add validation for the CLI argument parser while preserving existing behavior.

Visible success check, for reference only:
python3 -m unittest discover -s tests

Ablation protocol:
- Inspect and edit normally.
- Do not run test, build, lint, grader, or other verification commands.
- Finish after the minimal edit and describe what you changed.
