import assert from 'node:assert/strict';
import { test } from 'node:test';
import { UndoableQueue } from '../src/index.mjs';

function ids(queue) {
  return queue.toArray().map(item => item.id);
}

test('enqueues and dequeues in FIFO order', () => {
  const queue = new UndoableQueue();
  queue.enqueue({ id: 'a' }).enqueue({ id: 'b' });

  assert.deepEqual(ids(queue), ['a', 'b']);
  assert.equal(queue.dequeue().id, 'a');
  assert.deepEqual(ids(queue), ['b']);
});

test('undo restores queue ids after dequeue', () => {
  const queue = new UndoableQueue([{ id: 'a' }, { id: 'b' }]);

  assert.equal(queue.dequeue().id, 'a');
  assert.deepEqual(ids(queue), ['b']);
  assert.equal(queue.undo(), true);
  assert.deepEqual(ids(queue), ['a', 'b']);
});

test('redo reapplies an undone enqueue', () => {
  const queue = new UndoableQueue([{ id: 'a' }]);

  queue.enqueue({ id: 'b' });
  assert.deepEqual(ids(queue), ['a', 'b']);
  assert.equal(queue.undo(), true);
  assert.deepEqual(ids(queue), ['a']);
  assert.equal(queue.redo(), true);
  assert.deepEqual(ids(queue), ['a', 'b']);
});
