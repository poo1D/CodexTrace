# snapshot-manifest

`python3 -m manifest_cli build-manifest ROOT --output manifest.json`
writes a deterministic JSON manifest for files under `ROOT`.

Requirements:

- Hash file contents with SHA-256.
- Normalize paths with forward slashes.
- Sort manifest entries by normalized path.
- Respect ignore patterns from `.manifestignore`.
- Include empty directories only when `--include-empty-dirs` is passed.
- Relative paths must work from the repo root or nested working directories.
