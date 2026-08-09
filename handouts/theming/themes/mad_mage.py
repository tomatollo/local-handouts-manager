"""Waterdeep: Dungeon of the Mad Mage.

Undermountain: torch-lit depths, mad-wizard green, and stone. Uncial Antiqua --
a rounded manuscript uncial -- reads like a mad wizard's grimoire, setting
Halaster's megadungeon apart from the city above. It sits large and wide, so it
needs less of a scale bump than most.
"""

from ..base import Theme

THEME = Theme(
    id='mad-mage',
    name='Waterdeep: Dungeon of the Mad Mage',
    blurb='Undermountain: torch-lit depths, mad-wizard green, and stone.',
    fonts=('Uncial Antiqua', 'Lora'),
    scale=1.35,
    vars={
        '--bg': '#0c0e0d',          # black Undermountain rock
        '--bg-panel': '#161a17',    # wet dungeon stone
        '--ink': '#e4e6df',
        '--ink-dim': '#8b938a',
        '--accent': '#8fbf3f',      # Halaster's mad arcane green
        '--accent-2': '#c06a2e',    # torch ember
        '--border': '#060706',
        '--shadow': '#000000',
        '--good': '#6a9c4f',
    },
    home_label='Ascend to the City (Home)',
    errors={
        400: ('\U0001F5FA\uFE0F', 'Lost on the Level',
              'Undermountain twisted your map. Your request wandered into the '
              'wrong corridor and never returned.'),
        401: ('\U0001F6AA', 'Warded Door',
              'A sigil-locked door blocks the way. You lack the phrase Halaster '
              'set upon it.'),
        403: ('\U0001F9D9', "Halaster's Whim",
              'The Mad Mage has decided you may not pass. His dungeon rearranges '
              'itself to keep you out.'),
        404: ('\U0001F573\uFE0F', 'Empty Level',
              'This level of Undermountain is bare stone. Nothing you sought is '
              'here -- or it moved when you blinked.'),
        429: ('\U0001F300', 'Teleport Trap',
              'You keep tripping the same teleport glyph. Pause before the '
              'dungeon flings you somewhere worse.'),
        500: ('\U0001F52E', 'Arcane Meltdown',
              "Halaster's experiments overloaded the weave. The dungeon is "
              'reshaping itself while it recovers.'),
    },
)
