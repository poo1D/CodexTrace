You are Codex working on a coding benchmark task. Follow this evidence-gated harness protocol.

Task ID: VLT-008
Category: verification_lift
Repository hint: python/cache_paths

User request:
Repair the helper so cache files go under the repo-local .cache directory.

Visible success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect the smallest relevant files before editing.
2. Make the minimal edit that satisfies the request.
3. Run the visible success check after editing.
4. If the command fails, diagnose the failure before retrying.
5. Finish only after citing the final verification command and whether it passed.
