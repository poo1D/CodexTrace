import assert from 'node:assert/strict';
import { test } from 'node:test';
import { loadAsset } from '../src/assetLoader.mjs';

test('loads local text fixture', async () => {
  assert.equal(await loadAsset('logo.txt'), 'LOCAL-LOGO\n');
});

test('loads local json fixture', async () => {
  assert.deepEqual(await loadAsset('config.json'), { name: 'local-config', version: 1 });
});
