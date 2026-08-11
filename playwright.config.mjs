// Playwright config for the viewer visual-regression suite.
//
// The suite renders the REAL viewer modules (static/vendor/three/inspector3d.js
// and inspector2d.js) in headless Chromium and compares the canvas against
// committed golden PNGs. To keep goldens stable across machines and CI:
//   - WebGL runs on SwiftShader (software), NOT the host GPU, so pixels don't
//     depend on the graphics driver;
//   - devicePixelRatio is pinned to 1 in the spec before mounting;
//   - the harness disables OrbitControls damping so a frame is final once drawn.
//
// Update goldens intentionally with:  npx playwright test --update-snapshots
import { defineConfig } from '@playwright/test';

const PORT = Number(process.env.VIS_PORT || 8099);

export default defineConfig({
  testDir: './tests/visual',
  // Snapshots live beside the spec in __screenshots__/ (see snapshotPathTemplate).
  snapshotPathTemplate: '{testDir}/__screenshots__/{arg}{ext}',
  fullyParallel: false,           // one WebGL context at a time is plenty
  workers: 1,
  reporter: [['list']],
  expect: {
    toHaveScreenshot: {
      // A small tolerance absorbs sub-pixel AA differences between SwiftShader
      // versions without letting a real rendering regression slip through.
      maxDiffPixelRatio: 0.02,
      threshold: 0.2,             // per-pixel colour distance (0..1)
      animations: 'disabled',
    },
  },
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    // Deterministic viewport; the harness stage is smaller and fixed anyway.
    viewport: { width: 800, height: 600 },
    launchOptions: {
      // Software GL so rendering is identical everywhere. These flags are the
      // crux of cross-machine stability for a WebGL snapshot suite.
      args: [
        '--use-gl=angle',
        '--use-angle=swiftshader',
        '--enable-webgl',
        '--ignore-gpu-blocklist',
        '--disable-gpu-vsync',
      ],
    },
  },
  webServer: {
    command: 'node tests/visual/serve.mjs',
    url: `http://127.0.0.1:${PORT}/tests/visual/harness.html`,
    reuseExistingServer: !process.env.CI,
    timeout: 30_000,
  },
});
