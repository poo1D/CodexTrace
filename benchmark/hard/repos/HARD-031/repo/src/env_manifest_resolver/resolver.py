import json
from pathlib import Path


def load_manifest(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def resolve_manifest(manifest_path, overrides=None):
    manifest = load_manifest(manifest_path)
    base_dir = Path.cwd()
    values = dict(manifest.get("defaults", {}))
    values.update(_read_env_file(base_dir / ".env"))
    values.update(_read_env_file(base_dir / ".env.local"))
    values.update(overrides or {})
    return {key: values.get(key, "") for key in manifest.get("required", [])}


def _read_env_file(path):
    if not path.exists():
        return {}

    result = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        result[key.strip()] = value.strip()
    return result
