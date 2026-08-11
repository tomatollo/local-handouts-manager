// Generates deterministic PNG fixture textures used by the viewer visual tests.
// No real handout uploads are touched: the tests must be reproducible and
// runnable on a clean checkout, so the textures are drawn from scratch here
// with fixed geometry and colours (no randomness, no fonts).
//
//   node tests/visual/make-fixtures.mjs
//
// Output (committed, small):
//   tests/visual/fixtures/front.png       solid parchment sheet w/ border + mark
//   tests/visual/fixtures/holed.png       same, with transparent "torn" holes
//   tests/visual/fixtures/back.png        distinct back face
import { PNG } from 'pngjs';
import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const outDir = join(here, 'fixtures');
mkdirSync(outDir, { recursive: true });

const W = 512, H = 724; // ~A-series portrait

function make({ bg, ink, holes = false }) {
  const png = new PNG({ width: W, height: H });
  for (let y = 0; y < H; y++) {
    for (let x = 0; x < W; x++) {
      const i = (W * y + x) << 2;
      // Border frame.
      const border = x < 16 || x >= W - 16 || y < 16 || y >= H - 16;
      // A centred cross "mark" so orientation is visible in the render.
      const cx = Math.abs(x - W / 2), cy = Math.abs(y - H / 2);
      const mark = (cx < 8 && cy < 160) || (cy < 8 && cx < 160);
      let [r, g, b, a] = border || mark ? ink : bg;
      if (holes) {
        // Two circular fully-transparent holes to exercise alphaTest in the
        // sheet material (torn scroll / bullet hole behaviour).
        for (const [hx, hy, hr] of [[160, 240, 46], [340, 500, 60]]) {
          if ((x - hx) ** 2 + (y - hy) ** 2 < hr * hr) { a = 0; }
        }
      }
      png.data[i] = r; png.data[i + 1] = g; png.data[i + 2] = b; png.data[i + 3] = a;
    }
  }
  return PNG.sync.write(png);
}

const parchment = [214, 196, 158, 255];
const darkInk   = [40, 30, 18, 255];
const backBg    = [150, 120, 96, 255];
const backInk   = [30, 20, 12, 255];

writeFileSync(join(outDir, 'front.png'), make({ bg: parchment, ink: darkInk }));
writeFileSync(join(outDir, 'holed.png'), make({ bg: parchment, ink: darkInk, holes: true }));
writeFileSync(join(outDir, 'back.png'),  make({ bg: backBg, ink: backInk }));
console.log('fixtures written to', outDir);
