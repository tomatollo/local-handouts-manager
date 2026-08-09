"""Interactive map (global, master-controlled).

One shared map per table: the Master reveals hexes and moves a marker, and
every player screen polls this state. Stored at the DB root (see MAP_KEY),
not under `settings`, because it is live scene state rather than a display
preference.

Named map_state (not map) so it never shadows the builtin. The confirmed state
is what players read; the Master edits a `pending` draft and explicitly confirms
it. See docs/STORAGE.md for the staging model.
"""

import re
import uuid

from .paths import MAP_KEY


def get_map_state(db):
    """Return the current map state dict.

    Never None: _normalize() guarantees the node and its keys exist, but we
    still fall back defensively so a caller that hand-built a db without
    normalizing gets a sane shape rather than a KeyError.
    """
    return db.setdefault(MAP_KEY, {
        'revealed_hexes': [],
        'marker_x': 0,
        'marker_y': 0,
        'marker_visible': False,
        'marker_scale': 1.0,
        'marker_icon': '',
        'marker_color': '#c0533b',
        'grid_cols': 20,
        'grid_rows': 15,
        'fog_color': '#0d0b0a',
        'map_image': None,
        'offset_x': 0.0,
        'offset_y': 0.0,
        'hex_size': 5.0,
        'pois': [],
        'focus': {'seq': 0, 'x': 50.0, 'y': 50.0, 'scale': 1.0},
    })


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
    `target` is either the confirmed state or its `pending` sub-dict.
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


def update_map_state(db, data):
    """Write `data` into the DRAFT (pending) layer and return the full state.

    This is what the Master's live edits hit: revealing a hex, dragging the
    marker, changing the grid or fog colour all land in `pending` and are NOT
    visible to players until confirm_map_state() promotes them. `data` may
    carry any subset of the known keys.

    NB: the map-upload route writes map_image straight to BOTH layers via
    set_map_image() -- see there for why an uploaded image is not staged.
    """
    state = get_map_state(db)
    pending = state.setdefault('pending', {})
    _coerce_map_fields(pending, data or {})
    return state


def set_map_image(db, filename):
    """Set (or clear) the map background on BOTH the confirmed and draft layers.

    The background image is deliberately NOT staged: an uploaded map is a setup
    action, not a reveal, and a half-set-up map where the Master sees the new
    image but players still see the old one (until a confirm) would be more
    confusing than useful. Upload = immediately live for everyone.
    """
    state = get_map_state(db)
    _coerce_map_fields(state, {'map_image': filename})
    _coerce_map_fields(state.setdefault('pending', {}), {'map_image': filename})
    return state


def confirm_map_state(db):
    """Promote the draft to confirmed: players now see what the Master staged.

    Copies every pending field onto the confirmed state and bumps confirm_seq
    so player pages can tell this is a fresh confirmation. This is the ONLY
    function that changes what players read (aside from set_map_image).
    """
    state = get_map_state(db)
    pending = state.get('pending', {})
    for key in ('revealed_hexes', 'marker_x', 'marker_y', 'marker_visible',
                'marker_scale', 'marker_icon', 'marker_color',
                'grid_cols', 'grid_rows', 'fog_color',
                'map_image', 'offset_x', 'offset_y', 'hex_size', 'pois'):
        if key in pending:
            # Copy lists by value so the two layers don't alias. POIs need a
            # deep copy: each is a dict, and a shallow list() would still let
            # a later draft edit mutate the confirmed pin in place.
            if key == 'revealed_hexes':
                state[key] = list(pending[key])
            elif key == 'pois':
                state[key] = [dict(poi) for poi in pending[key]]
            else:
                state[key] = pending[key]
    state['confirm_seq'] = state.get('confirm_seq', 0) + 1
    return state


def discard_map_state(db):
    """Throw the draft away: reset pending back to the confirmed state.

    Used by the Master's 'Discard changes' button so a session of experimental
    reveals can be abandoned wholesale without touching what players see.
    """
    state = get_map_state(db)
    state['pending'] = {
        'revealed_hexes': list(state['revealed_hexes']),
        'marker_x': state['marker_x'],
        'marker_y': state['marker_y'],
        'marker_visible': state['marker_visible'],
        'marker_scale': state['marker_scale'],
        'marker_icon': state['marker_icon'],
        'marker_color': state['marker_color'],
        'grid_cols': state['grid_cols'],
        'grid_rows': state['grid_rows'],
        'fog_color': state['fog_color'],
        'map_image': state['map_image'],
        'offset_x': state['offset_x'],
        'offset_y': state['offset_y'],
        'hex_size': state['hex_size'],
        'pois': [dict(poi) for poi in state['pois']],
    }
    return state


def set_map_focus(db, x, y, scale):
    """Record a camera-focus broadcast and return the new focus dict.

    Not staged: a focus is a live "look here, now" directive, so it takes
    effect immediately rather than waiting for a confirm -- the same design as
    a POP. Bumping seq is what notifies players: they poll for it and animate
    to the new centre/zoom on any value above the last one they acted on, so a
    Master re-focusing the same spot still nudges a table that drifted away.

    x/y are the focus point as PERCENT of the image (clamped 0..100); scale is
    the zoom level, clamped to a sane range so a bad client value can't ask the
    player view for an absurd magnification.
    """
    state = get_map_state(db)
    focus = state.setdefault('focus', {'seq': 0})
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
    state['focus'] = {
        'seq': focus.get('seq', 0) + 1,
        'x': fx, 'y': fy, 'scale': fs,
    }
    return state['focus']
