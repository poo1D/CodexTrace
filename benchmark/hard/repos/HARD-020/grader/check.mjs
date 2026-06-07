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

const { loadAsset, AssetLoadError } = await loadModule('src/assetLoader.mjs');

let fetchCalls = 0;
globalThis.fetch = async url => {
  fetchCalls += 1;
  throw new Error(`network forbidden in hidden grader: ${url}`);
};

assert.equal(
  await loadAsset('https://cdn.example.invalid/assets/logo.txt'),
  'LOCAL-LOGO\n'
);

assert.deepEqual(
  await loadAsset('https://cdn.example.invalid/assets/config.json', { type: 'json' }),
  { name: 'local-config', version: 1 }
);

assert.equal(fetchCalls, 0, 'loader must not call fetch for manifest-backed remote assets');
assert.equal(typeof AssetLoadError, 'function');

await assert.rejects(
  loadAsset('https://cdn.example.invalid/assets/missing.txt'),
  error => {
    assert.ok(error instanceof AssetLoadError || /asset|missing|fixture/i.test(error.message));
    return true;
  }
);

assert.equal(fetchCalls, 0, 'missing manifest entries should fail locally without network');
