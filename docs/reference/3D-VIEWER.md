# The 3D Object-Inspection Viewer

The `object3d` viewer lets a player pick up a handout and turn it over in their
hands a Resident-Evil / *Nobody Wants to Die* style full-screen WebGL inspector
that rotates, zooms and pans. It shows one of two things: a **`.glb` 3D model**,
or a **procedurally-built double-sided sheet** (a scroll, a torn note, a metal
plate) whose PNG transparency punches real holes through the paper.

This document explains how that viewer works end to end: what it is built on,
how a handout's files and material settings travel from disk to the screen, how
the sheet is given real depth, and how the whole WebGL context is torn down again
so opening handout after handout never leaks. For the *shape* of the data it
reads (`view_type`, `back_texture`, `sheet_material`) see
[DATA-MODEL.md](DATA-MODEL.md); for the storage package that stores and cleans
those fields see [STORAGE.md](STORAGE.md).

---

## What it is built on

The viewer is plain [Three.js](https://threejs.org/) (r160, MIT), **self-hosted**
there is no CDN, because the app runs on a laptop at the table with no
guaranteed internet. `fetch_vendor.py` is a one-off setup step that downloads the
exact files needed and lays them out under `static/vendor/three/`:

```
static/vendor/three/
  three.module.min.js                     # the engine
  addons/loaders/GLTFLoader.js            # .glb model loader
  addons/controls/OrbitControls.js        # rotate / zoom / pan
  addons/utils/BufferGeometryUtils.js     # imported by GLTFLoader (relative path)
```

The addon sub-tree mirrors three's own `examples/jsm/` layout on purpose:
`GLTFLoader.js` imports `../utils/BufferGeometryUtils.js` by relative path, so the
folders must line up or the import breaks.

Bare specifiers (`import * as THREE from 'three'`) are resolved by an **import
map** declared in `player/_lightbox.html`:

```html
<script type="importmap">
{ "imports": {
    "three": ".../vendor/three/three.module.min.js",
    "three/addons/": ".../vendor/three/addons/"
} }
</script>
```

The map is emitted with Flask's `url_for`, so it is correct whatever path the app
is mounted under. It sits in the page body, which is fine because the reader
module is imported **lazily** long after the map has parsed (see below).

The two files that make up the viewer itself are:

| File | Role |
| --- | --- |
| `static/vendor/three/inspector3d.js` | The WebGL viewer. One self-contained ES-module class, `Inspector3D`. Builds the scene, loads the content, runs the render loop, and disposes everything on close. |
| `static/vendor/three/inspector2d.js` | The no-WebGL fallback. Same public surface (`new X(host, opts).init()` / `.destroy()`), plus it exports `supportsWebGL()`, which decides between the two. Shows a flat image (with a Flip button) or an honest "needs WebGL" notice for a model. |

Styling for both lives in `static/css/inspector3d.css`, loaded only where the
lightbox is included so it ships with the feature rather than bloating the main
stylesheet. All its colours come from the active theme's CSS custom properties,
so the viewer matches whatever theme the Master picked.

---

## Where it fits: the shared lightbox

There is no separate 3D page. Every handout carousel, book or 3D opens in the
**one shared lightbox** (`player/_lightbox.html`), which picks a renderer from the
handout's `view_type`:

```
openData(payload)
  ├─ view_type === 'book'      -> renderBook()       (StPageFlip)
  ├─ view_type === 'object3d'  -> renderObject3d()   (this document)
  └─ else                      -> renderCarousel()   (one image at a time)
```

`openData(payload)` is the single entry point. It takes a plain object, not a DOM
node, so the **same code path** serves three sources:

- a **card click** on the hub / a folder page `open(card)` reads the card's
  `data-*` attributes into a payload;
- a **POP** the watcher (`player/_pop.html`) receives a handout as JSON from
  `/api/pop` and calls `window.Lightbox.openData(...)` directly;
- a **secret reveal** typing the right password swaps the current handout for
  the linked one through the very same `openData`.

So a 3D handout inspects identically however it was opened, and none of the three
callers needs to know how the 3D viewer works.

---

## The data it reads

Three handout fields drive the 3D viewer. All are normalized by the storage layer
on load, so the viewer can trust their shape.

| Field | Meaning for the 3D viewer |
| --- | --- |
| `view_type` | Must be `object3d` for this viewer to run at all. |
| `files[0]` | The cover file. If its `reader` is `model` (a `.glb`), the viewer loads a model; otherwise `files[0]` is the **front texture** of a built sheet. |
| `back_texture` | Sheet only: the image painted on the **reverse** face. `null` reuses the front. Ignored by a model. |
| `sheet_material` | Sheet only: `{preset, roughness, metalness, thickness}` how the paper looks and how thick it is. Ignored by a model (a `.glb` brings its own materials). See [the built sheet](#the-built-sheet-and-its-real-depth). |

### How they reach the browser

Two transport routes, one shape:

- **Cards.** `hub.html` and `folder.html` render each handout as a
  `.handout-card` carrying `data-files`, `data-back-texture` and
  `data-sheet-material` (JSON in attributes). `open(card)` parses them back out.
- **Payloads.** `storage.player_payload(handout)` builds the JSON the POP poll and
  the secret-reveal endpoint return. It includes `back_texture` and
  `sheet_material` (cleaned on the way out), so a popped or revealed 3D handout
  carries everything the viewer needs.

Because both routes converge on `openData`, adding a field to the 3D viewer means
touching **three** render-side spots (the two card templates + `player_payload`)
and the reader no more.

---

## The render flow, step by step

`renderObject3d()` in the lightbox is the glue; `Inspector3D` in
`inspector3d.js` is the engine. The sequence when a 3D handout opens:

```
openData(payload)
   │  sets files / backTexture / sheetMaterial, view = 'object3d'
   ▼
renderObject3d()
   │  1. build the stage DOM: .inspector3d host + spinner + hint
   │  2. decide opts from files[0]:
   │        model?  -> opts.modelUrl = uploads/<glb>
   │        sheet?  -> opts.frontUrl = uploads/<png>
   │                   opts.backUrl  = uploads/<back_texture>   (if any)
   │                   opts.material = sheetMaterial            (if any)
   │  3. bump open3dToken  (guards the async import against a close)
   ▼
import(inspector2d.js)          ← always first: it owns supportsWebGL()
   │
   ├─ supportsWebGL() true  → import(inspector3d.js)
   │                          new Inspector3D(host, opts).init()
   │
   └─ supportsWebGL() false → new Inspector2D(host, opts).init()
                              (flat image + Flip, or a "needs WebGL" note)
```

Two things are worth calling out.

**The 2D fallback module is imported first, always.** It is tiny and
dependency-free, and it is the module that exports `supportsWebGL()`. Only if
WebGL is actually usable does the heavier `inspector3d.js` (which pulls in the
whole Three.js engine) get downloaded. A locked-down browser, a headless VM or a
GPU blacklist therefore never pays for the 3D engine at all, and still sees the
handout flat, with an explicit **"2D view"** badge so the degraded mode is
obvious rather than looking broken.

**Everything downstream treats `inspector` the same.** Both classes expose
`new X(host, opts).init()` and `.destroy()`, so `destroy3d()` and `close()` never
branch on which one is live.

### Lazy loading and the close-during-load guard

Nothing 3D is downloaded until the first `object3d` handout opens a table that
only ever uses carousels never fetches Three.js. Because that import is async, the
player can close the lightbox (or open a different handout) while the module is
still downloading. `open3dToken` is a monotonic counter bumped on every open and
on `destroy3d()`; each resolved `import().then()` checks that its captured token
is still current (and that the box isn't hidden) before touching anything. A stale
resolution simply no-ops, so a fast close mid-download can't build a viewer into a
closed lightbox.

---

## Inside `Inspector3D`

The class owns exactly one canvas and one render loop.

### init()

```
init()
  _initRenderer()   WebGLRenderer(antialias, alpha:false), pixelRatio capped at 2,
                    canvas appended to the host, sized to the host box
  _initScene()      near-black background so the object pops
  _initCamera()     45° perspective, pulled back on +Z looking at the origin
  _initLights()     ambient fill + a key light + a dim opposite fill, so the
                    BACK of a sheet isn't lost in shadow when spun around
  _initControls()   OrbitControls with damping (the fluid, weighty motion)
  _loadContent()    async: a .glb model, or a built sheet (see below)
  _observeResize()  ResizeObserver on the host + a window resize fallback
  _start()          the requestAnimationFrame loop
```

The scene renders immediately lit, orbitable, empty and the object drops in
when its async load resolves, so there is never a frozen black frame.

### The render loop

`enableDamping` gives the camera its inertia, which means `controls.update()` must
run **every frame**, not only on input, or the glide after you let go would never
settle. The loop is guarded by `_running` and `_disposed` so it stops cleanly.

### Two kinds of content

`_loadContent()` branches on the opts it was handed:

- **Model** (`opts.modelUrl`): `GLTFLoader` loads the `.glb`. `_frameObject`
  recentres it on the origin and scales it to a unit-ish box, so a wildly large or
  tiny export both frame sensibly. `_harvestDisposables` walks the loaded scene
  and records every geometry / material / texture it brought, so teardown can
  dispose them (a model packs its own).
- **Sheet** (`opts.frontUrl` [+ `opts.backUrl`]): `TextureLoader` loads the front
  (and optional back) image, then `_assembleSheet` builds the paper. This is the
  procedurally-built handout, described next.

---

## The built sheet, and its real depth

A sheet handout has no model file the viewer builds the geometry itself from the
front image. The interesting part is **thickness**.

### The problem it fixes

The sheet used to be two zero-thickness `PlaneGeometry` planes placed back to
back. Turned edge-on, it vanished to a line there was simply nothing there in
that dimension. The fix is to give the sheet a real depth while keeping the PNG
transparency working.

### How `_assembleSheet` builds it

The sheet is a `THREE.Group` of three parts, centred on the origin:

```
        front plane  (z = +thickness/2)   textured, transparent, alphaTest
   ┌───────────────────────────────┐
   │                               │  ← side wall: an open-ended box shell
   │            (interior)         │     tinted to the material, filling the gap
   │                               │
   └───────────────────────────────┘
        back plane   (z = -thickness/2)   textured (back_texture or front, flipped)
```

- **Front face** a `PlaneGeometry` at `+thickness/2`, `MeshStandardMaterial`
  with the front texture, `transparent: true`, `alphaTest: 0.5`.
- **Back face** a `PlaneGeometry` at `-thickness/2`, rotated 180° so its texture
  reads correctly from behind. Uses `back_texture` if present, otherwise the front
  texture (so a blank-backed scroll shows paper, not a void).
- **Side wall** a `BoxGeometry` sized `w × h × thickness` with its **+Z and -Z
  faces removed** (see below), leaving just the four-sided rim that fills the gap.
  It is tinted from the material: a warm parchment edge for matte paper, a mid-grey
  edge when `metalness > 0.5`.

Keeping the two faces as **separate transparent planes** (rather than texturing
one solid box) is what preserves the holes: `alphaTest` drops fully-transparent
texels on each face, and because the faces are now set apart by the thickness, a
hole shows the real interior depth and the far face through it a torn scroll
looks torn, not painted.

The sheet is sized to the front texture's aspect ratio (height normalised to 2
scene units) so it is never stretched, then `_frameSheet` sets a camera distance
that fits it.

### Opening the box ends: `_openBoxEnds`

The side wall must be a rim only an open tube so it doesn't cover the textured
faces (and their holes). `BoxGeometry` lays its faces out in a **fixed group
order**: `+X, -X, +Y, -Y, +Z, -Z`, six indices (two triangles) each, 36 total. The
`+Z` and `-Z` caps are therefore the **last 12 indices**. `_openBoxEnds` trims them
off the index buffer, leaving the four walls and keeping the shared vertex buffer
intact. (This ordering has been stable in three for many releases and is verified
against the vendored r160 build.)

### Where the material values come from

`opts.material` is `{roughness, metalness, thickness}`. The constructor runs it
through `_cleanMaterial`, which clamps `roughness`/`metalness` to 0–1 and
`thickness` to 0.005–0.5 and fills any missing key from the parchment default so
the reader is robust even if handed a partial or stale material (an old POP
payload, a hand-built call). `roughness`/`metalness` map straight onto the faces'
`MeshStandardMaterial`; `thickness` is the geometry depth.

The named presets (Paper, Parchment, Leather, Wood, Stone, Metal) and the
clamping rules live server-side in `handouts/storage/materials.py`; the browser
only ever sees the four resolved numbers. See [DATA-MODEL.md](DATA-MODEL.md#handout)
for the stored shape.

---

## Teardown: why `destroy()` is exhaustive

A player opens handout after handout in a session. Every WebGL context and every
GPU buffer that isn't released is a leak, and browsers cap the number of live
contexts leak enough and the next viewer fails to start. So `destroy()` is
deliberately total, and idempotent (the close button, the backdrop, Escape and a
POP swap can all trigger it):

```
destroy()
  1. stop the render loop          (_running = false, cancelAnimationFrame)
  2. drop the ResizeObserver + window listener
  3. controls.dispose()            (releases its canvas listeners)
  4. dispose every tracked geometry / material / texture
  5. traverse the scene, dispose any stragglers, empty the graph
  6. renderer.dispose() + forceContextLoss(), remove the <canvas>, null refs
```

Every geometry, material and texture the class creates is pushed onto a tracking
array the moment it exists, so step 4 can free them without having to know what
kind of object each was. Step 6's `forceContextLoss()` tells the driver to release
the GL context **now** rather than whenever the canvas is finally garbage-
collected, so reopening is immediate.

The lightbox's `destroy3d()` wraps this: it bumps `open3dToken` (invalidating any
in-flight import) and then calls `inspector.destroy()`. `close()` and every
handout switch call `destroy3d()` first, so a stale viewer is never left running
behind a new one.

---

## The live preview (create / edit pages)

The same `Inspector3D` class powers the **live material preview** on the master's
Create and Edit pages, so the Master sees roughness / metalness / depth before
saving. It is the reader's second consumer, and it reuses it without modification.

- The preview host is a small square canvas beside the material controls.
- Its front texture is the **picked image**, shown via `URL.createObjectURL(file)`
  no upload needed, so the preview works before the handout is saved. On the
  Edit page it falls back to the already-saved cover image when no new file has
  been picked.
- Its material is read live from the preset chips + advanced sliders.
- Rebuilds are **debounced** (~180 ms) so dragging a slider doesn't thrash the
  GPU, **token-guarded** so a superseded build is dropped, and every rebuild tears
  down the previous inspector and revokes the old object URL.
- It only ever runs for a built sheet (an image front) in the `object3d` viewer;
  choosing a `.glb`, or another viewer, tears it down and shows a hint instead.

Because the preview and the player both drive the identical `Inspector3D`, what
the Master tunes is exactly what the table will see there is no second, drifting
implementation of "how a sheet looks".

---

## Properties worth preserving

If you change this viewer, keep these intact they are load-bearing.

**Self-hosted, no CDN.** The whole point is a table with no internet. Keep Three.js
under `static/vendor/three/` and keep the import map pointed at it. If you bump the
three version, re-run `fetch_vendor.py` and re-check `_openBoxEnds` against the new
build's `BoxGeometry` face order.

**Fallback module imported first.** `supportsWebGL()` lives in `inspector2d.js`,
and importing it before the heavy engine is what keeps a no-WebGL client from
downloading Three.js it can't use. Don't invert the order.

**One public surface for both viewers.** `new X(host, opts).init()` / `.destroy()`
is what lets the lightbox treat 2D and 3D identically. A new viewer variant must
keep that surface.

**`destroy()` stays exhaustive and idempotent.** Every created geometry / material
/ texture must be tracked and disposed, and calling `destroy()` twice must be
safe. This is what stops the session-long leak.

**Separate transparent faces for the sheet.** The holes depend on the front and
back being distinct `alphaTest` planes set apart by the thickness. Merging them
into one solid textured box would flatten the depth and kill the see-through
holes.

**Sheet material is clamped in two places.** The server
(`materials.clean_sheet_material`) and the reader (`_cleanMaterial`) both clamp and
fill. Keep both: the server defends the stored record, the reader defends against
a partial payload it might be handed directly.

---

## Where this maps to code

| Concern | Code |
| --- | --- |
| Viewer selection, lazy load, DOM stage | `templates/player/_lightbox.html` (`renderObject3d`, `destroy3d`, `open3dToken`) |
| The WebGL viewer | `static/vendor/three/inspector3d.js` (`Inspector3D`) |
| The no-WebGL fallback + `supportsWebGL()` | `static/vendor/three/inspector2d.js` (`Inspector2D`) |
| Styling + the 2D badge | `static/css/inspector3d.css` |
| Cards that carry the 3D data | `templates/player/hub.html`, `templates/player/folder.html` |
| POP / reveal payload | `handouts/storage/records.py` (`player_payload`) |
| Material presets, clamping, `custom` derivation | `handouts/storage/materials.py` |
| Field normalization on load | `handouts/storage/db.py` (`_normalize`) |
| Create / edit forms + live preview | `templates/master/create.html`, `templates/master/edit.html` |
| Self-hosting the engine | `fetch_vendor.py` |

See [DATA-MODEL.md](DATA-MODEL.md) for the stored fields and [STORAGE.md](STORAGE.md)
for the storage package that defends them.
