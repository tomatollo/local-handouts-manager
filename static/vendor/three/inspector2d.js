/**
 * Inspector2D — lightweight 2D fallback for the object3d handout viewer.
 *
 * Some environments have no usable WebGL: locked-down browsers, virtualised /
 * headless machines, GPU blacklists, or a player on very old hardware. In those
 * cases Inspector3D cannot start (its WebGLRenderer constructor throws), and the
 * player would otherwise be left with the error overlay and no way to see the
 * handout at all. This module is the graceful degradation for that case.
 *
 * It deliberately exposes the SAME public surface as Inspector3D —
 *   new Inspector2D(host, opts).init()   and   .destroy()
 * with the same opts (modelUrl | frontUrl [+ backUrl], onLoaded, onError) — so
 * the lightbox can pick one or the other by capability and treat them
 * identically afterwards (see _lightbox.html, renderObject3d + supportsWebGL).
 *
 * What it renders, with NO WebGL / no Three.js:
 *   - Sheet handouts (frontUrl [+ backUrl]): the front image shown flat, with
 *     a "Flip" button to swap to the back when a back texture exists. Plain
 *     <img> pan/zoom is left to the lightbox's own 2D zoom machinery (the
 *     media modifier class is set so that path applies), so this stays tiny.
 *   - Model handouts (modelUrl, a .glb): there is no software glTF rasteriser
 *     here, so it shows a clear, translated notice that the 3D model needs
 *     WebGL, rather than pretending to render it. A poster image can be passed
 *     via opts.posterUrl to show *something* representative if available.
 *
 * Everything created is torn down in destroy(): the DOM subtree is removed and
 * every listener is dropped. destroy() is idempotent.
 *
 * No imports: this file loads and runs on its own, which is the whole point —
 * it must work exactly where the ES-module + WebGL stack does not.
 */

export class Inspector2D {
    /**
     * @param {HTMLElement} host  Element the fallback UI is appended to (the
     *                            same full-stage host Inspector3D would use).
     * @param {Object} opts
     * @param {string} [opts.modelUrl]  A .glb model URL (cannot be rasterised
     *                                  without WebGL; a notice is shown).
     * @param {string} [opts.frontUrl]  Front-face image (sheet mode).
     * @param {string} [opts.backUrl]   Back-face image (sheet mode).
     * @param {string} [opts.posterUrl] Optional still to show for a model.
     * @param {Object} [opts.strings]   Translated UI strings (see defaults in
     *                                  _STRINGS); the lightbox passes these so
     *                                  copy stays localised without this module
     *                                  needing the i18n layer.
     * @param {Function}[opts.onLoaded] Called once content is on screen.
     * @param {Function}[opts.onError]  Called with an Error if even the 2D
     *                                  fallback cannot show anything.
     */
    constructor(host, opts = {}) {
        this.host = host;
        this.opts = opts;
        this._disposed = false;

        // The single subtree we own; removed wholesale in destroy().
        this._root = null;
        // Bound listeners kept so destroy() can remove the exact references.
        this._onFlip = null;
        this._flipBtn = null;
        this._imgFront = null;
        this._imgBack = null;
        this._showingBack = false;

        this._strings = Object.assign({}, Inspector2D._STRINGS, opts.strings || {});
    }

    // Default English copy; overridden by opts.strings (already translated).
    static get _STRINGS() {
        return {
            flipToBack: 'Flip to back',
            flipToFront: 'Flip to front',
            modelNeedsWebgl:
                'This 3D model needs WebGL, which is unavailable here. ' +
                'Open it in a browser with 3D graphics enabled to inspect it.',
            imageError: 'This handout could not be loaded.',
            fallbackBadge: '2D view',
        };
    }

    // =====================================================================
    // INITIALISATION
    // =====================================================================

    init() {
        if (this._disposed) return this;

        const root = document.createElement('div');
        root.className = 'inspector2d';
        this._root = root;

        // A small corner badge makes the degraded mode explicit, so a player
        // (or the Master helping them) understands why it looks flat and isn't
        // left wondering whether the 3D view is broken.
        const badge = document.createElement('span');
        badge.className = 'inspector2d__badge';
        badge.textContent = this._strings.fallbackBadge;
        root.appendChild(badge);

        this.host.appendChild(root);

        if (this.opts.frontUrl) {
            this._buildSheet(this.opts.frontUrl, this.opts.backUrl || null);
        } else if (this.opts.modelUrl) {
            this._buildModelNotice(this.opts.posterUrl || null);
        } else {
            this._fail(new Error('Inspector2D: no frontUrl or modelUrl given.'));
        }
        return this;
    }

    // ---- sheet: flat front image, optional flip to a back image ----------

    _buildSheet(frontUrl, backUrl) {
        const wrap = document.createElement('div');
        wrap.className = 'inspector2d__sheet';

        const front = document.createElement('img');
        front.className = 'inspector2d__img inspector2d__img--front';
        front.alt = '';
        front.decoding = 'async';
        front.addEventListener('error', this._onImgError.bind(this), { once: true });
        front.addEventListener('load', this._loadedOnce.bind(this), { once: true });
        front.src = frontUrl;
        this._imgFront = front;
        wrap.appendChild(front);

        if (backUrl) {
            const back = document.createElement('img');
            back.className = 'inspector2d__img inspector2d__img--back';
            back.alt = '';
            back.decoding = 'async';
            back.hidden = true;
            back.src = backUrl;
            this._imgBack = back;
            wrap.appendChild(back);

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'inspector2d__flip';
            btn.textContent = this._strings.flipToBack;
            this._onFlip = this._flip.bind(this);
            btn.addEventListener('click', this._onFlip);
            this._flipBtn = btn;
            wrap.appendChild(btn);
        }

        this._root.appendChild(wrap);
    }

    _flip() {
        if (this._disposed || !this._imgFront || !this._imgBack) return;
        this._showingBack = !this._showingBack;
        this._imgFront.hidden = this._showingBack;
        this._imgBack.hidden = !this._showingBack;
        if (this._flipBtn) {
            this._flipBtn.textContent = this._showingBack
                ? this._strings.flipToFront
                : this._strings.flipToBack;
        }
    }

    // ---- model: no software rasteriser, so a clear notice (+ poster) -----

    _buildModelNotice(posterUrl) {
        const wrap = document.createElement('div');
        wrap.className = 'inspector2d__model';

        if (posterUrl) {
            const poster = document.createElement('img');
            poster.className = 'inspector2d__poster';
            poster.alt = '';
            poster.decoding = 'async';
            poster.src = posterUrl;
            wrap.appendChild(poster);
        }

        const note = document.createElement('p');
        note.className = 'inspector2d__note';
        note.textContent = this._strings.modelNeedsWebgl;
        wrap.appendChild(note);

        this._root.appendChild(wrap);
        // A notice IS the successful render for the model case: resolve the
        // loading state so the spinner drops.
        this._loaded();
    }

    // =====================================================================
    // DESTRUCTION
    // =====================================================================

    destroy() {
        if (this._disposed) return;
        this._disposed = true;

        if (this._flipBtn && this._onFlip) {
            this._flipBtn.removeEventListener('click', this._onFlip);
        }
        this._onFlip = null;
        this._flipBtn = null;
        this._imgFront = null;
        this._imgBack = null;

        if (this._root && this._root.parentNode) {
            this._root.parentNode.removeChild(this._root);
        }
        this._root = null;
        this.host = null;
    }

    // =====================================================================
    // Helpers
    // =====================================================================

    _loadedOnce() { this._loaded(); }

    _onImgError() {
        this._fail(new Error('Inspector2D: image failed to load.'));
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
            console.error('Inspector2D:', err);
        }
    }
}

/**
 * Feature-detect a usable WebGL context. Returns true only if a real context
 * can be created — the mere presence of the constructor is not enough (drivers
 * can be blacklisted so getContext still returns null). Cached after the first
 * call because the answer cannot change within a page load, and creating throw-
 * away contexts is not free.
 */
let _webglCache = null;
export function supportsWebGL() {
    if (_webglCache !== null) return _webglCache;
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') ||
                   canvas.getContext('experimental-webgl');
        _webglCache = !!(gl && typeof gl.getParameter === 'function');
        // Release the probe context promptly.
        if (gl) {
            const lose = gl.getExtension && gl.getExtension('WEBGL_lose_context');
            if (lose) lose.loseContext();
        }
    } catch (e) {
        _webglCache = false;
    }
    return _webglCache;
}

export default Inspector2D;
