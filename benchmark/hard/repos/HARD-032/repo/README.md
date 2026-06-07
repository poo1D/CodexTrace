# undoable-queue

`UndoableQueue` is a FIFO queue with history.

Public API:

- `enqueue(item)`
- `dequeue()`
- `clear()`
- `undo()`
- `redo()`
- `peek()`
- `toArray()`
- `size`

Items are plain objects with at least an `id` field. Queue
history must preserve full item metadata, keep FIFO ordering,
and isolate snapshots from later mutations of returned values.
