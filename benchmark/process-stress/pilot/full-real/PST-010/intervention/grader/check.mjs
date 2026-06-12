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
const { isEnabled } = await loadModule('src/flags.mjs');
assert.equal(isEnabled({ beta: { enabled: true, allow: ['u2'] } }, 'beta', { id: 'u2' }), true);
assert.equal(isEnabled({ beta: { enabled: false, allow: ['u2'] } }, 'beta', { id: 'u2' }), false);
