# The Storage Package

`handouts/storage/` is the persistence layer: everything that touches the JSON
database (`data/database.json`) or the uploads folders (`static/uploads`,
`static/maps`) lives here, so the route modules stay thin and free of storage
details. It used to be a single ~55 KB `storage.py`; it is now a package with
one module per responsibility. **Its public surface is unchanged** every
consumer still writes `from handouts import storage` and calls
`storage.load_db()`, `storage.get_map(db, map_id)`, and so on. Only the internals
moved.

The key point to understand first: **splitting the file changed no behaviour and
no call site.** The package `__init__.py` re-exports the entire public API flat,
so `storage.xxx()` resolves exactly as it did when `storage` was one module. If
you are just *using* storage, you never need to know which submodule a function
lives in.

---

## Why a package

The old `storage.py` had grown into a "god module": JSON database access, upload
handling, PDF-origin format labelling, folders, tags, the interactive map, POP
broadcasts, the welcome header, and theme settings were all mixed together. That
made it hard to find anything and hard to change one concern without reading past
the other nine.

The split follows the same pattern already used for `theming/` and `i18n/`: turn
the file into a package, give each responsibility its own module, and have
`__init__.py` re-export the public names so the rest of the app is untouched.

---

## Module map

Each module owns one concern. The list is ordered from the lowest layer (no
internal dependencies) upward.

| Module | Responsibility |
| --- | --- |
| `paths.py` | On-disk paths (`DB_PATH`, `UPLOAD_DIR`, `MAP_DIR`, `BASE_DIR`) and the small cross-cutting constants several modules share: `VIEW_TYPES`, `DEFAULT_VIEW_TYPE`, `ALLOWED_EXTENSIONS`, `MAP_EXTENSIONS`, `POP_KEY`, `MAP_KEY` (legacy single-map key, read once by the migration), `MAPS_KEY` (current list-of-maps key), `MAP_NAME_MAX`, `POP_TTL_SECONDS`. No internal imports the foundation everything else builds on. |
| `util.py` | Small pure helpers with no knowledge of the DB shape: `clean_view_type`, `allowed_file`, `reader_for`, `new_handout_id`, `now_iso`, `now_stamp`. |
| `formats.py` | Source-format labelling for the master's "Group by Format" view: `ext_of`, `normalize_format`, `format_of_handout`, `source_format_from_uploads`, `all_formats`. Carries `_PDF_PAGE_MARKER`, kept in sync with `pdfs.PDF_PAGE_MARKER`. |
| `records.py` | Handout-record helpers over the loaded DB: `find`, `player_payload`, `reveal_secret`, plus the aggregate/parse helpers `all_categories`, `all_tags`, `parse_tags`, `parse_passwords`, `parse_session_number`. |
| `folders.py` | Master-defined folders (`{id, name}`, multi-membership on handouts): `all_folders`, `find_folder`, `create_folder`, `rename_folder`, `delete_folder`, `valid_folder_ids`. |
| `settings.py` | Global, master-controlled theme: `get_theme`, `set_theme`. The only module that imports `theming`. |
| `materials.py` | Object3d **built-sheet** material presets (roughness/metalness/thickness): `SHEET_MATERIAL_PRESETS`, `DEFAULT_SHEET_MATERIAL_PRESET`, `default_sheet_material`, `clean_sheet_material`, `sheet_material_from_form`. A foundation module  no internal imports so `db._normalize` and `records` can pull it in without a cycle. See [the materials module](#the-materials-module). |
| `welcome.py` | The player-hub welcome header (titles/subtitles/random): `get_welcome_config`, `set_welcome`, `pick_welcome`, and the shared `_normalize_welcome` cleaner. |
| `pop.py` | POP broadcasts "put this handout on every screen, now": `pop_state`, `pop_age_seconds`, `pop_is_live`, `set_pop`, `clear_pop`. |
| `map_state.py` | The interactive **maps**: a list of maps, each with confirmed state plus a `pending` draft layer, POIs, and focus broadcasts. Owns the map collection CRUD (`all_maps`, `find_map`, `get_map`, `create_map`, `rename_map`, `delete_map`), the per-map scene operations (all taking a `map_id`), the validation constants and cleaners (`_clean_pois`, `_coerce_map_fields`, `_normalize_map`, ...). Named `map_state` (not `map`) so it never shadows the builtin. |
| `files.py` | Upload/file operations on disk: `save_files`, `remove_files`, `save_back_cover`, `allowed_map_file`, `save_map_image`, `remove_map_image`. The only module besides `db` that reaches the filesystem. |
| `db.py` | The heart: `load_db`, `save_db`, `_normalize`, `is_current_schema`, the write lock, atomic writes, the schema-version stamp (`_SCHEMA_VERSION`), and the opt-in per-request cache (`set_request_cache_hooks`). |
| `__init__.py` | Re-exports the whole public API flat and declares `__all__`. |

---

## The dependency graph is acyclic

The modules form a layered, one-directional graph. `paths` and `util` sit at the
bottom and import nothing internal. `materials` also imports nothing internal, so
it sits on that same foundation layer. The domain modules (`formats`, `records`,
`folders`, `settings`, `welcome`, `pop`, `map_state`, `files`) import only from
those foundations `records` pulls in `materials` to clean a handout's
`sheet_material` for the player payload. `db` sits at the top and is the **only**
module that imports several domain modules never the reverse.

```
paths, util, materials              (no internal imports)
      ^
formats, records, folders,          (import paths/util/materials only;
settings, welcome, pop,              records imports materials)
map_state, files
      ^
db                                  (imports paths, util, formats,
                                     materials, welcome, map_state)
      ^
__init__                            (re-exports everything)
```

`db` imports the domain modules because `_normalize` the migration pass that
brings a loaded DB up to the current shape has to touch every concern
(welcome, POP, map POIs, handout view-type, format, sheet material, secrets).
Keeping each concern's per-node cleaner in its own module and letting `db` call
them means the migration logic for a concern lives next to that concern, and the
graph stays acyclic because nothing the domain modules import ever reaches back
into `db`.

---

## Two properties worth preserving

If you edit the package, keep these intact they are load-bearing.

### 1. `db` has no Flask import

`storage` must stay usable from the command line (`transfer_cli.py`, one-off
scripts, tests), where there is no Flask request context. So `db.py` imports no
Flask. The per-request DB cache is instead **injected** by the web layer: `app.py`
calls `storage.set_request_cache_hooks(getter, setter)` at startup, handing
`storage` two callables backed by `flask.g`. Inside a request, the many callers
that each `load_db()` (the language/CSRF/rate-limit hooks, the UI context
processor, and the view itself) share one read + normalize instead of re-parsing
the file every time.

Outside a request context the hooks are simply never installed: `_cache_get`
returns `None`, every `load_db()` reads from disk exactly as before, and nothing
depends on Flask being importable. If you add caching or state to `db`, route it
through the same injected-hook pattern rather than importing Flask.

### 2. `_normalize` is public despite the underscore

`transfer.py` calls `storage._normalize(incoming)` on a freshly imported DB
before saving it, so `_normalize` is part of the real public surface even though
its name is underscored. It is re-exported from `__init__.py` for that reason.
Don't "clean it up" out of the exports.

---

## The schema stamp and the migration fast-path

`_normalize` does two very different kinds of work on a loaded DB: a handful of
cheap **DB-level** defaults (folders list, settings, theme, welcome, POP) and a
far heavier pass that walks **every handout** (and every map) filling in legacy
fields. The heavy pass is pure migration on a database already current it
finds nothing to change, yet it still costs a full walk of the library, and it
ran on *every* request, because `load_db` calls `_normalize` each time it reads
from disk and several callers read per request.

To cut that steady cost, `db.py` carries an integer `_SCHEMA_VERSION` and stamps
it into the DB as `_schema`. The flow:

- `_normalize` always runs the cheap DB-level defaults (so a fresh or
  hand-edited DB is always safe), then, **if** `data['_schema']` already equals
  `_SCHEMA_VERSION`, returns early and skips the per-handout + per-map loop.
  Otherwise it runs the full migration as before.
- `_normalize` never writes the stamp. Only `save_db` does, setting
  `data['_schema'] = _SCHEMA_VERSION` just before it writes so the stamp
  appears only once the migrated shape actually reaches disk. Until a save
  happens, every load keeps doing the full pass, which is correct: an
  un-persisted migration must not be assumed complete.
- `is_current_schema(db)` exposes the same check to callers that want to skip
  their *own* one-time work on an already-migrated DB. The player hub (`home`)
  uses it to skip the legacy PDF-page and thumbnail backfills (`pdfs.backfill_*`),
  which are the same kind of once-only, whole-library migration and previously
  walked the library on every hub load.

**The stamp is a local optimisation only, never portable state.** An export
bundle carries no `_schema` (stripped in `transfer._public_db`), and an imported
bundle is always fully re-normalized regardless of any stamp it might contain
(`transfer._read_bundle` pops `_schema` before calling `_normalize`), because a
bundle is external data of unknown vintage whose stamp cannot be trusted. The
merge's own `save_db` then re-stamps the merged DB.

**If you add or change a migration step** inside the per-handout loop (or
`_normalize_map`), you MUST bump `_SCHEMA_VERSION` by one otherwise a DB
stamped at the old version takes the fast path and never receives your new
migration. Bumping it makes every older DB fail the equality check once, run the
full pass, and get re-stamped on the next save. This is called out again in
*How to extend* below.

---

## The maps model

`map_state.py` is the one module with non-obvious internal structure, so it is
worth spelling out.

### A list of maps

The table can have **several maps** a world map, a city, a dungeon level. They
live in a list at the DB root under `MAPS_KEY` (`'maps'`); each map is a dict
with a stable `id`, a display `name`, and the full scene state. The collection
is managed with:

- `all_maps(db)` every map, in stored order (the chooser list).
- `find_map(db, map_id)` / `get_map(db, map_id)` look one up. `get_map`
  returns it **normalized**, or `None` if the id doesn't exist. There is no
  implicit creation: a missing id is a real "not found" (a deleted map, a stale
  URL), which the routes turn into a 404 rather than silently spawning a blank
  map.
- `create_map(db, name)` / `rename_map(db, map_id, name)` /
  `delete_map(db, map_id)`. `delete_map` only touches the DB; the caller removes
  the map's background image file (the master route does this via
  `storage.remove_map_image`).

### Migration from the legacy single map

Databases written before multi-map support stored **one** map under the legacy
`MAP_KEY` (`'map_state'`). `db._normalize` migrates that into `maps[0]` exactly
once and drops the old key a clean, one-way migration (backups are the safety
net, via export/import). The migrated map is given a stable id (`'legacy-map'`)
and a default name so it stays addressable across requests **before** the first
save: without a fixed id, `_normalize_map` would mint a fresh random id on every
`load_db`, and because the migration isn't persisted until a save, each request
would see a different id an endless redirect between the map list and a map
that no longer matches its id. Visiting the master map list saves once, making
the migrated shape (and its id) permanent.

### The staging (draft) model per map

Each map has **two layers**:

- **Confirmed state** the only thing players read. Their screens poll it.
- **`pending` (draft) state** what the Master edits.

The Master reveals hexes, drags the marker, resizes the grid, or moves POIs into
that map's *draft*; none of it reaches players until an explicit **confirm**. So
a mistaken click never flashes onto the table mid-session. Every per-map
operation takes a `map_id` and is a no-op returning `None` when the id doesn't
resolve, so a stale id from a slow client can't raise:

- `update_map_state(db, map_id, data)` writes a subset of fields into that map's
  `pending`.
- `confirm_map_state(db, map_id)` copies `pending` → confirmed and bumps that
  map's `confirm_seq` (players compare it to tell a real change from an
  unchanged poll). This is the only function that changes what players read,
  aside from `set_map_image`.
- `discard_map_state(db, map_id)` throws that map's draft away, resetting
  `pending` back to its confirmed state.

Two things are deliberately **not** staged, because they are live directives
rather than draft edits the same design as a POP:

- `set_map_image(db, map_id, filename)` writes the background to *both* layers at
  once. An uploaded map is setup, not a reveal; a half-set-up map where the
  Master sees the new image but players still see the old one would only confuse.
- `set_map_focus(db, map_id, x, y, scale)` records a "everyone look here, now"
  broadcast on that map that takes effect immediately, bumping its own `seq`.

All map coordinates (POIs, calibration offsets, hex size, focus point) are stored
as **percent of the image**, so they survive a change of map resolution.

Each map also carries a `grid_type` (`'hex'`, the default, or `'square'`). It is
a staged field like the rest, so the Master picks the shape in the draft and it
reaches players on confirm. The client's `buildGrid()` and the server-side
compositor (`mapmask`) both branch on it and MUST stay in step: squares reuse
`hex_size` as the cell side (percent of image width) and the same
`offset_x`/`offset_y` origin, laid out edge-to-edge with no stagger; hexes keep
the flat-top interlocking layout. Cells are identified the same way in both
modes (`hex-<col>-<row>`), so switching a map's grid type re-shapes the overlay
without invalidating already-revealed cells.

`_normalize_map(m)` is the per-map cleaner `db._normalize` calls for every map in
the list (and for the migrated legacy map): it ensures the id + name, fills any
missing scene field, de-duplicates revealed hexes, re-cleans POIs, and seeds the
`pending`/`confirm_seq`. It is idempotent, so re-running it is always safe on
an already-current DB the schema fast-path skips it, but correctness never
depends on that (running it again changes nothing).

---

## The materials module

`materials.py` owns the object3d **built-sheet** material the small
`{preset, roughness, metalness, thickness}` dict that says how a procedurally-
built sheet (a scroll, a torn note, a plate) looks and how thick it is. A `.glb`
model ignores it (it brings its own materials); the carousel/book viewers never
look at it. For the stored shape and the field meanings see
[DATA-MODEL.md](DATA-MODEL.md#sheet-material); for how the 3D reader turns the
four numbers into geometry see
[3D-VIEWER.md](3D-VIEWER.md#the-built-sheet-and-its-real-depth).

It is a **foundation** module: it imports no sibling, so both `db._normalize`
(which sets `sheet_material` on every handout) and `records.player_payload`
(which cleans it into the POP/reveal payload) can depend on it without a cycle.

The public surface:

- `SHEET_MATERIAL_PRESETS` the named looks offered in the create/edit form
  (`paper`, `parchment`, `leather`, `wood`, `stone`, `metal`), each with its
  `label` + `roughness`/`metalness`/`thickness`. The dict order is the UI order.
- `DEFAULT_SHEET_MATERIAL_PRESET` (`'parchment'`) and `default_sheet_material()`
  the default a fresh handout gets and every legacy record is normalized to. It
  matches the reader's old hardcoded 0.85 / 0.0 look, so existing sheets are
  unchanged. `default_sheet_material()` returns a **fresh dict** each call, so
  storing it on a record never aliases a shared object.
- `clean_sheet_material(raw)` the cleaner. Coerces junk to the default, clamps
  `roughness`/`metalness` to 0–1 and `thickness` to 0.005–0.5, and applies the
  key rule: **explicit slider values win over a named preset, and the recorded
  `preset` becomes `'custom'` only when the numbers actually diverge from every
  preset.** That is what lets the form send a preset choice *and* advanced
  overrides in one POST "Metal, but rougher" resolves to a custom material
  seeded from metal. This is the same defensive cleaner `db._normalize` and
  `player_payload` both call, so a hand-edited record or a stale POST can never
  store out-of-range numbers.
- `sheet_material_from_form(preset, roughness, metalness, thickness)` packs the
  four raw form fields into the dict shape and runs it through
  `clean_sheet_material`. Used by the upload + edit routes.

Mirroring the two-place clamping noted in [3D-VIEWER.md](3D-VIEWER.md): the server
cleans here (defending the stored record and every payload), and the browser
reader clamps again (defending against a partial material it might be handed
directly). Both are deliberate keep them.

---

## How to extend

**Add a function to an existing concern.** Put it in the matching module, then
add its name to that module's block in `__init__.py` and to `__all__`. That's the
only wiring needed for `storage.your_function()` to work everywhere.

**Add a new concern.** Create `handouts/storage/<concern>.py`, importing only
from `paths`/`util` (and other foundations) to keep the graph acyclic. Re-export
its public names in `__init__.py` and list them in `__all__`. If the concern
introduces a new field that legacy databases won't have, add its migration to
`_normalize` in `db.py` (calling a cleaner defined in your module, mirroring how
`welcome`/`map_state` do it) so old records are brought up to shape on load.
**If that migration lives in the per-handout loop or in `_normalize_map`** (the
heavy pass gated by the schema fast-path), bump `_SCHEMA_VERSION` so every
already-stamped DB runs it once more see
[The schema stamp and the migration fast-path](#the-schema-stamp-and-the-migration-fast-path).
A new DB-level default placed *above* the fast-path early-return needs no bump,
since it always runs.

**A note on `__pycache__`.** When a module becomes a package, an old
`__pycache__/storage.cpython-*.pyc` can linger. Python gives the package
precedence, so it's harmless, but removing the stale `.pyc` keeps things tidy.
