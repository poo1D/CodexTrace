You are Codex working on a coding benchmark ablation task. Follow this evidence-gated harness protocol.

Task ID: VAB-002
Category: verification_ablation
Repository hint: python/cli_args

User request:
Add validation for the CLI argument parser while preserving existing behavior.

Visible success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect the smallest relevant files before editing.
2. Make the minimal edit that satisfies the request.
3. Run the visible success check after editing.
4. If the command fails, diagnose the failure before retrying.
5. Finish only after citing the final verification command and whether it passed.
