You are Codex working on a coding benchmark task. Follow this evidence-gated harness protocol.

Task ID: VLV2-001
Category: verification_lift_v2
Repository hint: python/report_averages

User request:
Fix the aggregate-report average bug with the smallest local code change.

Visible success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect the smallest relevant files before editing.
2. Make the minimal edit that satisfies the request.
3. Run the visible success check after editing.
4. If the command fails, diagnose the failure before retrying.
5. Finish only after citing the final verification command and whether it passed.
