// Minimal static file server for the visual tests. Serves the project root so
// the harness can load /static/vendor/three/* exactly as the app does, plus
// /tests/visual/* (harness + fixtures). No dependency on Flask, the database,
// uploads or master auth: the tests exercise the viewer modules in isolation,
// which is what makes them fast and deterministic.
//
// Chosen over Playwright's webServer option because it needs no framework and
// starts in milliseconds. Started/stopped by the Playwright config.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { join, normalize, extname } from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = normalize(join(fileURLToPath(import.meta.url), '..', '..', '..'));
const TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.png': 'image/png',
  '.glb': 'model/gltf-binary',
  '.json': 'application/json',
};

export function startServer(port = 0) {
  const server = createServer(async (req, res) => {
    try {
      const url = decodeURIComponent((req.url || '/').split('?')[0]);
      // Contain every path to ROOT (no traversal outside the project).
      const path = normalize(join(ROOT, url));
      if (!path.startsWith(ROOT)) { res.writeHead(403).end('forbidden'); return; }
      const body = await readFile(path);
      res.writeHead(200, { 'Content-Type': TYPES[extname(path)] || 'application/octet-stream' });
      res.end(body);
    } catch (e) {
      res.writeHead(404, { 'Content-Type': 'text/plain' }).end('not found');
    }
  });
  return new Promise((resolve) => {
    server.listen(port, '127.0.0.1', () => {
      const { port } = server.address();
      resolve({ server, baseURL: `http://127.0.0.1:${port}` });
    });
  });
}

// Allow `node server.mjs 8099` for manual poking.
if (import.meta.url === `file://${process.argv[1]}`) {
  const { baseURL } = await startServer(Number(process.argv[2]) || 8099);
  console.log('serving', baseURL);
}
