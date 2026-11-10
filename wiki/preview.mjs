import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../build/wiki');
const types = { '.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.json': 'application/json', '.webp': 'image/webp', '.png': 'image/png', '.md': 'text/plain', '.csv': 'text/csv' };
http.createServer((req, res) => {
  let file;
  try { file = path.resolve(root, '.' + decodeURIComponent(new URL(req.url, 'http://localhost').pathname)); } catch { res.writeHead(400).end(); return; }
  if (file === root) file = path.join(root, 'index.html');
  if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404).end('Not found'); return; }
  res.writeHead(200, { 'Content-Type': (types[path.extname(file)] || 'application/octet-stream') + (types[path.extname(file)]?.startsWith('text/') ? '; charset=utf-8' : ''), 'X-Content-Type-Options': 'nosniff' });
  fs.createReadStream(file).pipe(res);
}).listen(8766, '127.0.0.1', () => console.log('Wiki preview: http://127.0.0.1:8766'));
