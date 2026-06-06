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
const { matchRoute } = await loadModule('src/router.mjs');
assert.deepEqual(matchRoute('/users/:id', '/users/a%20b/'), { matched: true, params: { id: 'a b' } });
assert.deepEqual(matchRoute('/files/*path', '/files/a/b/c.txt'), { matched: true, params: { path: 'a/b/c.txt' } });
assert.deepEqual(matchRoute('/files/*path', '/other/a'), { matched: false, params: {} });
