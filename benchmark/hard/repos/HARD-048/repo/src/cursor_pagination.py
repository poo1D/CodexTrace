from __future__ import annotations

import base64
import json
from dataclasses import dataclass


MAX_LIMIT = 100


class CursorError(Exception):
    pass


@dataclass
class Page:
    items: list
    next_cursor: str | None


def _encode_cursor(offset):
    payload = json.dumps({"offset": offset}).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii")


def _decode_cursor(cursor):
    try:
        data = base64.urlsafe_b64decode(cursor.encode("ascii"))
        return json.loads(data.decode("utf-8"))["offset"]
    except Exception as exc:
        raise CursorError("malformed cursor") from exc


def list_page(items, limit, cursor=None, *, order="desc"):
    if order not in {"asc", "desc"}:
        raise ValueError("order must be asc or desc")

    start = _decode_cursor(cursor) if cursor else 0
    limit = max(1, min(int(limit), MAX_LIMIT))

    items.sort(
        key=lambda item: item["created_at"],
        reverse=(order == "desc"),
    )
    page_items = items[start:start + limit]
    next_offset = start + len(page_items)
    next_cursor = None
    if next_offset < len(items):
        next_cursor = _encode_cursor(next_offset)
    return Page(page_items, next_cursor)
