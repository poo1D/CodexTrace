import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs';

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
assert.ok(fs.existsSync(path.join(root, 'src/react-shim.d.ts')));
const shim = fs.readFileSync(path.join(root, 'src/react-shim.d.ts'), 'utf8');
assert.match(shim, /JSX|IntrinsicElements|react/i);
