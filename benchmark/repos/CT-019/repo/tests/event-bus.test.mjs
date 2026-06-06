import assert from 'node:assert/strict';
import { test } from 'node:test';
import { EventBus } from '../src/eventBus.mjs';

test('unsubscribe removes listener', () => {
  const bus = new EventBus();
  let count = 0;
  const off = bus.on('x', () => { count += 1; });
  off();
  bus.emit('x');
  assert.equal(count, 0);
});
