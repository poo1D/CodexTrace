# Failure Taxonomy

This taxonomy defines observable multi-turn tool-use failures for coding agents.
The unit of analysis is a `codex exec --json` trace, not only the final answer.

## Labels

### verification_gap

The agent edits files but does not run a relevant test, build, lint, type-check,
or smoke command after the last edit.

Trace signal:

- at least one `file_change`
- zero post-edit verification commands

Why it matters:

- the final answer may sound confident even though no evidence supports it

### unrecovered_tool_error

A command or tool call fails and the trace shows no clear recovery step.

Trace signal:

- non-zero command exit
- no later successful related command or verification command

Why it matters:

- agents often continue after tool failures as if they had useful evidence

### repetitive_exploration

The agent repeatedly searches or reads the same target without new information.

Trace signal:

- repeated normalized `rg`, `grep`, `find`, `ls`, `sed`, or `cat` commands

Why it matters:

- repeated exploration is a measurable form of token/tool-call waste

### context_drift

Later commands or edits become weakly related to the original task.

Trace signal for v1:

- high context usage
- low implementation progress
- no file edits or verification despite many prompt/trace tokens

Future signal:

- compare task keywords against command/file/edit terms

### premature_completion

The agent claims completion before producing verification evidence.

Trace signal for v1:

- final agent message contains completion language
- no post-edit verification command

Future signal:

- require explicit evidence citation in final answer

### sandbox_permission_deadlock

The trace repeatedly hits permission, network, approval, or sandbox errors and
does not change strategy.

Trace signal:

- failed or blocked command containing sandbox/permission words
- no later scoped alternative or approval request

Why it matters:

- this is a harness failure, not purely a model reasoning failure
