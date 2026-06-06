import assert from 'node:assert/strict';
import { test } from 'node:test';
import { resolveSettings } from '../src/settingsPanel.mjs';

test('user settings override defaults', () => {
  assert.deepEqual(resolveSettings({ theme: 'dark' }, { theme: 'light' }).theme, 'light');
});
