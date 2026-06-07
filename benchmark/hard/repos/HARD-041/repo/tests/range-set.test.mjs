import assert from 'node:assert/strict';
import test from 'node:test';
import { RangeSet } from '../src/range-set.mjs';

test('add stores a range and contains values inside it', () => {
  const ranges = new RangeSet().add(1, 3);

  assert.equal(ranges.contains(1), true);
  assert.equal(ranges.contains(2), true);
  assert.equal(ranges.contains(4), false);
  assert.deepEqual(ranges.toArray(), [[1, 3]]);
});

test('remove drops a fully covered range', () => {
  const ranges = new RangeSet([[1, 3], [10, 12]]).remove(1, 3);

  assert.deepEqual(ranges.toArray(), [[10, 12]]);
});
