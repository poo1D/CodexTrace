import fs from 'node:fs';

if (!fs.existsSync('src/react-shim.d.ts')) {
  console.error('Cannot find React JSX type declarations');
  process.exit(1);
}
const app = fs.readFileSync('src/App.tsx', 'utf8');
if (!app.includes('<main>')) {
  console.error('App markup missing');
  process.exit(1);
}
console.log('build ok');
