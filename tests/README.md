# Viewer tests & profiling

Dev-only JavaScript tooling for the **object3d handout viewer** (the WebGL
"object inspection" reader in `static/vendor/three/inspector3d.js`, its 2D
fallback `inspector2d.js`, and the lightbox that hosts them). The Flask app has
no Node dependency; nothing here ships to players.

Two things live here:

- **`tests/visual/`** — visual-regression tests that render the *real* viewer
  modules in headless Chromium and diff the canvas against golden PNGs.
- **`tests/perf/`** — a performance profiler that measures load time, frame
  time, heap and teardown for a *light* handout vs a *large* one (many
  high-resolution pages).

Both run the viewer in isolation against generated fixture textures — no
database, uploads, or Master login required — which is what keeps them fast and
reproducible.

## One-time setup

    npm install
    npm run setup        # downloads the Chromium build Playwright needs

`npm install` pins Playwright to **1.56.x**; `npm run setup` fetches the exact
matching browser. (If your machine already provisions Playwright browsers to a
shared path, point at it with `PLAYWRIGHT_BROWSERS_PATH=/path node ...` instead.)

## Visual regression

    npm run test:visual            # generate fixtures, then diff vs goldens

On a clean checkout there are no goldens yet, so the **first** run must record
them:

    npm run test:visual:update     # writes tests/visual/__screenshots__/*.png

Review those PNGs, then re-run `npm run test:visual` — it should pass with zero
diffs. After that, any change that alters the rendered output fails the run and
drops a diff image under `test-results/`. When a change is *intended* (you
edited the material, lighting, framing, or the fallback markup), re-record with
`test:visual:update` and commit the new goldens.

What's covered (`tests/visual/viewer.spec.mjs`):

1. 3D sheet render (front + back textures) — the WebGL canvas.
2. 3D sheet with PNG alpha holes — guards the `alphaTest` "torn paper" material.
3. 2D fallback sheet — the flat no-WebGL view, front then flipped to back.
4. 2D fallback model notice — the honest "needs WebGL" message for a `.glb`.
5. Teardown leak check — `destroy()` must leave zero canvases behind.

### Why it's stable across machines

WebGL rendering normally varies by GPU/driver, which would make golden diffing
useless. The suite removes that variance:

- **SwiftShader** (software GL) via the launch flags in
  `playwright.config.mjs`, so pixels don't depend on the host GPU.
- **`devicePixelRatio` pinned to 1** in the spec before the module loads, so the
  canvas backing-store size is identical everywhere.
- **OrbitControls damping disabled** in the harness, so a frame is final as soon
  as it's drawn (no easing tail).

A small `maxDiffPixelRatio` tolerance still absorbs sub-pixel AA differences
between SwiftShader versions. If you upgrade the pinned Playwright (and thus the
Chromium/SwiftShader build), re-record goldens in the same commit.

Goldens are `.gitignore`d by default because the "correct" pixels depend on the
local SwiftShader build. If your CI uses a fixed Playwright version (recommended),
un-ignore `tests/visual/__screenshots__/` and commit the goldens so CI diffs
against them.

## Performance profiling

    npm run profile                       # default: 5 reps, 24 large pages @2048px

Tune the workload:

    node tests/perf/make-perf-fixtures.mjs --large-pages 40 --large-dim 4096
    node tests/perf/profile.mjs --reps 8 --orbit-frames 180

It prints a table and writes `tests/perf/results/latest.json`. Columns:

| column      | meaning |
|-------------|---------|
| `load ms`   | mount → `onLoaded`: texture decode + GPU upload + first frame |
| `frame ms`  | median frame time during a scripted orbit (per-frame render cost) |
| `p95 ms`    | 95th-percentile frame time — catches hitches (e.g. shader compile) |
| `fps`       | derived from median frame time |
| `heap MB`   | JS heap growth from before-mount to loaded (working-set signal) |
| `tex`       | live GPU textures the renderer reports (footprint proxy) |
| `destroy ms`| teardown time; also hard-asserts the canvas count returns to 0 |

### Reading the numbers

The profiler runs on **SwiftShader**, so absolute milliseconds are *software*
timings — slower than real hardware and meaningful mainly for **comparison**:
the large-vs-light ratio, and regressions over time on the same machine. Two
caveats baked into the output's `note` field:

- **`frame ms` is vsync-capped** (~16.7 ms / 60 fps) under headless Chromium, so
  it flags *dropped* frames rather than raw GPU headroom. A large handout whose
  `frame ms` climbs above ~17 ms is dropping frames and worth investigating.
- **`destroy ms` is dominated by WebGL context-loss**, which is slow on
  SwiftShader and near-instant on a real GPU. Treat it as a *leak check* (does
  teardown complete and free the canvas?), not a hardware cost.

The expected shape: large handouts cost several times the **load** of light ones
(big textures to decode and upload) while **steady-state frame time is
basically identical** — once uploaded, the sheet is the same two-triangle draw
regardless of texture resolution. If that stops being true (frame time scaling
with page count/resolution), something regressed.

## Files

    playwright.config.mjs            visual-suite config (SwiftShader flags, snapshot path)
    package.json                     dev deps + npm scripts (pinned Playwright)
    tests/visual/
      harness.html                   loads the real viewer modules; exposes mount/destroy hooks
      viewer.spec.mjs                the visual-regression tests
      make-fixtures.mjs              deterministic golden fixtures (front/holed/back)
      server.mjs                     tiny static server (serves project root)
      serve.mjs                      webServer entry point Playwright launches
      __screenshots__/               goldens (generated; commit deliberately)
      fixtures/                      generated (git-ignored)
    tests/perf/
      harness.html                   viewer + frame-time / render-info instrumentation
      make-perf-fixtures.mjs         light + large texture profiles (+ manifest.json)
      profile.mjs                    the profiler driver
      fixtures/  results/            generated (git-ignored)
