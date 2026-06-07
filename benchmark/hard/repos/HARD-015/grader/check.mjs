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


run('npm', ['run', 'build']);

const fs = await import('node:fs/promises');
const { createRequire } = await import('node:module');
const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8'));
assert.equal(pkg.exports['.'].import, './dist/index.mjs');
assert.equal(pkg.exports['.'].require, './dist/index.cjs');

const esm = await loadModule('dist/index.mjs');
const require = createRequire(path.join(root, 'grader.cjs'));
const cjs = require(path.join(root, 'dist/index.cjs'));

assert.equal(esm.formatName({ first: 'Ada', last: 'Lovelace' }), 'Ada Lovelace');
assert.equal(cjs.formatName({ first: 'Grace', last: 'Hopper' }), 'Grace Hopper');
assert.equal(esm.formatName({ first: '  Katherine ', last: ' Johnson  ' }), 'Katherine Johnson');
assert.equal(cjs.formatName({ first: 'Alan', last: 'Turing', title: 'Dr.' }), 'Alan Turing');
