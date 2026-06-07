import json
import os
from pathlib import Path


def build_manifest(root, include_empty_dirs=False):
    root_path = Path(root)
    entries = []
    for current, dirs, files in os.walk(root_path):
        for filename in files:
            path = Path(current) / filename
            rel = str(path.relative_to(root_path))
            entries.append({
                "path": rel,
                "kind": "file",
                "size": path.stat().st_size,
            })
    return {"entries": entries}


def write_manifest(root, output, include_empty_dirs=False):
    manifest = build_manifest(root, include_empty_dirs=include_empty_dirs)
    Path(output).write_text(json.dumps(manifest) + "\n", encoding="utf-8")
    return manifest
