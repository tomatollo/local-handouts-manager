"""How themes are grouped into labelled families in the picker.

THEME_GROUPS states, in one spot, which family each theme belongs to and the
order they render. The first group holds the official D&D campaign presets;
"Other Universes" collects everything that isn't D&D. Membership is by explicit
id list, and any theme NOT named in a group falls through to the LAST group
automatically (see registry.theme_groups) -- so a future non-D&D preset lands
in "Other Universes" without editing this file.

Dungeon Torch lives under "Other Universes" (it is the generic pixel default,
not D&D-specific). It is still DEFAULT_THEME, and theme_groups() floats the
default to the front of whichever group holds it, so it shows first there.
"""

THEME_GROUPS = (
    ('Dungeons & Dragons', (
        'phandelver',
        'shattered-obelisk',
        'curse-of-strahd',
        'tomb-of-annihilation',
        'dragon-heist',
        'mad-mage',
        'tiamat',
        'out-of-the-abyss',
        'icewind-dale',
        'witchlight',
        'candlekeep',
        'tashas-cauldron',
        'xanathars-guide',
        'vecna-eve-of-ruin',
        'theros',
    )),
    ('Other Universes', (
        'dungeon-torch',
        'vintage-arcade',
        'military-terminal',
        'analog-archive',
        'holo-hud',
    )),
)
