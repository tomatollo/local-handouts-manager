# The Storage Package

`handouts/storage/` is the persistence layer: everything that touches the JSON
database (`data/database.json`) or the uploads folders (`static/uploads`,
`static/maps`) lives here, so the route modules stay thin and free of storage
details. It used to be a single ~55 KB `storage.py`; it is now a package with
one module per responsibility. **Its public surface is unchanged** — every
consumer still writes `from handouts import storage` and calls
`storage.load_db()`, `storage.get_map_state(db)`, and so on. Only the internals
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
| `paths.py` | On-disk paths (`DB_PATH`, `UPLOAD_DIR`, `MAP_DIR`, `BASE_DIR`) and the small cross-cutting constants several modules share: `VIEW_TYPES`, `DEFAULT_VIEW_TYPE`, `ALLOWED_EXTENSIONS`, `MAP_EXTENSIONS`, `POP_KEY`, `MAP_KEY`, `POP_TTL_SECONDS`. No internal imports — the foundation everything else builds on. |
| `util.py` | Small pure helpers with no knowledge of the DB shape: `clean_view_type`, `allowed_file`, `reader_for`, `new_handout_id`, `now_iso`, `now_stamp`. |
| `formats.py` | Source-format labelling for the master's "Group by Format" view: `ext_of`, `normalize_format`, `format_of_handout`, `source_format_from_uploads`, `all_formats`. Carries `_PDF_PAGE_MARKER`, kept in sync with `pdfs.PDF_PAGE_MARKER`. |
| `records.py` | Handout-record helpers over the loaded DB: `find`, `player_payload`, `reveal_secret`, plus the aggregate/parse helpers `all_categories`, `all_tags`, `parse_tags`, `parse_passwords`, `parse_session_number`. |
| `folders.py` | Master-defined folders (`{id, name}`, multi-membership on handouts): `all_folders`, `find_folder`, `create_folder`, `rename_folder`, `delete_folder`, `valid_folder_ids`. |
| `settings.py` | Global, master-controlled theme: `get_theme`, `set_theme`. The only module that imports `theming`. |
| `welcome.py` | The player-hub welcome header (titles/subtitles/random): `get_welcome_config`, `set_welcome`, `pick_welcome`, and the shared `_normalize_welcome` cleaner. |
| `pop.py` | POP broadcasts — "put this handout on every screen, now": `pop_state`, `pop_age_seconds`, `pop_is_live`, `set_pop`, `clear_pop`. |
| `map_state.py` | The interactive map: confirmed state plus the `pending` draft layer, POIs, and focus broadcasts. Named `map_state` (not `map`) so it never shadows the builtin. Owns the map validation constants and cleaners (`_clean_pois`, `_coerce_map_fields`, ...). |
| `files.py` | Upload/file operations on disk: `save_files`, `remove_files`, `save_back_cover`, `allowed_map_file`, `save_map_image`, `remove_map_image`. The only module besides `db` that reaches the filesystem. |
| `db.py` | The heart: `load_db`, `save_db`, `_normalize`, the write lock, atomic writes, and the opt-in per-request cache (`set_request_cache_hooks`). |
| `__init__.py` | Re-exports the whole public API flat and declares `__all__`. |

---

## The dependency graph is acyclic

The modules form a layered, one-directional graph. `paths` and `util` sit at the
bottom and import nothing internal. The domain modules (`formats`, `records`,
`folders`, `settings`, `welcome`, `pop`, `map_state`, `files`) import only from
those foundations. `db` sits at the top and is the **only** module that imports
several domain modules — never the reverse.

```
paths, util                         (no internal imports)
      ^
formats, records, folders,          (import paths/util only)
settings, welcome, pop,
map_state, files
      ^
db                                  (imports paths, util, formats,
                                     welcome, map_state)
      ^
__init__                            (re-exports everything)
```

`db` imports the domain modules because `_normalize` — the migration pass that
brings a loaded DB up to the current shape — has to touch every concern
(welcome, POP, map POIs, handout view-type and format, secrets). Keeping each
concern's per-node cleaner in its own module and letting `db` call them means the
migration logic for a concern lives next to that concern, and the graph stays
acyclic because nothing the domain modules import ever reaches back into `db`.

---

## Two properties worth preserving

If you edit the package, keep these intact — they are load-bearing.

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

## The map staging model

`map_state.py` is the one module with non-obvious internal structure, so it is
worth spelling out. The interactive map has **two layers**:

- **Confirmed state** — the only thing players read. Their screens poll it.
- **`pending` (draft) state** — what the Master edits.

The Master reveals hexes, drags the marker, resizes the grid, or moves POIs into
the *draft*; none of it reaches players until an explicit **confirm**. This is so
a mistaken click never flashes onto the table mid-session.

- `update_map_state(db, data)` writes a subset of fields into `pending`.
- `confirm_map_state(db)` copies `pending` → confirmed and bumps `confirm_seq`
  (players compare it to tell a real change from an unchanged poll). This is the
  only function that changes what players read, aside from `set_map_image`.
- `discard_map_state(db)` throws the draft away, resetting `pending` back to the
  confirmed state.

Two things are deliberately **not** staged, because they are live directives
rather than draft edits — the same design as a POP:

- `set_map_image(db, filename)` writes the background to *both* layers at once. An
  uploaded map is setup, not a reveal; a half-set-up map where the Master sees the
  new image but players still see the old one would only confuse.
- `set_map_focus(db, x, y, scale)` records a "everyone look here, now" broadcast
  that takes effect immediately, bumping its own `seq`.

All map coordinates (POIs, calibration offsets, hex size, focus point) are stored
as **percent of the image**, so they survive a change of map resolution.

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

**A note on `__pycache__`.** When a module becomes a package, an old
`__pycache__/storage.cpython-*.pyc` can linger. Python gives the package
precedence, so it's harmless, but removing the stale `.pyc` keeps things tidy.
