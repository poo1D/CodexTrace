import assert from 'node:assert/strict';
import { test } from 'node:test';
import { BatchQueue } from '../src/batchQueue.mjs';

test('flush waits for async handlers and preserves order', async () => {
  const queue = new BatchQueue(async item => {
    await Promise.resolve();
    return item * 2;
  });
  queue.push(1);
  queue.push(2);
  assert.equal(queue.size(), 2);
  assert.deepEqual(await queue.flush(), [
    { status: 'fulfilled', value: 2 },
    { status: 'fulfilled', value: 4 },
  ]);
  assert.equal(queue.size(), 0);
});
