# Parser Event Coverage Audit

This generated audit checks that the JSONL parser normalizes the event variants used by CodexTrace reports and paper-facing schema claims.

## Summary

- Ready: yes
- Synthetic events parsed: 16
- Event kinds covered: 11 / 11
- Phases covered: 7 / 7
- Parser source markers covered: 11 / 11
- Parser source: `codex_trace/parser.py`
- Schema source: `codex_trace/schema.py`
- Paper draft: `docs/paper_draft.md`

## Event Kind Coverage

| Event kind | Present | Events |
| --- | --- | ---: |
| `thread` | yes | 1 |
| `turn` | yes | 2 |
| `agent_message` | yes | 2 |
| `reasoning` | yes | 1 |
| `command` | yes | 3 |
| `file_change` | yes | 1 |
| `mcp_tool` | yes | 1 |
| `web_search` | yes | 1 |
| `plan` | yes | 1 |
| `error` | yes | 1 |
| `unknown` | yes | 2 |

## Phase Coverage

| Phase | Present | Events |
| --- | --- | ---: |
| `setup` | yes | 4 |
| `inspect` | yes | 3 |
| `edit` | yes | 1 |
| `verify` | yes | 2 |
| `recover` | yes | 3 |
| `complete` | yes | 2 |
| `other` | yes | 1 |

## Feature Checks

| Feature | Covered |
| --- | --- |
| `thread_id` | yes |
| `usage_input_tokens` | yes |
| `usage_output_tokens` | yes |
| `failed_command_status` | yes |
| `file_paths` | yes |
| `mcp_tool_name` | yes |
| `web_search_query` | yes |
| `schema_event_kind_literal` | yes |
| `paper_pipeline_mentions_parser` | yes |
| `paper_schema_mentions_event_type` | yes |

Interpretation: this audit covers parser branch coverage for the normalized event schema. It does not claim compatibility with every future Codex JSONL variant; unknown events are preserved as `unknown` with raw metadata.
