// Performance profiler for the object3d viewer, across two handout profiles:
// "light" (one small sheet) and "large" (many high-res pages + a big sheet).
//
// For each profile it measures, over N repetitions:
//   - loadMs      : mount() -> onLoaded (texture decode + upload + first frame)
//   - fps / frame : median & p95 frame time and derived FPS during a scripted
//                   orbit, i.e. real per-frame render cost under interaction
//   - heapMB      : JS heap growth from before-mount to loaded (approx leak/
//                   working-set signal; Chromium only, needs --enable-precise-
//                   memory-info which we pass)
//   - textures    : live GPU textures the renderer reports (footprint proxy)
//   - destroyMs   : teardown time, plus a hard assert the canvas count is 0
//
// It renders on SwiftShader (software GL) so numbers are stable and comparable
// run-to-run on any machine, at the cost of being slower than a real GPU —
// treat the ABSOLUTE ms as relative/comparative, and watch the large-vs-light
// RATIO and regressions over time rather than the raw figure.
//
//   node tests/perf/profile.mjs [--reps 5] [--orbit-frames 120]
//
// Writes tests/perf/results/latest.json and prints a table.
import { chromium } from 'playwright';
import { startServer } from '../visual/server.mjs';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const args = Object.fromEntries(
  process.argv.slice(2).join(' ').split('--').filter(Boolean)
    .map(s => s.trim().split(/\s+/)).map(([k,v]) => [k, v]));
const REPS = Number(args.reps || 5);
const ORBIT_FRAMES = Number(args['orbit-frames'] || 120);

const BROWSERS = process.env.PLAYWRIGHT_BROWSERS_PATH;
const EXE = process.env.PW_CHROMIUM;   // optional explicit headless_shell path

const manifest = JSON.parse(readFileSync(join(here, 'fixtures', 'manifest.json')));

function pct(sorted, p) {
  if (!sorted.length) return 0;
  const i = Math.min(sorted.length - 1, Math.floor(p * sorted.length));
  return sorted[i];
}
function median(a){ const s=[...a].sort((x,y)=>x-y); return pct(s,0.5); }

async function measureOnce(page, profileName, profile) {
  const base = '/tests/perf/fixtures/';
  // Use the cover page as the 3D sheet front, the back.png as its back. The
  // "large" cost comes from the big dimensions of those two textures; the full
  // page list is also pre-fetched into the browser cache below to model the
  // real memory pressure of a many-page handout being opened.
  const frontUrl = base + profile.pages[0];
  const backUrl  = base + profile.back;

  // Warm the HTTP cache for every page so decode/upload timing isn't dominated
  // by network on the large profile — the profiler targets render cost, not the
  // dev server's throughput.
  await page.evaluate(async (urls) => {
    await Promise.all(urls.map(u => fetch(u).then(r => r.arrayBuffer())));
  }, [frontUrl, backUrl, ...profile.pages.map(p => base + p)]);

  const heapBefore = await page.evaluate(() =>
    (performance.memory ? performance.memory.usedJSHeapSize : 0));

  const t0 = await page.evaluate(() => performance.now());
  await page.evaluate(([f,b]) => window.perfMount3D({ frontUrl: f, backUrl: b, background: '#0b0b0d' }),
                      [frontUrl, backUrl]);
  await page.waitForFunction(() => window.__ready === true, { timeout: 30_000 });
  const loadMs = await page.evaluate((t) => performance.now() - t, t0);
  const err = await page.evaluate(() => window.__err);
  if (err) throw new Error(`${profileName}: viewer error: ${err}`);

  // performance.memory is noisy (GC can fire between reads and even make the
  // delta negative), so sample it a few times and take the max post-load size:
  // the working-set high-water mark is the stable, meaningful signal.
  const heapAfter = await page.evaluate(async () => {
    let hi = 0;
    for (let i = 0; i < 3; i++) {
      if (performance.memory) hi = Math.max(hi, performance.memory.usedJSHeapSize);
      await new Promise(r => setTimeout(r, 16));
    }
    return hi;
  });

  // Sample frame times during a scripted orbit.
  await page.evaluate(() => window.perfStartSampling());
  for (let i = 0; i < ORBIT_FRAMES; i++) {
    await page.evaluate(() => window.perfOrbit(0.03));
    await page.waitForTimeout(8);   // let a rAF tick happen
  }
  const frames = await page.evaluate(() => window.perfStopSampling());
  const sorted = [...frames].sort((a,b)=>a-b);
  const medFrame = median(frames);
  const p95Frame = pct(sorted, 0.95);

  const info = await page.evaluate(() => window.perfRenderInfo());

  const destroyMs = await page.evaluate(() => window.perfDestroyTimed());
  const canvases = await page.evaluate(() => window.perfCanvasCount());
  if (canvases !== 0) throw new Error(`${profileName}: leak — ${canvases} canvas(es) after destroy`);

  return {
    loadMs: +loadMs.toFixed(1),
    medFrameMs: +medFrame.toFixed(2),
    p95FrameMs: +p95Frame.toFixed(2),
    fps: medFrame > 0 ? +(1000 / medFrame).toFixed(1) : 0,
    heapMB: +(Math.max(0, heapAfter - heapBefore) / 1048576).toFixed(2),
    textures: info ? info.textures : null,
    geometries: info ? info.geometries : null,
    triangles: info ? info.triangles : null,
    destroyMs: +destroyMs.toFixed(1),
  };
}

function aggregate(runs) {
  const keys = ['loadMs','medFrameMs','p95FrameMs','fps','heapMB','destroyMs'];
  const out = { reps: runs.length };
  for (const k of keys) {
    const vals = runs.map(r => r[k]).filter(v => typeof v === 'number');
    out[k] = { median: +median(vals).toFixed(2),
               min: +Math.min(...vals).toFixed(2),
               max: +Math.max(...vals).toFixed(2) };
  }
  const last = runs[runs.length - 1];
  out.textures = last.textures; out.geometries = last.geometries; out.triangles = last.triangles;
  return out;
}

(async () => {
  const { server, baseURL } = await startServer(0);
  const launchArgs = ['--use-gl=angle','--use-angle=swiftshader','--enable-webgl',
                      '--ignore-gpu-blocklist','--disable-gpu-vsync',
                      '--enable-precise-memory-info'];
  const browser = await chromium.launch(
    EXE ? { executablePath: EXE, args: launchArgs } : { args: launchArgs });
  const page = await browser.newPage({ viewport: { width: 1100, height: 820 } });
  page.on('pageerror', e => console.error('PAGE ERROR', e.message));
  await page.goto(baseURL + '/tests/perf/harness.html');
  await page.waitForFunction(() => window.__harnessReady === true);

  const results = {};
  for (const [name, profile] of Object.entries(manifest)) {
    const runs = [];
    for (let i = 0; i < REPS; i++) {
      runs.push(await measureOnce(page, name, profile));
    }
    results[name] = { profile: { pages: profile.pages.length, dim: profile.dim },
                      ...aggregate(runs) };
  }

  await browser.close();
  server.close();

  // Report.
  const meta = {
    when: new Date().toISOString(),
    reps: REPS, orbitFrames: ORBIT_FRAMES,
    renderer: 'SwiftShader (software GL)',
    note: 'Absolute ms are software-GL; compare ratios + track regressions. ' +
          'frame ms is vsync-capped (~16.7ms/60fps) under headless Chromium, ' +
          'so it flags dropped frames rather than raw GPU headroom. destroyMs ' +
          'is dominated by WebGL context-loss, which is slow on SwiftShader and ' +
          'near-instant on real GPUs — read it as a leak check, not a hardware cost.',
  };
  const outDir = join(here, 'results');
  mkdirSync(outDir, { recursive: true });
  writeFileSync(join(outDir, 'latest.json'), JSON.stringify({ meta, results }, null, 2));

  const row = (label, r) => [
    label.padEnd(7),
    `${r.profile.pages}p ${r.profile.dim[0]}x${r.profile.dim[1]}`.padEnd(16),
    String(r.loadMs.median).padStart(8),
    String(r.medFrameMs.median).padStart(9),
    String(r.p95FrameMs.median).padStart(9),
    String(r.fps.median).padStart(6),
    String(r.heapMB.median).padStart(8),
    String(r.textures ?? '-').padStart(5),
    String(r.destroyMs.median).padStart(9),
  ].join('  ');
  const H = [['profile',7],['fixture',16],['load ms',8],['frame ms',9],['p95 ms',9],['fps',6],['heap MB',8],['tex',5],['destroy ms',9]];
  console.log('\n=== Viewer performance profile (medians over ' + REPS + ' reps) ===');
  console.log(H.map(([h,w],i) => i < 2 ? h.padEnd(w) : h.padStart(w)).join('  '));
  for (const [name, r] of Object.entries(results)) console.log(row(name, r));

  // Large-vs-light ratios, the headline comparison.
  if (results.light && results.large) {
    const ratio = (k) => results.light[k].median > 0
      ? +(results.large[k].median / results.light[k].median).toFixed(1) : 0;
    console.log('\nlarge / light ratio:  load ' + ratio('loadMs') + 'x   frame ' +
                ratio('medFrameMs') + 'x   heap ' + ratio('heapMB') + 'x');
  }
  console.log('\nWrote', join(outDir, 'latest.json'));
})();
