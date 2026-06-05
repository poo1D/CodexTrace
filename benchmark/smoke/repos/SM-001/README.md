# SM-001 sum_prefix

Bug: `sum_prefix(items, n)` treats `n` as the last index. It should treat `n`
as the number of leading items to include.
