import assert from 'node:assert/strict';
import { test } from 'node:test';
import { extractLinks } from '../src/markdownLinks.mjs';

test('ignores image links', () => {
  assert.deepEqual(extractLinks('![logo](logo.png) [docs](https://x.test)'), [
    { text: 'docs', href: 'https://x.test' },
  ]);
});
