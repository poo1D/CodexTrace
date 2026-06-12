You are Codex working on a coding benchmark ablation task.

Task ID: VAB-003
Category: verification_ablation
Repository hint: python/settings_precedence

User request:
Fix the settings precedence bug with the smallest code edit.

Visible success check, for reference only:
python3 -m unittest discover -s tests

Ablation protocol:
- Inspect and edit normally.
- Do not run test, build, lint, grader, or other verification commands.
- Finish after the minimal edit and describe what you changed.
