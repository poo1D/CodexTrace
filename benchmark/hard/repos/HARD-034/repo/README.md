# feature-flags

`evaluate_flag(config, flag_name, user)` decides whether a
feature flag is enabled for a user.

Current behavior:

- Missing flags return `config["default"]` when present.
- Boolean `enabled` controls simple flags.

Required extension:

- `allow_users` always enables listed users.
- `deny_users` always disables listed users.
- `rollout` is an integer percentage from 0 to 100.
- Rollout decisions must be deterministic across processes.
- The input config and user dictionaries must not be mutated.
