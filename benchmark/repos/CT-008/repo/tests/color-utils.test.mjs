import assert from 'node:assert/strict';
import { test } from 'node:test';
import { hexToRgb } from '../src/colorUtils.mjs';

test('converts valid hex', () => {
  assert.deepEqual(hexToRgb('#0a1b2c'), { r: 10, g: 27, b: 44 });
});

test('rejects malformed input', () => {
  assert.throws(() => hexToRgb('#xyz'), /invalid/i);
});
