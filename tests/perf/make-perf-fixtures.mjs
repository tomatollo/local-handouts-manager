// Generates the texture fixtures the performance profiler loads. Two profiles:
//
//   light/  — a single small sheet (front+back), ~512x724, a few KB each.
//             Represents the common case: one handout, quick to open.
//   large/  — many HIGH-RESOLUTION pages (2048x2896 by default) plus a big
//             front/back pair for the 3D sheet, to stress texture upload,
//             GPU memory and per-frame cost.
//
// The counts/sizes are CLI-tunable so the profiler can sweep them:
//   node make-perf-fixtures.mjs --large-pages 24 --large-dim 2048
//
// Deterministic (no randomness) so repeated profiling runs are comparable.
import { PNG } from 'pngjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).join(' ').split('--').filter(Boolean)
    .map(s => s.trim().split(/\s+/)).map(([k, v]) => [k, v]));

const LARGE_PAGES = Number(args['large-pages'] || 24);
const LARGE_DIM   = Number(args['large-dim'] || 2048);   // width; height = *1.414
const LIGHT_DIM   = 512;

function sheet(w, h, hue, label) {
  const png = new PNG({ width: w, height: h });
  for (let y = 0; y < h; y++) {
    for (let x = 0; x < w; x++) {
      const i = (w * y + x) << 2;
      const border = x < w*0.03 || x >= w*0.97 || y < h*0.03 || y >= h*0.97;
      // A few diagonal ink bands so the image has real high-frequency content
      // (a flat fill would compress away and under-exercise texture upload).
      const band = ((x + y + label * 40) % Math.max(24, (w >> 5))) < 6;
      let r, g, b;
      if (border || band) { r = 40; g = 30; b = 18; }
      else { r = 200 - (hue % 40); g = 180 - (hue % 30); b = 150 - (hue % 50); }
      png.data[i] = r; png.data[i+1] = g; png.data[i+2] = b; png.data[i+3] = 255;
    }
  }
  return PNG.sync.write(png);
}

// light profile
const lightDir = join(here, 'fixtures', 'light');
mkdirSync(lightDir, { recursive: true });
const lh = Math.round(LIGHT_DIM * 1.414);
writeFileSync(join(lightDir, 'page-000.png'), sheet(LIGHT_DIM, lh, 10, 0));
writeFileSync(join(lightDir, 'back.png'),      sheet(LIGHT_DIM, lh, 25, 1));
console.log(`light: 1 page + back @ ${LIGHT_DIM}x${lh}`);

// large profile
const largeDir = join(here, 'fixtures', 'large');
mkdirSync(largeDir, { recursive: true });
const H = Math.round(LARGE_DIM * 1.414);
for (let p = 0; p < LARGE_PAGES; p++) {
  writeFileSync(join(largeDir, `page-${String(p).padStart(3, '0')}.png`),
                sheet(LARGE_DIM, H, p * 7, p));
}
writeFileSync(join(largeDir, 'back.png'), sheet(LARGE_DIM, H, 99, 42));
console.log(`large: ${LARGE_PAGES} pages + back @ ${LARGE_DIM}x${H}`);

// A manifest the profiler reads so it need not re-derive counts/paths.
writeFileSync(join(here, 'fixtures', 'manifest.json'), JSON.stringify({
  light: { pages: ['light/page-000.png'], back: 'light/back.png', dim: [LIGHT_DIM, lh] },
  large: {
    pages: Array.from({ length: LARGE_PAGES }, (_, p) => `large/page-${String(p).padStart(3,'0')}.png`),
    back: 'large/back.png', dim: [LARGE_DIM, H],
  },
}, null, 2));
console.log('manifest written');
