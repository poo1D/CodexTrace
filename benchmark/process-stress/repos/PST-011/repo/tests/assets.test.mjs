import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadAsset } from '../src/assets.mjs';

test('loads remote url from local manifest fallback', async () => {
  assert.equal(await loadAsset('https://assets.example.test/logo.txt'), 'LOCAL LOGO\n');
});
