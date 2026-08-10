"""Interactive maps (global, master-controlled).

The table can have SEVERAL maps -- a world map, a city, a dungeon level --
each an independent scene the Master reveals hexes on and moves a marker
across, and each polled by the player screens. The maps live in a LIST at the
DB root under MAPS_KEY (see paths.py); every map is a dict with:

  * `id`   -- stable identifier used in URLs and API calls
  * `name` -- the Master's label for it (shown in the map list / chooser)
  * the full scene state: revealed hexes, marker, grid, fog, background image,
    calibration, POIs, focus, and a `pending` draft layer + `confirm_seq`.

Databases written before multi-map support stored a SINGLE map under the
legacy MAP_KEY; db._normalize migrates that into `maps[0]` once and drops the
old key (see there). This module never reads MAP_KEY itself.

Named map_state (historically) so it never shadows the builtin `map`. The
confirmed state is what players read; the Master edits a map's `pending` draft
and explicitly confirms it. See docs/STORAGE.md for the staging model.
"""

import re
import uuid

from .paths import MAPS_KEY, MAP_NAME_MAX


def _blank_map_state():
    """A fresh map's confirmed-state fields (no id/name -- the caller adds those).

    The single source of truth for a map's default shape, used when creating a
    new map, defaulting a lookup, and (via _normalize_map) migrating the legacy
    single map. `pending` and `confirm_seq` are seeded by _normalize_map so the
    draft starts equal to the confirmed state.
    """
    return {
        'revealed_hexes': [],
        'marker_x': 0,
        'marker_y': 0,
        'marker_visible': False,
        'marker_scale': 1.0,
        'marker_icon': '',
        'marker_color': '#c0533b',
        'grid_cols': 20,
        'grid_rows': 15,
        'grid_type': 'hex',
        'fog_color': '#0d0b0a',
        'map_image': None,
        'offset_x': 0.0,
        'offset_y': 0.0,
        'hex_size': 5.0,
        'pois': [],
        'focus': {'seq': 0, 'x': 50.0, 'y': 50.0, 'scale': 1.0},
    }


# Bounds for the grid dimensions the Master can set. A hard ceiling stops a
# typo (2300 instead of 23) from asking the browser to draw millions of hexes.
GRID_MIN = 1
GRID_MAX = 400


def _clean_hex_color(raw, fallback):
    """Return a #rrggbb / #rgb string, or `fallback` for anything else.

    Guards the fog colour: it is written straight into CSS on both the master
    and player pages, so only a real hex colour is allowed through -- never an
    arbitrary string that could carry other CSS.
    """
    raw = (raw or '').strip()
    if len(raw) in (4, 7) and raw[0] == '#' and \
            all(c in '0123456789abcdefABCDEF' for c in raw[1:]):
        return raw
    return fallback

# Caps for POIs. A generous ceiling on count stops a runaway client from
# stuffing the draft, and a label cap keeps one pin from carrying an essay
# (the label is rendered as plain text, so length is the only concern).
POI_MAX = 200
POI_LABEL_MAX = 80
# The icon is a single glyph the Master picks (a letter, an emoji, a symbol).
# We cap it short so it stays a marker, not a text field. Emoji can be multiple
# code points (e.g. flags, ZWJ sequences), so the cap is generous but bounded.
POI_ICON_MAX = 8
# POI/marker scale multipliers, clamped so a bad value can't make a pin fill
# the screen or vanish.
SCALE_MIN = 0.3
SCALE_MAX = 4.0
# A hex colour like #rrggbb or #rgb; anything else falls back to the default.
_HEX_COLOR_RE = re.compile(r'^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$')
POI_DEFAULT_COLOR = '#e8a83a'


def _clean_scale(value, default=1.0):
    """Clamp a scale multiplier to SCALE_MIN..SCALE_MAX, or return default."""
    try:
        return max(SCALE_MIN, min(SCALE_MAX, float(value)))
    except (TypeError, ValueError):
        return default


def _clean_color(value, default=POI_DEFAULT_COLOR):
    """Return value if it is a #rgb/#rrggbb hex colour, else the default."""
    if isinstance(value, str) and _HEX_COLOR_RE.match(value.strip()):
        return value.strip().lower()
    return default


def _clean_pois(raw, previous):
    """Return a validated list of POI dicts, or `previous` if `raw` is junk.

    Each POI is normalised to
    {id, label, x, y, always_visible, icon, color, scale}. x/y are clamped to
    0..100 (percent of the image). A POI with no usable id gets a fresh one; a
    blank label is allowed (the Master may pin first, name later). Anything that
    isn't a list leaves the previous value untouched, so a partial patch that
    omits `pois` never wipes them.
    """
    if not isinstance(raw, (list, tuple)):
        return previous
    cleaned = []
    seen_ids = set()
    for item in raw[:POI_MAX]:
        if not isinstance(item, dict):
            continue
        pid = str(item.get('id') or '').strip()
        if not pid or pid in seen_ids:
            pid = uuid.uuid4().hex
        seen_ids.add(pid)
        label = str(item.get('label') or '').strip()[:POI_LABEL_MAX]
        try:
            x = max(0.0, min(100.0, float(item.get('x', 0))))
        except (TypeError, ValueError):
            x = 0.0
        try:
            y = max(0.0, min(100.0, float(item.get('y', 0))))
        except (TypeError, ValueError):
            y = 0.0
        # icon: a short custom glyph. Empty string means "use the default pin".
        icon = str(item.get('icon') or '').strip()[:POI_ICON_MAX]
        # category: a free-text group the Master assigns (e.g. "Cities",
        # "Ruins"). Empty = uncategorised. Capped so it stays a tag, not prose.
        category = str(item.get('category') or '').strip()[:POI_LABEL_MAX]
        cleaned.append({
            'id': pid,
            'label': label,
            'x': x,
            'y': y,
            'always_visible': bool(item.get('always_visible', True)),
            'icon': icon,
            'color': _clean_color(item.get('color')),
            'scale': _clean_scale(item.get('scale')),
            'category': category,
            # Optional filled background behind the icon/pin, with its own
            # colour independent of the icon colour. icon_bg False = no plate.
            'icon_bg': bool(item.get('icon_bg', False)),
            'icon_bg_color': _clean_color(item.get('icon_bg_color'), '#241d18'),
        })
    return cleaned


def _coerce_map_fields(target, data):
    """Write the known map fields from `data` into `target` dict, in place.

    Shared by the draft writer and the map-upload route so validation lives in
    one spot. Unknown keys are ignored; bad types leave the previous value.
    `target` is either a map's confirmed state or its `pending` sub-dict.
    """
    if 'revealed_hexes' in data:
        hexes = data['revealed_hexes']
        if isinstance(hexes, (list, tuple)):
            seen = set()
            cleaned = []
            for hx in hexes:
                key = str(hx)
                if key not in seen:
                    seen.add(key)
                    cleaned.append(key)
            target['revealed_hexes'] = cleaned

    for axis in ('marker_x', 'marker_y'):
        if axis in data:
            try:
                target[axis] = float(data[axis])
            except (TypeError, ValueError):
                pass

    if 'marker_visible' in data:
        target['marker_visible'] = bool(data['marker_visible'])

    if 'marker_scale' in data:
        target['marker_scale'] = _clean_scale(data['marker_scale'])

    if 'marker_icon' in data:
        target['marker_icon'] = str(data['marker_icon'] or '').strip()[:POI_ICON_MAX]

    if 'marker_color' in data:
        target['marker_color'] = _clean_color(data['marker_color'], '#c0533b')

    for key in ('grid_cols', 'grid_rows'):
        if key in data:
            try:
                n = int(data[key])
                target[key] = max(GRID_MIN, min(GRID_MAX, n))
            except (TypeError, ValueError):
                pass

    # Grid shape: 'hex' (default) or 'square'. Anything unrecognised leaves the
    # previous value, so a malformed patch can't blank it. Both the client's
    # buildGrid() and the server-side compositor (mapmask) branch on this, so
    # the two must offer exactly the same set of values.
    if 'grid_type' in data:
        val = str(data['grid_type'] or '').strip().lower()
        if val in ('hex', 'square'):
            target['grid_type'] = val

    # Calibration floats (percent). offset can be slightly negative so the grid
    # can start just off the top-left corner; hex_size has a sane floor so a
    # zero never collapses every hex to a point.
    for key in ('offset_x', 'offset_y'):
        if key in data:
            try:
                target[key] = max(-50.0, min(150.0, float(data[key])))
            except (TypeError, ValueError):
                pass
    if 'hex_size' in data:
        try:
            target['hex_size'] = max(0.5, min(100.0, float(data['hex_size'])))
        except (TypeError, ValueError):
            pass

    if 'fog_color' in data:
        target['fog_color'] = _clean_hex_color(
            data['fog_color'], target.get('fog_color', '#0d0b0a'))

    if 'map_image' in data:
        val = data['map_image']
        if val is None:
            target['map_image'] = None
        elif isinstance(val, str) and '/' not in val and '\\' not in val:
            target['map_image'] = val

    if 'pois' in data:
        target['pois'] = _clean_pois(data['pois'], target.get('pois', []))


# The scene fields a confirm promotes from pending -> confirmed, and that a
# discard copies confirmed -> pending. `map_image` is included because a map
# without its image staged consistently would confirm to a blank background.
_STAGED_KEYS = (
    'revealed_hexes', 'marker_x', 'marker_y', 'marker_visible',
    'marker_scale', 'marker_icon', 'marker_color',
    'grid_cols', 'grid_rows', 'grid_type', 'fog_color',
    'map_image', 'offset_x', 'offset_y', 'hex_size', 'pois',
)


def clean_map_name(raw, fallback='Map'):
    """Trim + cap a map name, falling back when the Master left it blank."""
    name = (raw or '').strip()[:MAP_NAME_MAX]
    return name or fallback


def _normalize_map(m):
    """Bring one map dict up to the current shape, in place. Idempotent.

    Ensures id + name, fills every confirmed-state key from the blank template,
    re-cleans POIs, and seeds the `pending` draft (equal to confirmed on first
    run) plus `confirm_seq`. Mirrors the per-node defaulting the single map used
    to get inline in db._normalize, now factored here so each map in the list
    is normalized the same way.
    """
    if not isinstance(m, dict):
        m = {}
    m['id'] = str(m.get('id') or '').strip() or uuid.uuid4().hex
    m['name'] = clean_map_name(m.get('name'), fallback='Map')

    defaults = _blank_map_state()
    for key, default in defaults.items():
        m.setdefault(key, default)
    # De-duplicate revealed hexes while preserving order: legacy data (and any
    # hand-edit) may carry repeats, and _coerce_map_fields already keeps the
    # confirmed list unique, so normalize matches that invariant here too.
    if isinstance(m.get('revealed_hexes'), (list, tuple)):
        seen = set()
        deduped = []
        for hx in m['revealed_hexes']:
            key = str(hx)
            if key not in seen:
                seen.add(key)
                deduped.append(key)
        m['revealed_hexes'] = deduped
    # Re-run stored POIs through the cleaner so older pins (saved before
    # icon/colour/scale existed) gain the full field set with sane defaults.
    m['pois'] = _clean_pois(m['pois'], m['pois'])
    # Focus sub-dict defaults, in case a hand-edited map carries a partial one.
    focus = m['focus'] if isinstance(m.get('focus'), dict) else {}
    focus.setdefault('seq', 0)
    focus.setdefault('x', 50.0)
    focus.setdefault('y', 50.0)
    focus.setdefault('scale', 1.0)
    m['focus'] = focus

    # Staging (draft) layer: seeded from the confirmed values so a fresh map
    # starts with draft == live. See docs/STORAGE.md.
    pending = m.setdefault('pending', {})
    pending.setdefault('revealed_hexes', list(m['revealed_hexes']))
    pending.setdefault('marker_x', m['marker_x'])
    pending.setdefault('marker_y', m['marker_y'])
    pending.setdefault('marker_visible', m['marker_visible'])
    pending.setdefault('marker_scale', m['marker_scale'])
    pending.setdefault('marker_icon', m['marker_icon'])
    pending.setdefault('marker_color', m['marker_color'])
    pending.setdefault('grid_cols', m['grid_cols'])
    pending.setdefault('grid_rows', m['grid_rows'])
    pending.setdefault('grid_type', m['grid_type'])
    pending.setdefault('fog_color', m['fog_color'])
    pending.setdefault('map_image', m['map_image'])
    pending.setdefault('offset_x', m['offset_x'])
    pending.setdefault('offset_y', m['offset_y'])
    pending.setdefault('hex_size', m['hex_size'])
    pending.setdefault('pois', [dict(poi) for poi in m['pois']])
    pending['pois'] = _clean_pois(pending['pois'], pending['pois'])
    m.setdefault('confirm_seq', 0)
    return m


# --------------------------------------------------------------------------
# Collection access
# --------------------------------------------------------------------------

def all_maps(db):
    """Every map, in stored order. The list players/masters choose from."""
    maps = db.get(MAPS_KEY)
    return maps if isinstance(maps, list) else []


def find_map(db, map_id):
    """Return the map dict with this id, or None."""
    if not map_id:
        return None
    return next((m for m in all_maps(db) if m.get('id') == map_id), None)


def get_map(db, map_id):
    """Return the map with this id, normalized, or None if it doesn't exist.

    Unlike the old get_map_state there is no implicit creation: with several
    maps, a missing id is a real "not found" (a deleted map, a stale URL), which
    the route turns into a 404 rather than silently spawning an empty map.
    """
    m = find_map(db, map_id)
    return _normalize_map(m) if m is not None else None


def create_map(db, name=''):
    """Append a new, empty map and return it. Name defaults to 'Map N'."""
    maps = db.setdefault(MAPS_KEY, [])
    if not isinstance(maps, list):
        maps = db[MAPS_KEY] = []
    fallback = f'Map {len(maps) + 1}'
    m = {'id': uuid.uuid4().hex, 'name': clean_map_name(name, fallback)}
    _normalize_map(m)
    maps.append(m)
    return m


def rename_map(db, map_id, name):
    """Rename a map in place. No-op (returns None) if the map is gone."""
    m = find_map(db, map_id)
    if m is None:
        return None
    m['name'] = clean_map_name(name, fallback=m.get('name') or 'Map')
    return m


def delete_map(db, map_id):
    """Remove a map from the collection. Returns the removed map, or None.

    The caller is responsible for deleting the map's background image file from
    disk (it has the storage.remove_map_image helper); this only touches the DB
    so the module stays free of filesystem work except where it already lives.
    """
    maps = all_maps(db)
    m = find_map(db, map_id)
    if m is None:
        return None
    db[MAPS_KEY] = [x for x in maps if x.get('id') != map_id]
    return m


# --------------------------------------------------------------------------
# Per-map scene operations. Each takes a map_id and is a no-op returning None
# when it doesn't resolve, so a stale id from a slow client can't raise.
# --------------------------------------------------------------------------

def update_map_state(db, map_id, data):
    """Write `data` into a map's DRAFT (pending) layer; return the map or None.

    This is what the Master's live edits hit: revealing a hex, dragging the
    marker, changing the grid or fog colour all land in `pending` and are NOT
    visible to players until confirm_map_state() promotes them. `data` may
    carry any subset of the known keys.

    NB: the map-upload route writes map_image straight to BOTH layers via
    set_map_image() -- see there for why an uploaded image is not staged.
    """
    m = get_map(db, map_id)
    if m is None:
        return None
    _coerce_map_fields(m.setdefault('pending', {}), data or {})
    return m


def set_map_image(db, map_id, filename):
    """Set (or clear) a map's background on BOTH the confirmed and draft layers.

    The background image is deliberately NOT staged: an uploaded map is a setup
    action, not a reveal, and a half-set-up map where the Master sees the new
    image but players still see the old one (until a confirm) would be more
    confusing than useful. Upload = immediately live for everyone.
    """
    m = get_map(db, map_id)
    if m is None:
        return None
    _coerce_map_fields(m, {'map_image': filename})
    _coerce_map_fields(m.setdefault('pending', {}), {'map_image': filename})
    return m


def confirm_map_state(db, map_id):
    """Promote a map's draft to confirmed: players now see what was staged.

    Copies every pending field onto the confirmed state and bumps confirm_seq
    so player pages can tell this is a fresh confirmation. This is the ONLY
    function that changes what players read (aside from set_map_image).
    Returns the map, or None if the id doesn't resolve.
    """
    m = get_map(db, map_id)
    if m is None:
        return None
    pending = m.get('pending', {})
    for key in _STAGED_KEYS:
        if key in pending:
            # Copy lists by value so the two layers don't alias. POIs need a
            # deep copy: each is a dict, and a shallow list() would still let a
            # later draft edit mutate the confirmed pin in place.
            if key == 'revealed_hexes':
                m[key] = list(pending[key])
            elif key == 'pois':
                m[key] = [dict(poi) for poi in pending[key]]
            else:
                m[key] = pending[key]
    m['confirm_seq'] = m.get('confirm_seq', 0) + 1
    return m


def discard_map_state(db, map_id):
    """Throw a map's draft away: reset pending back to its confirmed state.

    Used by the Master's 'Discard changes' button so a session of experimental
    reveals can be abandoned wholesale without touching what players see.
    Returns the map, or None if the id doesn't resolve.
    """
    m = get_map(db, map_id)
    if m is None:
        return None
    m['pending'] = {
        'revealed_hexes': list(m['revealed_hexes']),
        'marker_x': m['marker_x'],
        'marker_y': m['marker_y'],
        'marker_visible': m['marker_visible'],
        'marker_scale': m['marker_scale'],
        'marker_icon': m['marker_icon'],
        'marker_color': m['marker_color'],
        'grid_cols': m['grid_cols'],
        'grid_rows': m['grid_rows'],
        'grid_type': m['grid_type'],
        'fog_color': m['fog_color'],
        'map_image': m['map_image'],
        'offset_x': m['offset_x'],
        'offset_y': m['offset_y'],
        'hex_size': m['hex_size'],
        'pois': [dict(poi) for poi in m['pois']],
    }
    return m


def set_map_focus(db, map_id, x, y, scale):
    """Record a camera-focus broadcast on a map; return its focus dict or None.

    Not staged: a focus is a live "look here, now" directive, so it takes
    effect immediately rather than waiting for a confirm -- the same design as
    a POP. Bumping seq is what notifies players: they poll for it and animate
    to the new centre/zoom on any value above the last one they acted on, so a
    Master re-focusing the same spot still nudges a table that drifted away.

    x/y are the focus point as PERCENT of the image (clamped 0..100); scale is
    the zoom level, clamped to a sane range so a bad client value can't ask the
    player view for an absurd magnification.
    """
    m = get_map(db, map_id)
    if m is None:
        return None
    focus = m.setdefault('focus', {'seq': 0})
    try:
        fx = max(0.0, min(100.0, float(x)))
    except (TypeError, ValueError):
        fx = 50.0
    try:
        fy = max(0.0, min(100.0, float(y)))
    except (TypeError, ValueError):
        fy = 50.0
    try:
        fs = max(0.1, min(8.0, float(scale)))
    except (TypeError, ValueError):
        fs = 1.0
    m['focus'] = {
        'seq': focus.get('seq', 0) + 1,
        'x': fx, 'y': fy, 'scale': fs,
    }
    return m['focus']
