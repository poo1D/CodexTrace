import fs from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const pkg = JSON.parse(await fs.readFile(path.join(root, 'package.json'), 'utf8'));
const entry = pkg.exports?.['.'];

if (!entry || typeof entry !== 'object') {
  throw new Error('package exports must define conditional import and require entry points');
}
if (entry.import !== './dist/index.mjs') {
  throw new Error('ESM import export must point to ./dist/index.mjs');
}
if (entry.require !== './dist/index.cjs') {
  throw new Error('CommonJS require export must point to ./dist/index.cjs');
}

await fs.mkdir(path.join(root, 'dist'), { recursive: true });
await fs.copyFile(path.join(root, 'src/index.mjs'), path.join(root, 'dist/index.mjs'));
await fs.copyFile(path.join(root, 'src/index.cjs'), path.join(root, 'dist/index.cjs'));
