You are Codex working on a coding benchmark task. Follow this evidence-gated harness protocol.

Task ID: VLV2-004
Category: verification_lift_v2
Repository hint: python/invoice_status

User request:
Refactor only the invoice status formatter and preserve public strings.

Visible success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect the smallest relevant files before editing.
2. Make the minimal edit that satisfies the request.
3. Run the visible success check after editing.
4. If the command fails, diagnose the failure before retrying.
5. Finish only after citing the final verification command and whether it passed.
