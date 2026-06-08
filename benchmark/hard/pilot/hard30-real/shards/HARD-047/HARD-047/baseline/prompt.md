You are Codex working on a coding benchmark task.

Task ID: HARD-047
Category: stateful_regression
Repository hint: python/webhook_replay_guard

User request:
Fix the webhook replay guard so signed webhook envelopes are accepted only once per tenant within the replay window. Preserve verify_event(envelope, keys, store, now), verify HMAC-SHA256 signatures over the exact raw body text, enforce timestamp skew, support signing-key rotation, prune expired seen ids, and do not mutate the envelope or keys inputs. Use only the Python standard library.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
