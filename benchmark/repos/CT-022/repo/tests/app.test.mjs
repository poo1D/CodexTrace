import assert from 'node:assert/strict';
import { test } from 'node:test';
import fs from 'node:fs';

test('app source exists', () => {
  assert.ok(fs.existsSync('src/App.tsx'));
});
