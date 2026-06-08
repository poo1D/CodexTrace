You are Codex working on a coding benchmark task. Follow this harness protocol.

Task ID: HARD-033
Category: error_recovery
Repository hint: python/log_redactor

User request:
Fix the log redactor so it consistently redacts credentials from plain text and structured log events without mutating inputs. It must handle token, apiKey, password, and authorization values across key-value text, URL query strings, headers, and JSON-like dictionaries.

Success check:
python3 -m unittest discover -s tests

Protocol:
1. Inspect first: identify the smallest relevant files before editing.
2. State the intended minimal edit before changing files.
3. Make the smallest change that satisfies the task.
4. Run a focused verification command after the edit.
5. If any command fails, diagnose the cause before retrying.
6. Finish only after citing concrete evidence from the final verification.
