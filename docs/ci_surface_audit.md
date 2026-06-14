# CI Surface Audit

This generated audit checks that the repository CI and packaging surface exercise the paper artifact's core offline gates.

## Summary

- Ready: yes
- CI checks covered: 10 / 10
- Packaging checks covered: 6 / 6
- Makefile checks covered: 3 / 3
- CI workflow: `.github/workflows/ci.yml`
- Python package metadata: `pyproject.toml`
- Local task runner: `Makefile`

## CI Checks

| Check | Description | Covered |
| --- | --- | --- |
| `checkout` | checks out repository sources | yes |
| `setup_python` | installs the Python runtime | yes |
| `python_312` | pins CI to Python 3.12 | yes |
| `editable_dev_install` | installs package and dev dependencies | yes |
| `pytest` | runs Python tests | yes |
| `submission_readiness` | runs the paper artifact readiness gate | yes |
| `setup_node` | installs the Node runtime | yes |
| `node_22` | pins CI to Node 22 | yes |
| `web_install` | installs Web UI dependencies | yes |
| `web_build` | builds the Web replay artifact | yes |

## Packaging Checks

| Check | Description | Covered |
| --- | --- | --- |
| `project_name` | declares the package name | yes |
| `python_requirement` | declares supported Python versions | yes |
| `dev_extra_pytest` | exposes pytest through the dev extra | yes |
| `console_script` | installs the codex-trace CLI entry point | yes |
| `build_backend` | declares a setuptools build backend | yes |
| `pytest_pythonpath` | keeps tests importable from repository root | yes |

## Makefile Checks

| Check | Description | Covered |
| --- | --- | --- |
| `test` | local pytest target | yes |
| `demo` | offline demo target | yes |
| `web_build` | local Web build target | yes |

Interpretation: this audit checks committed CI and packaging declarations. It does not execute GitHub Actions itself.
