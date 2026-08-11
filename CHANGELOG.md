# Changelog

All notable changes to this project are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not use formal version numbers yet, so changes are grouped by
the phase of work that produced them, newest first.

## Unreleased

### Documentation
- **README rewritten** and brought back in sync with the code: all ten themes
  listed, the interactive map documented, the desktop launcher covered, the
  routes table corrected, and a security section pointing to `SECURITY.md`. The
  not-yet-built Wiki was moved to a "Roadmap" section rather than being
  described as a live feature (it had no routes and would 404).
- **`INSTALL.md` rewritten** as a full install guide for Windows, macOS and
  Linux, covering both the double-click launcher and the terminal, plus
  connecting phones, running under `waitress` for a real session, updating
  safely, and a troubleshooting section. (The previous file was truncated
  mid-command.)
- Added **`docs/screenshots/`** with a guide to the expected screenshot
  filenames; the README references them.

### Fixed
- **Export/Import now carries the whole app state.** Two gaps are closed:
  - The **interactive-map background image** (in `static/maps`) is now included
    in the export bundle. Before, only handout uploads travelled, so an
    imported library pointed at a map image that never left the source machine
    and the map came up blank.
  - The **map state itself** (revealed hexes, POIs, marker, calibration, fog,
    background) is now actually applied on import. Before, `apply_import`
    merged only handouts, folders and wiki, silently ignoring the incoming
    map.
  The map is a single global scene, not a per-id collection, so import offers
  **one explicit choice** on the review page — keep your current map or replace
  it with the imported one — defaulting to *keep*, so an import can never wipe
  a map you are mid-session on. The choice appears only when the incoming map
  has content and differs from yours.

### Security
- **CSRF protection** on every state-changing request, via a per-session
  synchronizer token (stdlib `hmac` + `secrets`, no Flask-WTF). The token is
  emitted once in the shared `<head>` and delivered automatically: a script
  injects a hidden field into every POST form, and `fetch` is wrapped to add an
  `X-CSRF-Token` header to same-origin writes (the interactive map). See
  `handouts/security.py` and `SECURITY.md` §4.
- **Rate limiting** (in-memory token bucket, keyed by IP) to stop a request
  loop from exhausting the server. Tight policy on the DB-touching pollers
  (`/api/pop`, `/api/map/state`, `/api/map/reveal.png`), a loose ceiling
  elsewhere; over-limit gets HTTP 429 + `Retry-After`. See `SECURITY.md` §5.
- **Baseline hardening headers** on every response: `X-Content-Type-Options:
  nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy:
  strict-origin-when-cross-origin`.
- **Debugger off by default.** The Werkzeug interactive debugger (which allows
  arbitrary code execution) is now opt-in via `HANDOUTS_DEBUG=1`, never on by
  default. See `SECURITY.md` §6.3.
- **Guide information leak fixed.** The public `/guide` no longer shows the
  Master section (or a "Back to Dashboard" link) during first-run, when the
  master side is open to everyone. A new `auth.is_master_unlocked()` gates
  master-only *content* on a real passphrase unlock, distinct from the
  first-run fall-open that keeps the dashboard reachable. See `SECURITY.md`
  §3.5.
- Removed the temporary `/test-error/<code>` route.
- **`SECURITY.md`** added: an account of the threat model and the reasoning
  behind each control, with sources.

### Added
- **3D Inspect viewer (`object3d`).** A third handout viewer, alongside
  Carousel and Book, that opens the handout in a full-screen WebGL canvas the
  player can **rotate, zoom and pan** (Resident Evil / *Nobody Wants to Die*
  style object inspection). Two kinds of handout are supported:
  - a **`.glb` 3D model** (loaded with `GLTFLoader`), or
  - a **double-sided sheet** built procedurally from a front image and an
    optional **back texture**, where PNG transparency punches *real holes*
    through the paper (torn scrolls, bullet holes) rather than showing white.
  - **Interaction:** `OrbitControls` with `enableDamping` for fluid motion,
    ambient + two directional lights so both faces read when the sheet is spun.
  - **Performance / memory:** Three.js and the reader module are **lazy-loaded**
    — nothing 3D is downloaded until an `object3d` handout is actually opened.
    Closing the viewer runs a **total cleanup**: the `requestAnimationFrame`
    loop is stopped, the canvas removed from the DOM, and `.dispose()` is
    called on every geometry, material, texture, the controls and the renderer
    (which also loses its GL context), so opening and closing repeatedly never
    leaks. The init and destroy paths are kept separate in
    `static/vendor/three/inspector3d.js` (class `Inspector3D`).
  - **Self-hosted, offline-first:** Three.js r160 (build + `GLTFLoader` +
    `OrbitControls` + `BufferGeometryUtils`) is served from
    `static/vendor/three/`, resolved via an import map in the lightbox — no CDN.
    Run `python fetch_vendor.py` once to fetch it (same one-command setup the
    Book viewer's StPageFlip already uses).
  - **Storage:** handouts gain an optional `back_texture` (the sheet's reverse
    side), stored parallel to the Book viewer's `back_cover`; `.glb` files are
    recorded with `reader: 'model'` so the PDF-expansion and thumbnail passes
    skip them. Both the new field and format survive export/import.
  - **Master UI:** the upload and edit forms offer the new viewer, a back-texture
    upload (shown only for 3D Inspect), and accept `.glb`; the file card shows a
    `3D` badge for model handouts.
- **Three new themes**, each inspired by a D&D sourcebook:
  - *Vecna: Eve of Ruin* — necrotic grave-green and rotten violet.
  - *Tasha's Cauldron of Everything* — a simmering arcane brew: animated
    radial background, copper panel rim, violet-to-copper heading gradient,
    glowing buttons.
  - *Xanathar's Guide to Everything* — the watching beholder: a dilating
    magenta/green pupil, surveillance scanlines, iris panel rings, eye-ray
    button hovers.
  Themes can now carry an optional `extra_css` block (in `theming.py`) for
  per-theme textures and animations beyond colour/font tokens; it is emitted
  only while that theme is active, and all motion sits behind
  `prefers-reduced-motion`.
- **POP Handout.** The Master can now push a handout onto every player's
  screen, instead of publishing it and asking the table to refresh.
  - **POP** on any public handout (dashboard) broadcasts it immediately.
  - **Publish & POP** does both in one click for a hidden handout, and
    **Forge & POP** does the same straight from the upload form.
  - Players' screens open the handout in the existing lightbox, so carousel,
    book, PDFs and back covers all behave exactly as they do on a click. A
    player already reading something is not interrupted: they get a banner
    offering the new handout instead of having the viewer swapped underneath
    them.
  - **Sync:** the project had no client sync layer, so one was added. Players
    poll `GET /api/pop` every 3s; the endpoint returns a monotonic `seq` plus
    the handout to show. Polling was chosen over SSE/WebSockets because it
    holds no connections open (the app runs on the Werkzeug dev server) and
    recovers by itself from sleeping phones and Wi-Fi drops.
  - **Persistent by design:** the POP lives in `settings.pop` in the DB, not in
    memory, so a player who joins late, reloads, or wakes their phone still
    receives the POP the Master fired, and a server restart does not replay an
    old one. Only the newest POP is kept there is no queue, because a queue
    would make the table work through a backlog of reveals in the wrong order.
  - Popping is refused on hidden handouts (`400`): a route named "pop" must
    not be a back door to publishing. `/api/pop` re-checks `visible` on every
    read, so unpublishing or deleting a popped handout retires the broadcast
    and a stale pointer can never leak a handout the Master pulled back.
- **Master access control.** A single passphrase now separates the Master from
  the table, stored as a salted hash and carried in a signed session cookie.
  New `/unlock` prompt, `Lock master mode`, and a `Master Access` settings page.
  The signing key can be supplied via the `HANDOUTS_SECRET_KEY` environment
  variable; otherwise one is generated and persisted on first run.
  - Every `/dm-panel*`, `/export` and `/import` route is now enforced
    server-side. Previously they were reachable by anyone on the Wi-Fi.
  - On first run the app stays open (there is nothing to authenticate against
    yet) and the dashboard shows a warning banner until a passphrase is set.
- **Quick Wiki**, split into two collections:
  - **Players Wiki** (`/wiki`) read-only, lore the party has learnt.
  - **Master Wiki** (`/dm-panel/wiki/master`) secrets, guarded.
  - Pages carry a `scope`; the player routes only ever query the players'
    scope, so there is no request parameter that could reach master pages.
    Requesting a master page's id from the player side returns `404`, not
    `403`, so the existence of a secret page is not leaked.
  - One-click **Reveal to players** / **Hide from players** flips a page
    between the two wikis, for when the party learns something.
  - Pages are plain text (no markdown, no HTML), so a wiki body cannot inject
    script into a player's browser.
  - Wiki content is included in export/import bundles.
- **Master navigation menu** (hamburger drawer) on every master page, reusing
  the player hub's existing drawer machinery.

### Changed
- **Decluttered the Master's Screen.** The dashboard was holding the two
  handout lists, the upload form, folder management, the theme picker, the
  export/import panel and a language switcher at once. The occasional controls
  moved behind the new menu into pages of their own:
  - Theme + interface language → `/dm-panel/appearance`
  - Export / import → `/dm-panel/transfer`
  - Passphrase → `/dm-panel/security`
  The dashboard now carries only what is used constantly: search, the
  hidden/public lists, upload and folders.
- `POST /settings/theme` now redirects to `/dm-panel/appearance` (was
  `/dm-panel`), so the Master sees the new theme applied where they chose it.
- The player browse drawer gained a **Wiki** section linking to the Players
  Wiki.

### Fixed
- **Export bundles no longer carry credentials.** `export_bytes()` dumped the
  whole DB, and the new passphrase hash + session signing key live under
  `settings` so every `.zip` would have shipped them. A bundle is emailed or
  carried on a USB stick, so it is now treated as public: both are stripped
  (`transfer.PRIVATE_SETTINGS`). The signing key mattered most holding it
  lets anyone forge an `is_master` cookie without knowing the passphrase.
- **Import now carries wiki pages.** The merge only handled handouts and
  folders, so wiki pages would have been silently dropped on transfer. New
  pages are added with their scope intact (a master page stays secret); pages
  whose id already exists are left alone. The review screen lists incoming
  pages and which wiki each lands in, so importing someone else's secrets is
  never a surprise.
- `'Summary'` was about to be defined twice in the Italian catalogue, where the
  second definition would have silently overwritten the import-review page's
  translation. Since catalogue keys *are* the English source string, the wiki's
  field is named `'Page summary'` instead.
- Password, search, number and textarea inputs were not covered by the base
  input styling (which predates them) and rendered as unstyled native boxes.

## Earlier phases

### Theming
- Seven themes, each overriding the full token set (palette + display/body font
  pair + heading scale), inspired by official D&D campaigns.
- Only the active theme's fonts are fetched, and font families needing explicit
  axis tuples are spelled out the Google Fonts `css2` API fails the whole
  request if one family is under-specified, which silently killed both faces.

### Internationalisation
- English and Italian, per-user via a cookie (`?lang=` sets it). The `|t`
  filter takes the Jinja context so it is evaluated per render; without that,
  Jinja constant-folds it and bakes one language into the cached template.

### Handouts
- Multi-file handouts, per-file descriptions, drag-and-drop reordering.
- Carousel and Book (page-curl) viewers; optional back cover.
- PDF pages rendered to images for the Book viewer; first-page thumbnails for
  card previews, backfilled for older records.
- Folders (multi-membership), tags, categories, session numbers/titles,
  discovery place/date.
- Export/import of the whole library with a conflict review step.
