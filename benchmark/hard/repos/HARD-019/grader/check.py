import importlib
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
sys.path.insert(0, str(ROOT / "src"))


def run_visible_tests():
    result = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)


run_visible_tests()
mod = importlib.import_module("search_ranker")

docs = [
    {"id": "new-loose", "title": "Search ranker", "body": "exact match tuning", "updated_at": "2026-06-01T00:00:00Z"},
    {"id": "old-exact-title", "title": "Exact match", "body": "ranking notes", "updated_at": "2024-01-01T00:00:00Z"},
    {"id": "new-one-term", "title": "Exact", "body": "unrelated", "updated_at": "2026-07-01T00:00:00Z"},
]
assert [doc["id"] for doc in mod.rank_results("exact match", docs)][:2] == [
    "old-exact-title",
    "new-loose",
]

phrase_docs = [
    {"id": "recent-split", "title": "Match diagnostics", "body": "exact token appears elsewhere", "updated_at": "2026-05-01T00:00:00Z"},
    {"id": "older-body-phrase", "title": "Diagnostics", "body": "Investigate exact match behavior", "updated_at": "2025-05-01T00:00:00Z"},
]
assert mod.rank_results("exact match", phrase_docs)[0]["id"] == "older-body-phrase"

tie_docs = [
    {"id": "older-exact", "title": "Exact match", "body": "", "updated_at": "2025-01-01T00:00:00Z"},
    {"id": "newer-exact", "title": "Exact match", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
]
assert [doc["id"] for doc in mod.rank_results("exact match", tie_docs)] == [
    "newer-exact",
    "older-exact",
]

stable_docs = [
    {"id": "first", "title": "Nothing", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
    {"id": "second", "title": "Nothing", "body": "", "updated_at": "2026-01-01T00:00:00Z"},
]
assert [doc["id"] for doc in mod.rank_results("missing", stable_docs)] == ["first", "second"]
