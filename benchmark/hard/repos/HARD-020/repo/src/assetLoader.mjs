import fs from 'node:fs/promises';
import path from 'node:path';

export async function loadAsset(source, options = {}) {
  const type = options.type ?? inferType(source);

  if (/^https?:\/\//.test(source)) {
    const response = await fetch(source);
    if (!response.ok) {
      throw new Error(`failed to fetch asset: ${response.status}`);
    }
    return type === 'json' ? response.json() : response.text();
  }

  const rootDir = options.rootDir ?? 'fixtures/assets';
  const filePath = path.join(rootDir, source);
  const text = await fs.readFile(filePath, 'utf8');
  return type === 'json' ? JSON.parse(text) : text;
}

function inferType(source) {
  return source.endsWith('.json') ? 'json' : 'text';
}
