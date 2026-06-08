You are Codex working on a coding benchmark task.

Task ID: HARD-033
Category: error_recovery
Repository hint: python/log_redactor

User request:
Fix the log redactor so it consistently redacts credentials from plain text and structured log events without mutating inputs. It must handle token, apiKey, password, and authorization values across key-value text, URL query strings, headers, and JSON-like dictionaries.

Success check:
python3 -m unittest discover -s tests

Complete the task with your normal coding workflow.
