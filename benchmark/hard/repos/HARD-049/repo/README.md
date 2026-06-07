# test-sharder

`plan_shards(tests, shard_count, *, quarantined=None)` creates
deterministic CI test shards.

Test item shape:

```python
{"id": "tests/test_api.py::test_create", "estimated_seconds": 12}
```

Return shape:

```python
[
    {"index": 0, "tests": ["test id"], "estimated_seconds": 12},
    ...
]
```

Requirements:

- reject `shard_count < 1` with `ShardError`
- reject duplicate test ids with `ShardError`
- exclude ids listed in `quarantined`
- greedily balance by `estimated_seconds`
- break ties deterministically by shard load, shard index, and test id
- keep every shard present, even if it receives no tests
- do not mutate `tests` or test dictionaries
