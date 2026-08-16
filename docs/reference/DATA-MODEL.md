# Data Model

Everything the app persists lives in one JSON file, `data/database.json`. This
document describes its shape object by object: what each record is, which fields
it carries, and what they mean. It is a reference, not a guide — for *how* the
storage package is organised (modules, the load/save cycle, migrations) see
[STORAGE.md](STORAGE.md).

The file is plain JSON with no schema enforcement; the shapes below are what the
code writes and what `storage._normalize()` guarantees on load. Legacy records
are brought up to the current shape on every load, so you may see extra or
missing keys in an old file that the app fills in automatically.

## Top level

The root object has these keys:

```json
{
  "handouts": [ ... ],
  "folders":  [ ... ],
  "maps":     [ ... ],
  "settings": { ... }
}
```

- `handouts` — the library, a list of handout objects (see below).
- `folders` — master-defined collections, a list of `{id, name}`.
- `maps` — the interactive maps, a list of map objects.
- `settings` — table-wide settings: the theme, the welcome header, the current
  POP broadcast, and the (opaque) master credentials.

A freshly created database starts as `{"handouts": [], "folders": []}`; the
other keys are added on first normalize.

---

## Handout

A single piece of shared material — one or more image/PDF pages, or a 3D model —
plus its metadata and the flags that control how and when players see it.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable unique id (hex), minted at upload. Used in every URL and API payload. |
| `title` | string | The handout's name. Required at upload. |
| `description` | string | Free-text blurb shown in the viewer's info panel. |
| `files` | list | The pages, in display order. Each is `{filename, reader, description, thumb}` (see below). |
| `visible` | bool | `false` = a hidden draft; `true` = published to the players' hub. Every handout starts hidden. |
| `category` | string | A single free-text category label. |
| `tags` | list of strings | Multi-value tags, searchable and groupable, separate from `category` and folders. |
| `folders` | list of strings | Folder ids this handout belongs to (multi-membership). |
| `view_type` | string | How players open it: `carousel`, `book`, or `object3d`. Defaults to `carousel`. |
| `hard_covers` | bool | Book viewer only: whether the cover and back cover are rigid boards (`true`) or flip like inner leaves. Default `true`. |
| `source_format` | string | The ORIGINAL upload format (`pdf`, `png`, …), recorded before PDF pages are rendered to images. Drives the master's "Group by Format" view only. |
| `back_cover` | file entry or null | Book viewer only: a single page shown as the very last leaf. Ignored by other viewers. |
| `back_texture` | file entry or null | `object3d` sheet viewer only: the image painted on the reverse face; PNG transparency shows through as holes. |
| `secret_passwords` | list of strings | Words that, typed into the viewer, reveal `secret_handout_id`. Empty = no secret. Plain text by design — this is table theatre, not security. |
| `secret_ignore_case` | bool | Match `secret_passwords` without regard to letter case. |
| `secret_handout_id` | string or null | The handout unlocked when a secret password is entered. |
| `secret_password` | string | Legacy mirror of the first entry in `secret_passwords`, kept so older readers and export/import still work. Not the source of truth. |
| `session_number` | int or null | Optional session number for the "Group by Session" view. |
| `session_title` | string | Optional session title. |
| `found_location` | string | Optional in-fiction discovery place. |
| `found_date` | string | Optional in-fiction discovery date. |
| `created_at` | string | ISO-8601 UTC timestamp set at upload. |

### File entry

Each item in `files` (and each `back_cover` / `back_texture`) is:

| Field | Type | Meaning |
| --- | --- | --- |
| `filename` | string | The stored file's name under `static/uploads/`. |
| `reader` | string | How the client reads this file: `image`, `pdf`, or `model` (a `.glb`). Set from the extension at upload. |
| `description` | string | Optional per-file caption. |
| `thumb` | string or null | A rendered first-page thumbnail (PDFs only); `null` when none. |

> A PDF is rendered to one image per page at upload, so a stored PDF handout's
> `files` are usually image pages even though `source_format` stays `pdf`. A
> `.glb` model keeps `reader: "model"` and is left untouched by the PDF and
> thumbnail passes.

---

## Folder

A master-defined collection. Handouts reference folders by id; a folder never
lists its members (membership lives on the handout's `folders` field).

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable unique id (hex). |
| `name` | string | The display label. Names are unique case-insensitively. |

Deleting a folder detaches it from every handout but never deletes the handouts
themselves.

---

## Map

One interactive scene the Master reveals and the players poll. A table can hold
several. Each map carries its full **confirmed** state (what players read), a
**`pending`** draft layer (what the Master is editing), and a `confirm_seq`
counter. Coordinates are stored as **percent of the image** so they survive a
change of map resolution.

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable id used in URLs and API calls. (The migrated legacy map is `legacy-map`.) |
| `name` | string | The Master's label, shown in the chooser. |
| `revealed_hexes` | list of strings | Ids of revealed cells (`hex-<col>-<row>`), the only cells players see. |
| `marker_x`, `marker_y` | float | Party marker position (percent). |
| `marker_visible` | bool | Whether the marker is shown. |
| `marker_scale` | float | Marker size multiplier (0.3–4.0). |
| `marker_icon` | string | Optional custom glyph for the marker. |
| `marker_color` | string | Marker colour (`#rrggbb`). |
| `grid_cols`, `grid_rows` | int | Grid dimensions (1–400). |
| `grid_type` | string | `hex` (default) or `square`. |
| `fog_color` | string | The unrevealed-terrain colour (`#rrggbb`). |
| `map_image` | string or null | Background image filename under `static/maps/`, or `null` for none (shows the fog placeholder). |
| `offset_x`, `offset_y` | float | Grid calibration origin (percent; may be slightly negative). |
| `hex_size` | float | Cell size (percent of image width). Reused as the square side in square mode. |
| `pois` | list | Points of interest (see below). |
| `focus` | object | The current "everyone look here" broadcast (see below). |
| `pending` | object | The draft layer: the same scene fields, edited privately until confirmed. |
| `confirm_seq` | int | Bumped on every confirm so players can tell a real change from an unchanged poll. |

### Point of interest (POI)

Each item in a map's `pois`:

| Field | Type | Meaning |
| --- | --- | --- |
| `id` | string | Stable id (hex). |
| `label` | string | Pin label (may be blank; up to 80 chars). |
| `x`, `y` | float | Position (percent, 0–100). |
| `always_visible` | bool | Whether the pin shows before its hex is revealed. |
| `icon` | string | Custom glyph, or empty for the default pin. |
| `color` | string | Icon colour (`#rrggbb`). |
| `scale` | float | Size multiplier (0.3–4.0). |
| `category` | string | Optional free-text group (e.g. "Cities"). |
| `icon_bg` | bool | Whether to draw a filled plate behind the icon. |
| `icon_bg_color` | string | The plate colour (`#rrggbb`). |

### Focus

A map's `focus` is a live camera broadcast, not a staged edit:

| Field | Type | Meaning |
| --- | --- | --- |
| `seq` | int | Monotonic counter; players animate to the point on any value above the last they acted on. |
| `x`, `y` | float | Focus centre (percent, 0–100). |
| `scale` | float | Zoom level. |

---

## Settings

Table-wide, master-controlled state under the root `settings` key.

| Field | Type | Meaning |
| --- | --- | --- |
| `theme` | string | The active theme id (see [THEMES.md](../dev/THEMES.md)). Global — every player sees it. |
| `welcome` | object | The player-hub welcome header: title(s), subtitle(s), and a `random` flag. Empty values mean "use the app default". |
| `pop` | object | The current POP broadcast (see below). |

`settings` also holds the master **passphrase hash** and the **session signing
key** (written by `auth.py`). These are opaque to display code, and both are
stripped from export bundles so a shared `.zip` never carries credentials. The
per-user interface language is deliberately NOT stored here — it is a cookie, so
each person can pick their own.

### POP

The `settings.pop` object records the current "put this on every screen" broadcast:

| Field | Type | Meaning |
| --- | --- | --- |
| `seq` | int | Monotonic counter; a device shows any POP whose seq is higher than the last it displayed. |
| `handout_id` | string or null | The handout to open. |
| `at` | string or null | When it was fired (used to expire it after a couple of minutes). |

Only the newest POP is kept — there is no queue. The player endpoint re-checks
the handout is still visible on every read, so a POP can never leak a handout
the Master has pulled back.

---

## Where this maps to code

The shapes above are defined and defended in the storage package: `db._normalize`
(handout + settings fields), `map_state._blank_map_state` / `_normalize_map`
(map + POI + focus), and `folders` (`{id, name}`). See [STORAGE.md](STORAGE.md)
for the module layout and the reasoning behind the draft/confirm staging model.
