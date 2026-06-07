class ShardError(Exception):
    pass


def plan_shards(tests, shard_count, *, quarantined=None):
    if shard_count < 1:
        raise ShardError("shard_count must be positive")

    shards = [
        {"index": index, "tests": [], "estimated_seconds": 0}
        for index in range(shard_count)
    ]

    for offset, test in enumerate(sorted(tests, key=lambda item: item["id"])):
        shard = shards[offset % shard_count]
        shard["tests"].append(test["id"])
        shard["estimated_seconds"] += int(test.get("estimated_seconds", 1))

    return shards
