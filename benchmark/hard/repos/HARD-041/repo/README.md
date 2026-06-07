# range-set

`RangeSet` stores closed integer intervals.

Public API:

- `new RangeSet(ranges = [])`
- `add(start, end)`
- `remove(start, end)`
- `contains(value)`
- `union(other)`
- `toArray()`

Requirements:

- All operations return a new `RangeSet`; existing instances are
  immutable.
- Ranges are closed integer intervals.
- Overlapping and adjacent ranges coalesce.
- Removing a range can split an existing range.
- Invalid ranges throw `RangeSetError`.
- `toArray()` returns sorted normalized `[start, end]` pairs.
