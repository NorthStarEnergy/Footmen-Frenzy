import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const source = path.join(root, 'site');
const output = path.resolve(root, '../build/wiki');
const files = fs.readdirSync(source, { recursive: true }).filter(f => fs.statSync(path.join(source, f)).isFile());
const allowed = new Set(['.html', '.css', '.js', '.json', '.md', '.csv', '.webp', '.png', '.jpg']);
const dataText = fs.readFileSync(path.join(source, 'wiki-data.js'), 'utf8');
const data = JSON.parse(dataText.slice(dataText.indexOf('=') + 1).trim().replace(/;$/, ''));
const refs = new Set();
function reference(value) {
  if (!value || value.startsWith('#')) return;
  if (/^(?:https?:|data:|mailto:)/i.test(value)) throw new Error(`Unexpected external reference: ${value}`);
  const decoded = decodeURIComponent(value.split(/[?#]/)[0]);
  if (decoded.startsWith('/') || decoded.split('/').includes('..')) throw new Error(`Unsafe reference: ${value}`);
  if (!fs.existsSync(path.join(source, decoded))) throw new Error(`Missing reference: ${value}`);
  refs.add(decoded);
}
function walk(value, key = '') {
  if (typeof value === 'string') {
    if (['path', 'icon'].includes(key) || value.startsWith('assets/')) reference(value);
    for (const m of value.matchAll(/(?:href|src)=["']([^"']+)["']/g)) reference(m[1]);
  } else if (value && typeof value === 'object') {
    for (const [k, v] of Object.entries(value)) walk(v, k);
  }
}
if ('matchSummary' in data || 'replayNote' in data) throw new Error('Private match metadata included');
walk(data);
for (const file of files) {
  if (!allowed.has(path.extname(file))) throw new Error(`Unapproved file: ${file}`);
  if (/\.(html|css|js|json|md|csv)$/.test(file)) {
    const text = fs.readFileSync(path.join(source, file), 'utf8');
    if (/[A-Z]:[\\/](?:Users|Projects)|ff_result\.txt|\.w3g\b|BEGIN .*PRIVATE KEY|sk-proj-/i.test(text)) throw new Error(`Private content marker in ${file}`);
    if (file === 'index.html') for (const m of text.matchAll(/(?:href|src)=["']([^"']+)["']/g)) reference(m[1]);
    if (file.endsWith('.css')) for (const m of text.matchAll(/url\(["']?([^"')]+)["']?\)/g)) reference(m[1]);
  }
}
for (const spell of data.spells) if (/<t[dh][^>]*>\s*default\s*<\//i.test(spell.html)) throw new Error('Placeholder spell value');
fs.mkdirSync(output, { recursive: true });
// Fail on stale output files rather than silently deploying unreviewed material.
for (const existing of fs.readdirSync(output, { recursive: true })) {
  if (fs.statSync(path.join(output, existing)).isFile() && !files.includes(existing)) throw new Error(`Unexpected output file: ${existing}`);
}
for (const file of files) {
  fs.mkdirSync(path.dirname(path.join(output, file)), { recursive: true });
  fs.copyFileSync(path.join(source, file), path.join(output, file));
}
const manifest = files.sort().map(file => ({ path: file.replaceAll('\\', '/'), bytes: fs.statSync(path.join(output, file)).size, sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(output, file))).digest('hex') }));
fs.writeFileSync(path.resolve(root, '../build/wiki-manifest.json'), JSON.stringify({ files: manifest, checkedReferences: refs.size }, null, 2));
console.log(JSON.stringify({ output, files: files.length, checkedReferences: refs.size, heroEditions: Object.keys(data.heroVariants), spells: data.spells.length, items: data.itemModel.items.length }, null, 2));
