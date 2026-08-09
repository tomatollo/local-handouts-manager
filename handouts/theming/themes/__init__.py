"""Theme registry: collects every theme module into ordered lookups.

Each theme lives in its own module here, exposing a module-level `THEME`
(a themes.base.Theme). This package gathers them into:

  ALL_THEMES : tuple[Theme]      -- in declaration order (order matters: the
               picker and theme_list rely on it, floating only the default).
  THEMES     : dict[str, Theme]  -- id -> Theme, same order.

Adding a preset is: drop a `<name>.py` here with a `THEME = Theme(...)`, then
add its id to _ORDER below (and to a group in theming/groups.py). Nothing else
needs editing -- the public API in theming/__init__.py reads these two names.

Why an explicit _ORDER list rather than auto-importing the folder: the on-page
order of themes is a curated thing (default first, campaigns in a chosen
sequence), and an explicit list states that order in one readable place instead
of depending on filesystem iteration order. A theme whose module exists but is
missing from _ORDER simply isn't shown -- a handy way to park a work-in-progress
preset without deleting it.
"""

from importlib import import_module

# Declaration order == on-page order. (module_name, ) resolved to THEME below.
# Keep this the single source of truth for which themes exist and their order.
_ORDER = (
    'dungeon_torch',
    'phandelver',
    'tiamat',
    'out_of_the_abyss',
    'tomb_of_annihilation',
    'curse_of_strahd',
    'icewind_dale',
    'vecna_eve_of_ruin',
    'tashas_cauldron',
    'xanathars_guide',
    'shattered_obelisk',
    'dragon_heist',
    'mad_mage',
    'witchlight',
    'candlekeep',
    'theros',
    'vintage_arcade',
    'military_terminal',
    'analog_archive',
    'holo_hud',
)

ALL_THEMES = tuple(
    import_module(f'.{mod}', __name__).THEME for mod in _ORDER
)

# id -> Theme, preserving _ORDER. Python dicts keep insertion order, so this
# doubles as the ordered table the rest of the package iterates.
THEMES = {theme.id: theme for theme in ALL_THEMES}
