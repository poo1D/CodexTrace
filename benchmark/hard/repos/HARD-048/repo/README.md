# cursor-pagination

`list_page(items, limit, cursor=None, *, order="desc")` returns
a `Page(items, next_cursor)` for API-style cursor pagination.

Item shape:

```python
{"id": "item-id", "created_at": 1700000000, ...}
```

Requirements:

- sort by `(created_at, id)` for deterministic keyset pages
- support `order="desc"` and `order="asc"`
- exclude the cursor item from the next page
- keep pagination stable when new records are inserted before
  the cursor between requests
- clamp limits into `1 <= limit <= MAX_LIMIT`
- raise `CursorError` for malformed or tampered cursors
- do not mutate the input list or item dictionaries
