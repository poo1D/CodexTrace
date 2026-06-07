# env-manifest-resolver

Resolve deployment environment values from a manifest and local
env files.

CLI:

```bash
python -m env_manifest_resolver.cli fixtures/app/manifest.json --set KEY=VALUE
```

Precedence is:

1. manifest `defaults`
2. `.env` next to the manifest
3. `.env.local` next to the manifest
4. explicit `--set KEY=VALUE`

Blank values in `.env.local` are ignored so local placeholder
lines do not erase shared `.env` values. Blank values passed
with `--set KEY=` are explicit overrides and must be preserved.

The CLI prints stable JSON containing every required key.
