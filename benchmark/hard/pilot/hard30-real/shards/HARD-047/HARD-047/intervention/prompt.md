You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-047
Category: stateful_regression
Repository hint: python/webhook_replay_guard

User request:
Fix the webhook replay guard so signed webhook envelopes are accepted only once per tenant within the replay window. Preserve verify_event(envelope, keys, store, now), verify HMAC-SHA256 signatures over the exact raw body text, enforce timestamp skew, support signing-key rotation, prune expired seen ids, and do not mutate the envelope or keys inputs. Use only the Python standard library.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
