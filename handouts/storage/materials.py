"""Material presets for the object3d "built" sheet.

When a handout is a double-sided sheet (front image + optional back texture)
rather than a .glb model, the 3D inspector builds the paper procedurally. This
module describes HOW that paper looks and how thick it is, so the Master can
pick a feel ("parchment", "metal plate", "stone tablet") from the create form
and, if they want, fine-tune the underlying PBR values.

The shape stored on a handout is `sheet_material`, a small dict:

    {
        "preset":    "parchment",   # one of SHEET_MATERIAL_PRESETS, or "custom"
        "roughness": 0.85,          # 0..1  PBR roughness (1 = fully matte)
        "metalness": 0.0,           # 0..1  PBR metalness (1 = metal)
        "thickness": 0.05,          # 0..~0.5  sheet depth in scene units
    }

Only the object3d SHEET path reads it; a .glb model brings its own materials and
ignores this entirely, and the carousel/book viewers never look at it. Keeping
it a self-contained dict (rather than four loose columns on the handout) means
the create form, the player payload, and the export/import round-trip all move
one value, and adding a future knob (an emissive glow, a normal-map strength)
touches only this file and the reader.

Nothing here imports a sibling storage module, so it sits at the same low layer
as paths/util and can be pulled in by db._normalize without an import cycle.
"""

# The named presets offered in the create form. Each carries the three PBR/
# geometry values the reader needs. Order here is the order shown in the UI.
# `roughness`/`metalness` mirror three.js MeshStandardMaterial; `thickness` is
# in the same scene units the reader frames the sheet in (its height is 2), so
# 0.05 is a sheet of paper, ~0.2 a slab. Values chosen to read well under the
# inspector's two-light rig (see inspector3d.js _initLights).
SHEET_MATERIAL_PRESETS = {
    'paper': {
        'label': 'Paper',
        'roughness': 0.95,
        'metalness': 0.0,
        'thickness': 0.02,
    },
    'parchment': {
        'label': 'Parchment',
        'roughness': 0.85,
        'metalness': 0.0,
        'thickness': 0.05,
    },
    'leather': {
        'label': 'Leather',
        'roughness': 0.7,
        'metalness': 0.0,
        'thickness': 0.08,
    },
    'wood': {
        'label': 'Wood',
        'roughness': 0.6,
        'metalness': 0.05,
        'thickness': 0.12,
    },
    'stone': {
        'label': 'Stone tablet',
        'roughness': 0.9,
        'metalness': 0.0,
        'thickness': 0.2,
    },
    'metal': {
        'label': 'Metal plate',
        'roughness': 0.35,
        'metalness': 0.9,
        'thickness': 0.1,
    },
}

# The default a fresh sheet handout gets, and what every legacy record is
# normalized to. Parchment is the "scroll" feel most handouts want and matches
# the old hardcoded 0.85 / 0.0 the reader used before this was configurable.
DEFAULT_SHEET_MATERIAL_PRESET = 'parchment'

# Bounds for the fine-tune sliders. roughness/metalness are the natural 0..1 of
# PBR; thickness is clamped so a sheet can't be a razor (invisible edge-on, the
# very bug this fixes) nor a thick brick that dwarfs its own art.
_ROUGHNESS_MIN, _ROUGHNESS_MAX = 0.0, 1.0
_METALNESS_MIN, _METALNESS_MAX = 0.0, 1.0
_THICKNESS_MIN, _THICKNESS_MAX = 0.005, 0.5


def _clamp(value, lo, hi, fallback):
    """Coerce `value` to a float in [lo, hi]; return `fallback` on junk."""
    try:
        v = float(value)
    except (TypeError, ValueError):
        return fallback
    if v != v:            # NaN
        return fallback
    return max(lo, min(hi, v))


def default_sheet_material():
    """A fresh copy of the default material dict.

    Returns a NEW dict each call so callers can store it on a record without
    aliasing a shared object (a later edit of one handout must not mutate the
    default for the next).
    """
    return _material_from_preset(DEFAULT_SHEET_MATERIAL_PRESET)


def _material_from_preset(preset_key):
    """Build a full material dict from a named preset's values."""
    preset = SHEET_MATERIAL_PRESETS.get(preset_key,
                                        SHEET_MATERIAL_PRESETS[DEFAULT_SHEET_MATERIAL_PRESET])
    return {
        'preset': preset_key if preset_key in SHEET_MATERIAL_PRESETS
        else DEFAULT_SHEET_MATERIAL_PRESET,
        'roughness': preset['roughness'],
        'metalness': preset['metalness'],
        'thickness': preset['thickness'],
    }


def clean_sheet_material(raw):
    """Normalize whatever is stored/submitted into a valid material dict.

    Accepts:
      * None / junk            -> the default material.
      * a dict with a known    -> that preset's values, UNLESS the dict also
        `preset`                  carries explicit roughness/metalness/thickness
                                  (the advanced sliders), in which case those
                                  win and the preset is recorded as 'custom'
                                  only when they actually differ.
      * a dict with 'custom'   -> the three sliders, clamped to their ranges,
        or no known preset        with any missing value filled from the
                                  default.

    The rule "explicit slider values win, preset is a starting point" is what
    lets the form send both a preset choice AND advanced overrides in one go:
    picking "Metal" then nudging roughness yields a custom material seeded from
    metal, exactly as the UI implies.
    """
    if not isinstance(raw, dict):
        return default_sheet_material()

    preset_key = (raw.get('preset') or '').strip().lower()
    base = _material_from_preset(preset_key) if preset_key in SHEET_MATERIAL_PRESETS \
        else default_sheet_material()

    # Did the caller send explicit numeric overrides? Absent keys keep the
    # preset's value; present ones are clamped and take precedence.
    roughness = _clamp(raw.get('roughness', base['roughness']),
                       _ROUGHNESS_MIN, _ROUGHNESS_MAX, base['roughness'])
    metalness = _clamp(raw.get('metalness', base['metalness']),
                       _METALNESS_MIN, _METALNESS_MAX, base['metalness'])
    thickness = _clamp(raw.get('thickness', base['thickness']),
                       _THICKNESS_MIN, _THICKNESS_MAX, base['thickness'])

    # Decide the recorded preset label. If the caller named a known preset and
    # the numbers still match it, keep that name; if the numbers were nudged
    # away from every preset, call it 'custom' so the UI shows the sliders as
    # the source of truth on the next edit.
    resolved_preset = preset_key if preset_key in SHEET_MATERIAL_PRESETS else base['preset']
    p = SHEET_MATERIAL_PRESETS.get(resolved_preset)
    if p is None or roughness != p['roughness'] or metalness != p['metalness'] \
            or thickness != p['thickness']:
        # Only downgrade to 'custom' when it genuinely differs from the named
        # preset; an exact match keeps the friendly name.
        if p is not None and roughness == p['roughness'] \
                and metalness == p['metalness'] and thickness == p['thickness']:
            pass
        else:
            resolved_preset = 'custom'

    return {
        'preset': resolved_preset,
        'roughness': roughness,
        'metalness': metalness,
        'thickness': thickness,
    }


def sheet_material_from_form(preset, roughness, metalness, thickness):
    """Assemble a material dict from raw form fields, then clean it.

    The create/edit forms send four fields: the chosen preset key and the three
    advanced-slider values (which the form pre-fills from the preset via JS, so
    they are always present even when the Master never opened "Advanced"). This
    packs them into the dict shape clean_sheet_material expects and returns the
    normalized result, so a hand-crafted or stale POST can't store out-of-range
    numbers.
    """
    return clean_sheet_material({
        'preset': preset,
        'roughness': roughness,
        'metalness': metalness,
        'thickness': thickness,
    })
