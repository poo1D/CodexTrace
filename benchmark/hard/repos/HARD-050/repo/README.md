# config-overlay-resolver

`resolve_config(defaults, env=None, cli=None, schema=None)`
builds an application config from default values plus runtime
overrides.

Requirements:

- deep-copy defaults before applying overrides
- environment variables start with `APP_`
- double underscores in env names map to nested paths:
  `APP_SERVER__PORT` -> `server.port`
- CLI keys use dotted paths: `server.port`
- CLI overrides environment values
- `schema` maps dotted paths to types such as `bool`, `int`,
  `float`, `str`, or `list`
- explicit false and zero values must override defaults
- unknown paths raise `ConfigError`
- inputs must not be mutated
