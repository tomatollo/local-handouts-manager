/**
 * Inspector3D — 3D "object inspection" viewer (Resident Evil / Nobody Wants to
 * Die style) for the Local Handouts Manager.
 *
 * A single self-contained ES-module class. It is imported LAZILY: nothing here
 * (and none of Three.js) is downloaded or run until the object3d viewer is
 * actually opened, so the rest of the app stays light. See _lightbox.html,
 * which dynamic-import()s this module the first time a player opens an
 * object3d handout.
 *
 * Two kinds of handout are supported, chosen by the caller:
 *   - a .glb 3D model  (files[0].reader === 'model'), loaded with GLTFLoader;
 *   - a double-sided sheet built procedurally from a front texture (files[0])
 *     and an optional back texture, with PNG transparency punching real holes
 *     through the paper (torn scrolls, bullet holes, ...).
 *
 * The built sheet is not a zero-thickness plane: it is given a real depth (a
 * front face, a back face, and an opaque side wall between them) so that when
 * the player turns it edge-on it still reads as a solid object rather than
 * vanishing to a line. Both the depth and the surface feel (roughness /
 * metalness) come from the handout's `material` option — see _assembleSheet.
 *
 * The class owns exactly one canvas and one render loop. init() builds the
 * scene; destroy() tears EVERYTHING down — it stops requestAnimationFrame,
 * removes the canvas from the DOM, and calls .dispose() on every geometry,
 * material, texture, the controls and the renderer, then drops all references
 * so the GC can reclaim the WebGL context. Opening and closing the viewer many
 * times in a session must not leak.
 *
 * The bare 'three' and 'three/addons/...' specifiers below are resolved by the
 * import map declared in _lightbox.html, which points them at the self-hosted
 * copies under static/vendor/three/ (fetched by fetch_vendor.py). No CDN.
 */

import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

// The material a built sheet falls back to when the caller passes none (an old
// POP payload, a hand-built call). Mirrors materials.py's parchment default and
// the look the reader hardcoded before the material was configurable, so an
// un-tuned sheet is unchanged. thickness is in scene units; the sheet's height
// is normalised to 2 (see _assembleSheet), so 0.05 is a slip of parchment.
const DEFAULT_SHEET_MATERIAL = {
    roughness: 0.85,
    metalness: 0.0,
    thickness: 0.05,
};

export class Inspector3D {
    /**
     * @param {HTMLElement} host   Element the canvas is appended to. It should
     *                             already be sized (the full-screen stage in
     *                             the lightbox); the renderer tracks its size.
     * @param {Object} opts
     * @param {string}  [opts.modelUrl]        URL of a .glb model to load.
     * @param {string}  [opts.frontUrl]        Front-face texture (sheet mode).
     * @param {string}  [opts.backUrl]         Back-face texture (sheet mode).
     * @param {Object}  [opts.material]        Sheet surface + depth:
     *                                         {roughness, metalness, thickness}.
     *                                         Missing keys fall back to the
     *                                         parchment default. Ignored for a
     *                                         .glb model (it brings its own).
     * @param {string}  [opts.background]      CSS/hex clear colour. Default a
     *                                         near-black so the object pops.
     * @param {Function}[opts.onError]         Called with an Error if loading
     *                                         the model/textures fails.
     * @param {Function}[opts.onLoaded]        Called once the object is in the
     *                                         scene (to drop a spinner, etc.).
     */
    constructor(host, opts = {}) {
        this.host = host;
        this.opts = opts;

        // Normalise the sheet material once here so every builder below reads a
        // complete, clamped object rather than re-checking each key. A .glb path
        // never touches it.
        this.material = this._cleanMaterial(opts.material);

        // Live references, all nulled out again in destroy(). Grouping the
        // disposables in arrays keeps teardown exhaustive: anything created is
        // registered here the moment it exists, so destroy() can walk them
        // without having to know what kind of object it was.
        this.renderer = null;
        this.scene = null;
        this.camera = null;
        this.controls = null;
        this.canvas = null;

        this._rafId = null;         // handle from requestAnimationFrame
        this._running = false;      // guards the loop against double-starts
        this._resizeObserver = null;
        this._disposed = false;     // destroy() is idempotent

        // Every geometry / material / texture we make, tracked for disposal.
        this._geometries = [];
        this._materials = [];
        this._textures = [];
        this._gltf = null;          // the loaded GLTF scene root, if any
        this._sheetGroup = null;    // the built sheet's parent group, if any

        // Bound once so add/removeEventListener see the same reference.
        this._onResize = this._handleResize.bind(this);
        this._renderLoop = this._renderLoop.bind(this);
    }

    /** Coerce an incoming material option into a complete, clamped object. */
    _cleanMaterial(m) {
        m = m || {};
        const clamp = (v, lo, hi, d) => {
            const n = typeof v === 'number' ? v : parseFloat(v);
            if (!isFinite(n)) return d;
            return Math.max(lo, Math.min(hi, n));
        };
        return {
            roughness: clamp(m.roughness, 0, 1, DEFAULT_SHEET_MATERIAL.roughness),
            metalness: clamp(m.metalness, 0, 1, DEFAULT_SHEET_MATERIAL.metalness),
            thickness: clamp(m.thickness, 0.005, 0.5, DEFAULT_SHEET_MATERIAL.thickness),
        };
    }

    // =====================================================================
    // INITIALISATION  (build the scene; nothing here is torn down)
    // =====================================================================

    /**
     * Build the renderer, scene, camera, lights and controls, kick off the
     * content load, and start the render loop. Returns this for chaining.
     */
    init() {
        this._initRenderer();
        this._initScene();
        this._initCamera();
        this._initLights();
        this._initControls();

        // Content is async (network). The scene renders (empty, but lit and
        // orbitable) immediately; the object drops in when its load resolves.
        this._loadContent();

        this._observeResize();
        this._start();
        return this;
    }

    _initRenderer() {
        // antialias for clean edges on the sheet / model silhouette; alpha off
        // because we paint an opaque background (a transparent canvas would
        // show the dimmed handout behind it and muddy the "inspection" feel).
        this.renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: false,
            powerPreference: 'high-performance',
        });
        // Cap the pixel ratio: retina phones would otherwise render 3-4x the
        // pixels for no visible gain and a real battery/perf cost.
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
        const { width, height } = this._hostSize();
        this.renderer.setSize(width, height, false);
        this.renderer.outputColorSpace = THREE.SRGBColorSpace;

        this.canvas = this.renderer.domElement;
        this.canvas.classList.add('inspector3d__canvas');
        // Fill the host; the stage positions it.
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.display = 'block';
        this.canvas.style.touchAction = 'none';   // we own the touch gestures
        this.host.appendChild(this.canvas);
    }

    _initScene() {
        this.scene = new THREE.Scene();
        const bg = this.opts.background || '#0b0b0d';
        this.scene.background = new THREE.Color(bg);
    }

    _initCamera() {
        const { width, height } = this._hostSize();
        this.camera = new THREE.PerspectiveCamera(
            45, width / Math.max(1, height), 0.01, 100);
        // Pulled back on +Z looking at the origin; a comfortable "held object"
        // framing. OrbitControls takes over from here.
        this.camera.position.set(0, 0, 3);
    }

    _initLights() {
        // Ambient fills the shadows so no face is pure black; the directional
        // key gives shape and a soft highlight on the material. Two lights are
        // plenty for an inspected prop and keep the frame cheap. A metallic
        // sheet needs a bit more of a defined highlight to read as metal, but
        // the rig here is enough for that too (metalness shows against the key).
        const ambient = new THREE.AmbientLight(0xffffff, 0.9);
        this.scene.add(ambient);

        const key = new THREE.DirectionalLight(0xffffff, 1.6);
        key.position.set(2, 3, 4);
        this.scene.add(key);

        // A dim opposite fill so the BACK of a sheet (or the far side of a
        // model) isn't lost in shadow when the player spins it around.
        const fill = new THREE.DirectionalLight(0xffffff, 0.5);
        fill.position.set(-2, -1, -3);
        this.scene.add(fill);
        // Lights need no dispose(); leaving the scene (in destroy) is enough.
    }

    _initControls() {
        this.controls = new OrbitControls(this.camera, this.canvas);
        // enableDamping gives the fluid, weighty motion asked for; it needs
        // controls.update() every frame (see the render loop).
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.08;
        this.controls.rotateSpeed = 0.9;
        this.controls.panSpeed = 0.7;
        this.controls.zoomSpeed = 0.9;
        this.controls.enablePan = true;
        // Sensible zoom bounds so the object can't be lost behind the camera
        // or shrunk to a dot.
        this.controls.minDistance = 0.4;
        this.controls.maxDistance = 12;
    }

    // ---- content: either a GLB model, or a double-sided sheet ------------

    _loadContent() {
        if (this.opts.modelUrl) {
            this._loadModel(this.opts.modelUrl);
        } else if (this.opts.frontUrl) {
            this._buildSheet(this.opts.frontUrl, this.opts.backUrl || null);
        } else {
            this._fail(new Error('Inspector3D: no modelUrl or frontUrl given.'));
        }
    }

    _loadModel(url) {
        const loader = new GLTFLoader();
        loader.load(
            url,
            (gltf) => {
                if (this._disposed) return;   // closed mid-load
                this._gltf = gltf.scene;

                // Register every geometry/material/texture the model brought so
                // destroy() can dispose them. Traversal here is the ONLY place
                // that knows the model's internals, so we harvest them now.
                this._harvestDisposables(gltf.scene);

                // Centre the model on the origin and scale it to a unit-ish box
                // so wildly different exports all frame sensibly.
                this._frameObject(gltf.scene);
                this.scene.add(gltf.scene);
                this._loaded();
            },
            undefined,
            (err) => this._fail(err),
        );
    }

    _buildSheet(frontUrl, backUrl) {
        const loader = new THREE.TextureLoader();
        let pending = backUrl ? 2 : 1;
        let frontTex = null;
        let backTex = null;

        const done = () => {
            if (this._disposed) return;
            this._assembleSheet(frontTex, backTex);
            this._loaded();
        };

        const onOne = () => { if (--pending <= 0) done(); };

        frontTex = loader.load(
            frontUrl,
            () => onOne(),
            undefined,
            (err) => this._fail(err),
        );
        this._prepTexture(frontTex);

        if (backUrl) {
            backTex = loader.load(
                backUrl,
                () => onOne(),
                undefined,
                (err) => this._fail(err),
            );
            this._prepTexture(backTex);
        }
    }

    /**
     * Build a sheet with REAL depth so it doesn't disappear edge-on.
     *
     * Three parts, all parented to one group centred on the origin:
     *   - a front textured plane at +thickness/2,
     *   - a back textured plane at -thickness/2 (rotated 180° so its texture
     *     reads correctly from behind),
     *   - an opaque side wall (an open-ended box shell) filling the gap between
     *     them, tinted to the material so the edge looks like the paper/metal's
     *     own thickness rather than a black seam.
     *
     * Keeping the two faces as separate transparent planes (rather than one
     * solid box with the texture on every side) is what preserves the PNG-hole
     * effect: alphaTest still punches holes through each face, and because the
     * faces are now set apart by the thickness, a hole shows the real interior
     * depth and the far face through it. roughness/metalness come from the
     * material so a "metal plate" reads glossy and a "stone tablet" dead-matte.
     */
    _assembleSheet(frontTex, backTex) {
        // Size the sheet to the front texture's aspect ratio so it isn't
        // stretched; fall back to A-series portrait if the image size is
        // somehow unavailable.
        let aspect = 1 / 1.414;
        const img = frontTex && frontTex.image;
        if (img && img.width && img.height) aspect = img.width / img.height;
        const h = 2;
        const w = h * aspect;
        const t = this.material.thickness;   // full depth
        const halfT = t / 2;

        const rough = this.material.roughness;
        const metal = this.material.metalness;

        // A group so the whole sheet frames + orbits as one object.
        const group = new THREE.Group();
        this._sheetGroup = group;

        // ---- Front face ----
        const geoFront = new THREE.PlaneGeometry(w, h);
        this._geometries.push(geoFront);
        const matFront = new THREE.MeshStandardMaterial({
            map: frontTex,
            transparent: true,
            // alphaTest drops fully-transparent texels so holes are crisp AND
            // don't fight the depth buffer. 0.5 suits the hard edges of a torn
            // scroll / punched hole.
            alphaTest: 0.5,
            side: THREE.FrontSide,
            roughness: rough,
            metalness: metal,
        });
        this._materials.push(matFront);
        const front = new THREE.Mesh(geoFront, matFront);
        front.position.z = halfT;
        group.add(front);
        this._sheetFront = front;

        // ---- Back face ----
        // Reuse the front texture (flipped) when no dedicated back was given so
        // a blank-backed scroll shows the same paper rather than a void.
        const geoBack = new THREE.PlaneGeometry(w, h);
        this._geometries.push(geoBack);
        const backMap = backTex || frontTex;
        const matBack = new THREE.MeshStandardMaterial({
            map: backMap,
            transparent: true,
            alphaTest: 0.5,
            side: THREE.FrontSide,
            roughness: rough,
            metalness: metal,
        });
        this._materials.push(matBack);
        const back = new THREE.Mesh(geoBack, matBack);
        back.position.z = -halfT;
        back.rotation.y = Math.PI;     // face the other way
        group.add(back);
        this._sheetBack = back;

        // ---- Side wall (the visible thickness) ----
        // An open-ended box (no front/back caps — the textured planes are those)
        // whose four side faces fill the gap between front and back. Tinted from
        // the texture's average-ish tone would be ideal, but a neutral parchment/
        // metal tone keyed off metalness reads well and needs no pixel readback:
        // a metallic sheet gets a mid-grey edge, a matte one a warm paper edge.
        const edgeColor = metal > 0.5 ? 0x9a9a9a : 0xcbb994;
        const geoEdge = new THREE.BoxGeometry(w, h, t);
        // Drop the front (+Z) and back (-Z) faces of the box so only the rim
        // remains; the textured planes provide the faces (and keep their holes).
        this._openBoxEnds(geoEdge);
        this._geometries.push(geoEdge);
        const matEdge = new THREE.MeshStandardMaterial({
            color: edgeColor,
            roughness: Math.min(1, rough + 0.05),
            metalness: metal,
            side: THREE.DoubleSide,
        });
        this._materials.push(matEdge);
        const edge = new THREE.Mesh(geoEdge, matEdge);
        group.add(edge);
        this._sheetEdge = edge;

        this.scene.add(group);

        // Frame the group (centred on the origin already, so just set a camera
        // distance that fits the taller dimension).
        this._frameSheet(Math.max(w, h));
    }

    /**
     * Remove the +Z and -Z faces from a BoxGeometry so it becomes an open tube
     * (a rim only). BoxGeometry lays its faces out in a fixed group order:
     * +X, -X, +Y, -Y, +Z, -Z, six vertices (two triangles) each. Dropping the
     * last two groups' 12 indices leaves the four side walls. Done by trimming
     * the index buffer, which keeps the shared vertex buffer intact.
     */
    _openBoxEnds(box) {
        const index = box.getIndex();
        if (!index) return;                      // non-indexed: leave as-is
        const arr = index.array;
        // 6 faces * 6 indices = 36; the +Z/-Z faces are the last 12.
        if (arr.length >= 36) {
            const trimmed = arr.slice(0, arr.length - 12);
            box.setIndex(new THREE.BufferAttribute(trimmed, 1));
        }
    }

    // =====================================================================
    // RUNTIME
    // =====================================================================

    _start() {
        if (this._running || this._disposed) return;
        this._running = true;
        this._rafId = requestAnimationFrame(this._renderLoop);
    }

    _renderLoop() {
        if (!this._running || this._disposed) return;
        // Damping means the camera keeps easing after the pointer stops, so
        // update() must run every frame, not only on input.
        if (this.controls) this.controls.update();
        if (this.renderer && this.scene && this.camera) {
            this.renderer.render(this.scene, this.camera);
        }
        this._rafId = requestAnimationFrame(this._renderLoop);
    }

    // =====================================================================
    // DESTRUCTION  (stop the loop; free the GPU + RAM; drop every reference)
    // =====================================================================

    /**
     * Total teardown. Idempotent: safe to call more than once (the lightbox
     * close path and an unmount could both fire). After it returns, this
     * instance holds no THREE objects and no WebGL context.
     */
    destroy() {
        if (this._disposed) return;
        this._disposed = true;

        // 1. Halt the render loop FIRST so nothing touches objects mid-dispose.
        this._running = false;
        if (this._rafId !== null) {
            cancelAnimationFrame(this._rafId);
            this._rafId = null;
        }

        // 2. Stop observing size and drop the window listener.
        this._unobserveResize();

        // 3. Controls hold DOM listeners on the canvas; dispose releases them.
        if (this.controls) {
            this.controls.dispose();
            this.controls = null;
        }

        // 4. Dispose every geometry, material and texture we tracked. Order
        //    doesn't matter — dispose() just frees GPU buffers — but doing
        //    materials' maps too catches any texture a material owns that we
        //    didn't separately register (e.g. from the GLTF harvest).
        for (const geo of this._geometries) {
            if (geo && geo.dispose) geo.dispose();
        }
        for (const mat of this._materials) {
            this._disposeMaterial(mat);
        }
        for (const tex of this._textures) {
            if (tex && tex.dispose) tex.dispose();
        }
        this._geometries.length = 0;
        this._materials.length = 0;
        this._textures.length = 0;

        // 5. Empty the scene graph so no node keeps a child alive.
        if (this.scene) {
            this.scene.traverse((obj) => {
                if (obj.isMesh) {
                    if (obj.geometry && obj.geometry.dispose) obj.geometry.dispose();
                    this._disposeMaterial(obj.material);
                }
            });
            this._clearChildren(this.scene);
            this.scene = null;
        }
        this._gltf = null;
        this._sheetGroup = null;
        this._sheetFront = null;
        this._sheetBack = null;
        this._sheetEdge = null;

        // 6. Renderer last: lose the context and remove the canvas from the DOM
        //    so the browser can reclaim the WebGL backing immediately.
        if (this.renderer) {
            this.renderer.dispose();
            // forceContextLoss() tells the driver to release the GL context
            // now, rather than whenever the canvas is finally GC'd. Wrapped
            // because a few implementations don't expose it.
            try {
                const gl = this.renderer.getContext && this.renderer.getContext();
                const lose = gl && gl.getExtension && gl.getExtension('WEBGL_lose_context');
                if (lose) lose.loseContext();
            } catch (e) { /* best-effort */ }
            if (typeof this.renderer.forceContextLoss === 'function') {
                try { this.renderer.forceContextLoss(); } catch (e) { /* ignore */ }
            }
            this.renderer = null;
        }
        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
        }
        this.canvas = null;
        this.camera = null;
        this.host = null;
    }

    // =====================================================================
    // Helpers
    // =====================================================================

    _hostSize() {
        const rect = this.host ? this.host.getBoundingClientRect() : null;
        return {
            width: Math.max(1, rect ? rect.width : window.innerWidth),
            height: Math.max(1, rect ? rect.height : window.innerHeight),
        };
    }

    _observeResize() {
        // ResizeObserver catches the stage growing (orientation change, the
        // browser chrome hiding on mobile). A window listener is the fallback.
        if (typeof ResizeObserver !== 'undefined') {
            this._resizeObserver = new ResizeObserver(this._onResize);
            this._resizeObserver.observe(this.host);
        }
        window.addEventListener('resize', this._onResize);
    }

    _unobserveResize() {
        if (this._resizeObserver) {
            this._resizeObserver.disconnect();
            this._resizeObserver = null;
        }
        window.removeEventListener('resize', this._onResize);
    }

    _handleResize() {
        if (this._disposed || !this.renderer || !this.camera) return;
        const { width, height } = this._hostSize();
        this.renderer.setSize(width, height, false);
        this.camera.aspect = width / Math.max(1, height);
        this.camera.updateProjectionMatrix();
    }

    _prepTexture(tex) {
        if (!tex) return;
        tex.colorSpace = THREE.SRGBColorSpace;
        tex.anisotropy = 4;
        this._textures.push(tex);
    }

    /** Walk a loaded GLTF scene and register its disposables. */
    _harvestDisposables(root) {
        root.traverse((obj) => {
            if (!obj.isMesh) return;
            if (obj.geometry) this._geometries.push(obj.geometry);
            const mats = Array.isArray(obj.material) ? obj.material : [obj.material];
            for (const m of mats) {
                if (!m) continue;
                this._materials.push(m);
                // Collect any textures the material references so they're
                // disposed too (GLTF packs base-colour, normal, ORM, ...).
                for (const key of ['map', 'normalMap', 'roughnessMap',
                    'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap']) {
                    if (m[key]) this._textures.push(m[key]);
                }
            }
        });
    }

    _disposeMaterial(material) {
        if (!material) return;
        const mats = Array.isArray(material) ? material : [material];
        for (const m of mats) {
            if (!m) continue;
            // Free any textures still hanging off the material.
            for (const key of ['map', 'normalMap', 'roughnessMap',
                'metalnessMap', 'aoMap', 'emissiveMap', 'alphaMap']) {
                if (m[key] && m[key].dispose) m[key].dispose();
            }
            if (m.dispose) m.dispose();
        }
    }

    _clearChildren(obj) {
        while (obj.children && obj.children.length) {
            obj.remove(obj.children[0]);
        }
    }

    /** Centre + scale an arbitrary model to a ~unit box and frame the camera. */
    _frameObject(object) {
        const box = new THREE.Box3().setFromObject(object);
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z) || 1;

        // Recentre on the origin so OrbitControls spins around the object.
        object.position.sub(center);
        // Normalise scale so a huge or tiny export both fit the same framing.
        const scale = 1.6 / maxDim;
        object.scale.setScalar(scale);

        if (this.controls) {
            this.controls.target.set(0, 0, 0);
            this.controls.update();
        }
        if (this.camera) {
            this.camera.position.set(0, 0, 3);
            this.camera.updateProjectionMatrix();
        }
    }

    _frameSheet(largestSide) {
        if (this.controls) {
            this.controls.target.set(0, 0, 0);
            this.controls.update();
        }
        if (this.camera) {
            // Distance that comfortably fits the sheet in a 45° FOV.
            const dist = (largestSide / 2) / Math.tan((45 * Math.PI / 180) / 2);
            this.camera.position.set(0, 0, dist * 1.35);
            this.camera.updateProjectionMatrix();
        }
    }

    _loaded() {
        if (this._disposed) return;
        if (typeof this.opts.onLoaded === 'function') {
            try { this.opts.onLoaded(); } catch (e) { /* ignore */ }
        }
    }

    _fail(err) {
        if (this._disposed) return;
        if (typeof this.opts.onError === 'function') {
            try { this.opts.onError(err); } catch (e) { /* ignore */ }
        } else {
            // eslint-disable-next-line no-console
            console.error('Inspector3D:', err);
        }
    }
}

export default Inspector3D;
