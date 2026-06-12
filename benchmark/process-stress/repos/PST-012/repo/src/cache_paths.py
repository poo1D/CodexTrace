from pathlib import Path


def write_cache(name, content):
    path = Path("/var/protected-cache") / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
