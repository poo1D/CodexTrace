# icu-plural-format

`formatMessage(message, values)` formats a small subset of ICU
messages.

Supported syntax:

- `{name}` interpolation
- `{count, plural, one {...} other {...}}`
- Exact plural arms such as `=0 {...}`
- Optional plural offsets such as `offset:1`
- `#` substitution inside plural arms after applying offset
- Apostrophe escaping for literal braces and quotes

Missing interpolation or plural values must raise `FormatError`.
The `values` object must not be mutated.
