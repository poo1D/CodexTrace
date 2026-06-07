import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

const root = process.cwd();

function run(command, args) {
  const result = spawnSync(command, args, { cwd: root, encoding: 'utf8' });
  if (result.status !== 0) {
    process.stdout.write(result.stdout || '');
    process.stdout.write(result.stderr || '');
    process.exit(result.status || 1);
  }
}

async function loadModule(relPath) {
  return import(pathToFileURL(path.join(root, relPath)).href + `?v=${Date.now()}`);
}


run('npm', ['test']);
const { FormatError, formatMessage } = await loadModule('src/formatMessage.mjs');

const values = { name: 'Ada', count: 0 };
const before = JSON.stringify(values);
assert.equal(
  formatMessage('{name} has {count, plural, =0 {no messages} one {one message} other {# messages}}.', values),
  'Ada has no messages.',
);
assert.equal(JSON.stringify(values), before);

assert.equal(
  formatMessage('{count, plural, one {One file} other {# files}}', { count: 1 }),
  'One file',
);
assert.equal(
  formatMessage('{count, plural, one {One file} other {# files}}', { count: 5 }),
  '5 files',
);
assert.equal(
  formatMessage('{count, plural, offset:1 =0 {Nobody came} one {{name} came alone} other {{name} and # others came}}', {
    count: 4,
    name: 'Grace',
  }),
  'Grace and 3 others came',
);
assert.equal(
  formatMessage("Use '{'count'}' literally: {count, plural, one {'#'} other {#}}", { count: 2 }),
  'Use {count} literally: 2',
);

assert.throws(
  () => formatMessage('{count, plural, one {ok} other {ok}}', {}),
  (error) => error instanceof FormatError && error.message.includes('count'),
);
assert.throws(
  () => formatMessage('{name} {missing}', { name: 'Ada' }),
  (error) => error instanceof FormatError && error.message.includes('missing'),
);
