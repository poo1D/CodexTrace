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


import base64
import copy
import json

run_visible_tests()
mod = importlib.import_module("cursor_pagination")

items = [
    {"id": "b", "created_at": 100, "title": "B"},
    {"id": "a", "created_at": 100, "title": "A"},
    {"id": "c", "created_at": 90, "title": "C"},
    {"id": "d", "created_at": 80, "title": "D"},
]
before = copy.deepcopy(items)

page1 = mod.list_page(items, 2)
assert [item["id"] for item in page1.items] == ["b", "a"]
assert page1.next_cursor is not None
assert items == before

changed = [{"id": "z", "created_at": 200, "title": "Z"}, *items]
page2 = mod.list_page(changed, 2, page1.next_cursor)
assert [item["id"] for item in page2.items] == ["c", "d"]
assert page2.next_cursor is None

asc = mod.list_page(items, 3, order="asc")
assert [item["id"] for item in asc.items] == ["d", "c", "a"]
asc2 = mod.list_page(items, 3, asc.next_cursor, order="asc")
assert [item["id"] for item in asc2.items] == ["b"]

many = [{"id": str(i), "created_at": i} for i in range(150)]
capped = mod.list_page(many, 1000)
assert len(capped.items) == mod.MAX_LIMIT
minimum = mod.list_page(many, 0)
assert len(minimum.items) == 1

first = mod.list_page(items, 1)
second = mod.list_page(items, 1, first.next_cursor)
assert first.items[0]["id"] != second.items[0]["id"]

tampered_payloads = [
    "abc",
    base64.urlsafe_b64encode(json.dumps({"offset": 1}).encode("utf-8")).decode("ascii"),
    base64.urlsafe_b64encode(json.dumps({"created_at": 100}).encode("utf-8")).decode("ascii"),
    base64.urlsafe_b64encode(json.dumps({"created_at": 100, "id": "missing"}).encode("utf-8")).decode("ascii"),
]
for bad in tampered_payloads:
    try:
        mod.list_page(items, 2, bad)
    except mod.CursorError:
        pass
    else:
        raise AssertionError(f"bad cursor was accepted: {bad}")
