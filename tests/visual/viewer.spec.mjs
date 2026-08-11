// Visual-regression tests for the object3d viewer canvas rendering.
//
// What is covered:
//   1. Inspector3D sheet render (front + back textures) — the WebGL canvas.
//   2. Inspector3D sheet with PNG alpha holes — exercises alphaTest so a
//      regression in the "torn paper" material shows up as a pixel diff.
//   3. Inspector2D sheet fallback — the flat no-WebGL DOM view (front, then
//      flipped to back).
//   4. Inspector2D model notice — the honest "needs WebGL" message for a .glb.
//   5. Teardown leak check — destroy() must remove the canvas so repeated
//      opens don't pile up WebGL contexts.
//
// Goldens are the committed PNGs under __screenshots__/. Regenerate on purpose
// with `--update-snapshots`; a diff otherwise fails the run.
import { test, expect } from '@playwright/test';

const HARNESS = '/tests/visual/harness.html';
const FX = '/tests/visual/fixtures';

// Pin devicePixelRatio to 1 BEFORE any module loads, so the renderer's
// setPixelRatio(min(dpr,2)) can't change the canvas backing size between hosts.
test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(window, 'devicePixelRatio', { get: () => 1 });
  });
  await page.goto(HARNESS);
  await page.waitForFunction(() => window.__harnessReady === true);
});

// Mount a viewer via a harness hook, wait for its onLoaded, then draw a couple
// of settled frames so the screenshot is of finished content.
async function mountAndSettle(page, fn, opts) {
  await page.evaluate(([fn, opts]) => window[fn](opts), [fn, opts]);
  await page.waitForFunction(() => window.__viewerReady === true, { timeout: 15_000 });
  const err = await page.evaluate(() => window.__viewerError);
  expect(err, 'viewer reported no load error').toBeNull();
  // Two rAF-spaced renders to let controls.update() + material compile settle.
  for (let i = 0; i < 3; i++) {
    await page.evaluate(() => window.renderOnce());
    await page.waitForTimeout(50);
  }
}

test('3D sheet renders front + back', async ({ page }) => {
  await mountAndSettle(page, 'mount3D', {
    frontUrl: `${FX}/front.png`,
    backUrl: `${FX}/back.png`,
    background: '#0b0b0d',
  });
  const canvas = page.locator('#stage canvas');
  await expect(canvas).toHaveScreenshot('sheet-3d-front.png');
});

test('3D sheet renders alpha holes (torn paper)', async ({ page }) => {
  await mountAndSettle(page, 'mount3D', {
    frontUrl: `${FX}/holed.png`,
    background: '#0b0b0d',
  });
  const canvas = page.locator('#stage canvas');
  await expect(canvas).toHaveScreenshot('sheet-3d-holed.png');
});

test('2D fallback sheet renders and flips', async ({ page }) => {
  await mountAndSettle(page, 'mount2D', {
    frontUrl: `${FX}/front.png`,
    backUrl: `${FX}/back.png`,
    strings: { flipToBack: 'Flip to back', flipToFront: 'Flip to front', fallbackBadge: '2D view' },
  });
  const root = page.locator('#stage .inspector2d');
  await expect(root).toHaveScreenshot('sheet-2d-front.png');

  // Flip to the back face and snapshot again.
  await page.locator('.inspector2d__flip').click();
  await page.waitForTimeout(50);
  await expect(root).toHaveScreenshot('sheet-2d-back.png');
});

test('2D fallback shows model notice for a .glb', async ({ page }) => {
  await mountAndSettle(page, 'mount2D', {
    modelUrl: '/some/model.glb',
    strings: { modelNeedsWebgl: 'This 3D model needs WebGL, which is unavailable here.', fallbackBadge: '2D view' },
  });
  const root = page.locator('#stage .inspector2d');
  await expect(root).toHaveScreenshot('model-2d-notice.png');
});

test('destroy() removes the canvas (no leak across opens)', async ({ page }) => {
  for (let i = 0; i < 3; i++) {
    await mountAndSettle(page, 'mount3D', { frontUrl: `${FX}/front.png` });
    expect(await page.evaluate(() => window.canvasCount())).toBe(1);
    await page.evaluate(() => window.destroyViewer());
    expect(await page.evaluate(() => window.canvasCount())).toBe(0);
  }
});
