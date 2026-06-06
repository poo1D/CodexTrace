import fs from 'node:fs';
const source = fs.readFileSync('src/format.mjs', 'utf8');
if (/\bvar\b/.test(source)) {
  console.error('no-var violation');
  process.exit(1);
}
if (/[^=!]==[^=]/.test(source)) {
  console.error('eqeqeq violation');
  process.exit(1);
}
